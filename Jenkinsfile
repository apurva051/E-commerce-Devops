pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipDefaultCheckout(true)
    }

    environment {
        DOKERHUB_NAMESPACE = 'apurva051'

        PRODUCT_IMAGE  = 'apurva051/ecommerce-product-service'
        ORDER_IMAGE    = 'apurva051/ecommerce-order-service'
        USER_IMAGE     = 'apurva051/ecommerce-user-service'
        GATEWAY_IMAGE  = 'apurva051/ecommerce-api-gateway'
        FRONTEND_IMAGE = 'apurva051/ecommerce-frontend'

        GITOPS_REPO = 'https://github.com/apurva051/ecommerce-gitops.git'
        GITOPS_BRANCH = 'main'
        GITOPS_ROOT = 'environment'
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

                     echo "Image tag for this build: ${env.IMAGE_TAG}"
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

                    echo "Checking Dockerfiles..."
                    test -f product-service/Dockerfile
                    test -f order-service/Dockerfile
                    test -f user-service/Dockerfile
                    test -f api-gateway/Dockerfile
                    test -f frontend/Dockerfile

                    git diff --check

                    echo "Validation completed."
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "Building Docker image..."

                    docker build \
                      --tag ${DOCKER_IMAGE}:${IMAGE_TAG} \
                      ./product-service

                    docker build \
                      -t ${ORDER_IMAGE}:${IMAGE_TAG} \
                      ./order-service

                    docker build \
                      -t ${USER_IMAGE}:${IMAGE_TAG} \
                      ./user-service

                    docker build \
                      -t ${GATEWAY_IMAGE}:${IMAGE_TAG} \
                      ./api-gateway

                    docker build \
                      -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                      ./frontend
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

                        docker push ${PRODUCT_IMAGE}:${IMAGE_TAG}
                        docker push ${ORDER_IMAGE}:${IMAGE_TAG}
                        docker push ${USER_IMAGE}:${IMAGE_TAG}
                        docker push ${GATEWAY_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}

                    
                    '''
                }
            }
        }
        stage ('Update GitOps Repository'){
            steps{
                withCredentials([
                    usernamePassword(
                        credentialsId: 'gitops-creds',
                        usernameVariable: 'GITHUB_USERNAME',
                        passwordVariable: 'GITHUB_TOKEN'
                    )
                ]){
                    sh '''
                        set -e
                        set +x

                        rm -rf gitops-work

                        git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/apurva051/ecommerce-gitops.git" gitops-work

                        cd gitops-work
                        git config user.name "jenkins-ci"
                        git config user.email "jenkins-ci@users.noreply.github.com"

                        sed -i -E \
                          "s#^([[:space:]]*image:[[:space:]]*${PRODUCT_IMAGE}:).*#\\1${IMAGE_TAG}#" \
                          "${GITOPS_ROOT}/apps/product-service.yaml"

                        sed -i -E \
                          "s#^([[:space:]]*image:[[:space:]]*${ORDER_IMAGE}:).*#\\1${IMAGE_TAG}#" \
                          "${GITOPS_ROOT}/apps/order-service.yaml"

                        sed -i -E \
                          "s#^([[:space:]]*image:[[:space:]]*${USER_IMAGE}:).*#\\1${IMAGE_TAG}#" \
                          "${GITOPS_ROOT}/apps/user-service.yaml"

                        sed -i -E \
                          "s#^([[:space:]]*image:[[:space:]]*${GATEWAY_IMAGE}:).*#\\1${IMAGE_TAG}#" \
                          "${GITOPS_ROOT}/gateway/api-gateway.yaml"

                        sed -i -E \
                          "s#^([[:space:]]*image:[[:space:]]*${FRONTEND_IMAGE}:).*#\\1${IMAGE_TAG}#" \
                          "${GITOPS_ROOT}/frontend/frontend.yaml"


                        echo "Updated GitOps image references:"
                        grep -R -n "image:" \
                          "${GITOPS_ROOT}/apps" \
                          "${GITOPS_ROOT}/gateway" \
                          "${GITOPS_ROOT}/frontend"

                        git add "${GITOPS_ROOT}"

                        if git diff --cached --quiet; then
                            echo "GitOps manifests are already up to date."
                        else
                            git commit \
                              -m "Deploy ecommerce services ${IMAGE_TAG}"

                            git push \
                              "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/apurva051/ecommerce-gitops.git" \
                              HEAD:${GITOPS_BRANCH}
                        fi

                        cd ..
                        rm -rf gitops-work

                        set -x
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
                      ${PRODUCT_IMAGE}:${IMAGE_TAG} \
                      ${ORDER_IMAGE}:${IMAGE_TAG} \
                      ${USER_IMAGE}:${IMAGE_TAG} \
                      ${GATEWAY_IMAGE}:${IMAGE_TAG} \
                      ${FRONTEND_IMAGE}:${IMAGE_TAG} || true
                fi

                docker logout || true
                rm -rf gitops-work
            '''
        }
    }
}