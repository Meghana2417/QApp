pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('docker-hub')
    }

    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/Meghana2417/APIGateway.git'
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build --no-cache -t meghana1724/api:latest ."
            }
        }

        stage('Docker Login') {
            steps {
                sh 'echo "$DOCKER_CREDS_PSW" | docker login -u "$DOCKER_CREDS_USR" --password-stdin'
            }
        }

        stage('Docker Push') {
            steps {
                sh "docker push meghana1724/api:latest"
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker stop api || true
                docker rm api || true

                docker pull meghana1724/api:latest

                docker run -d --name api -p 8000:8000 meghana1724/api:latest
                '''
            }
        }
    }
}
