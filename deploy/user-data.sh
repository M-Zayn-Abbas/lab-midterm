#!/bin/bash
# EC2 Launch Template "User data" - runs once as root when an Auto Scaling instance first boots.
# Installs Docker, clones the repo and starts the app with Docker Compose.
set -euxo pipefail
exec > /var/log/user-data.log 2>&1   # debug with: sudo cat /var/log/user-data.log

apt-get update -y
apt-get install -y docker.io docker-compose-v2 git
systemctl enable --now docker
usermod -aG docker ubuntu

git clone https://github.com/M-Zayn-Abbas/lab-midterm.git /opt/task-tracker
cd /opt/task-tracker

# Instance ID from the metadata service (IMDSv2) - shown on the page to prove load balancing
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)

cat > .env <<EOF
POSTGRES_DB=tasks
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=change-me
SERVER_NAME=$INSTANCE_ID
EOF
chmod 600 .env

docker compose up -d --build
