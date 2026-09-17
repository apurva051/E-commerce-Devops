pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipDefaultCheckout(true)
    }

    environment {
        DOCKER_IMAGE = 'apurva051/ecommerce-product-service'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Initialize') {
            steps {
                script {
                    def shortCommit = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${shortCommit}"

                    echo "Docker image: ${env.DOCKER_IMAGE}:${env.IMAGE_TAG}"
                }
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    set -e

                    echo "Checking required tools and files..."

                    git --version
                    docker --version

                    test -f product-service/Dockerfile

                    echo "Validation completed."
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."

                    docker build \
                      --tag ${DOCKER_IMAGE}:${IMAGE_TAG} \
                      ./product-service
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | \
                          docker login \
                          --username "$DOCKERHUB_USERNAME" \
                          --password-stdin

                        set -x

                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "CI pipeline completed successfully."
            echo "Published image: ${env.DOCKER_IMAGE}:${env.IMAGE_TAG}"
        }

        failure {
            echo "CI pipeline failed. Check the failed stage logs."
        }

        always {
            sh '''
                if [ -n "${IMAGE_TAG}" ]; then
                    docker image rm \
                      ${DOCKER_IMAGE}:${IMAGE_TAG} || true
                fi

                docker logout || true
            '''
        }
    }
}