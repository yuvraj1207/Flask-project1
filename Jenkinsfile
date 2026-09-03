pipeline {
    agent any

    triggers{
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                bat '''
                    "C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" --version
                    "C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pip install -r requirements.txt
                    "C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t yuvrajhinde/flask-container:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker push yuvrajhinde/flask-container:latest
                    '''
                }
            }
        }
    }

    post{
        success{
            emailext(
                subject: "SUCCESS ${env.JOB_NAME}  #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Successful</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "yuvrajhinde21@gmail.com"
            )
        }

        failure{
            emailext(
                subject: "FAILED ${env.JOB_NAME}  #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Failed</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "yuvrajhinde21@gmail.com"
            )
        }
    }

}
