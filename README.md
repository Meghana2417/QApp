Server Setup

    sudo apt update && sudo apt upgrade -y
    sudo apt install docker.io -y
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo apt install nginx -y
    sudo apt install postgresql postgresql-contrib -y

2. PostgreSQL Setup

        sudo -u postgres psql
        CREATE DATABASE qapp;
        CREATE USER qappuser WITH PASSWORD 'yourpassword';
        GRANT ALL PRIVILEGES ON DATABASE qapp TO qappuser;
        \q

3. Docker Commands

Build Docker image:

    docker build -t qapp:latest .


Run container:

    docker run -d --name qapp -p 8000:8000 --env-file .env qapp:latest


Check logs:

docker logs qapp


Stop & remove container:

    docker stop qapp
    docker rm qapp

4. Deployment Script

Run the deployment script:

    chmod +x docker-run.sh
    ./docker-run.sh

5. Nginx Commands

Test config:

    sudo nginx -t


Restart Nginx:

    sudo systemctl restart nginx

6. GitHub Actions Secrets Needed

        SSH_PRIVATE_KEY
        SERVER_IP
        SERVER_USER

7. After Deployment — Test App

        curl http://127.0.0.1:8000/
        curl http://YOUR_PUBLIC_IP/
        curl http://YOUR_PUBLIC_IP/api/
