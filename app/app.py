"""Student Task Tracker - Flask backend for the DevOps lab mid."""
import os
import socket
import time
from contextlib import contextmanager

import psycopg2
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Shown on every page so you can see which EC2 instance / container answered (Load Balancer demo).
SERVER_NAME = os.environ.get("SERVER_NAME") or socket.gethostname()


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
    )


@contextmanager
def db_cursor():
    """Open a connection, commit on success / rollback on error, and always close it."""
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            yield cur
    finally:
        conn.close()


def init_db(retries=15, delay=2):
    """Create the table, retrying because the DB container may still be starting."""
    for attempt in range(1, retries + 1):
        try:
            with db_cursor() as cur:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS tasks (
                           id SERIAL PRIMARY KEY,
                           title TEXT NOT NULL,
                           priority TEXT NOT NULL DEFAULT 'Medium',
                           done BOOLEAN NOT NULL DEFAULT FALSE,
                           created_at TIMESTAMP NOT NULL DEFAULT NOW()
                       )"""
                )
            print(f"Database ready (attempt {attempt})", flush=True)
            return
        except psycopg2.OperationalError as e:
            print(f"Waiting for database ({attempt}/{retries}): {e}", flush=True)
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database")


@app.route("/")
def index():
    with db_cursor() as cur:
        cur.execute("SELECT id, title, priority, done FROM tasks ORDER BY done, id DESC")
        tasks = [dict(zip(("id", "title", "priority", "done"), row)) for row in cur.fetchall()]
    return render_template("index.html", tasks=tasks, server=SERVER_NAME)


@app.route("/tasks", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")
    if title and priority in ("Low", "Medium", "High"):
        with db_cursor() as cur:
            cur.execute("INSERT INTO tasks (title, priority) VALUES (%s, %s)", (title, priority))
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    with db_cursor() as cur:
        cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s", (task_id,))
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    with db_cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    return redirect(url_for("index"))


@app.route("/health")
def health():
    """Used by the Docker HEALTHCHECK and the AWS Target Group health check."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
        return {"status": "ok", "server": SERVER_NAME}, 200
    except psycopg2.Error:
        return {"status": "db-unavailable", "server": SERVER_NAME}, 503


init_db()
