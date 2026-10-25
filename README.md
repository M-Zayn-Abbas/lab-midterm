# Student Task Tracker - DevOps Lab Mid

A small three-tier web app (HTML frontend, Flask backend, PostgreSQL database) deployed with
Docker and Docker Compose on AWS EC2 instances behind an Application Load Balancer and an
Auto Scaling Group, and tested with Selenium WebDriver.

**Live application (AWS Application Load Balancer):**
http://task-tracker-alb-1135327115.ap-south-1.elb.amazonaws.com/

**Lab report (screenshots for every task):** [SP23-BSE-136 Report.pdf](SP23-BSE-136%20Report.pdf)

```
.
├── app/
│   ├── app.py              # Flask backend (routes, DB access, /health)
│   ├── templates/index.html
│   └── static/style.css
├── Dockerfile              # Custom image for the web app
├── .dockerignore
├── compose.yaml            # web + db containers, named volume, private network
├── .env.example            # Copy to .env (never commit .env)
├── requirements.txt
├── deploy/user-data.sh     # EC2 Launch Template user data for the Auto Scaling Group
├── tests/
│   ├── test_selenium.py    # Selenium end-to-end test
│   └── requirements.txt
└── SP23-BSE-136 Report.pdf # Lab report
```

## Run with Docker Compose

```bash
cp .env.example .env        # set a password in .env
docker compose up -d --build
docker compose ps
```

Open `http://<server-ip>`. Health check: `http://<server-ip>/health`.

## Run the Selenium test

```bash
pip install -r tests/requirements.txt
python tests/test_selenium.py http://task-tracker-alb-1135327115.ap-south-1.elb.amazonaws.com
```
