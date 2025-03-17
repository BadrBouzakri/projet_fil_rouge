pipeline {
    environment { 
        DOCKER_ID = "bouzakri" 
        DOCKER_IMAGE = "foot_app"
        DOCKER_TAG = "v.${BUILD_ID}.0"
        GITHUB_REPO_URL = "git@github.com:bouzakri/k8s-projet-prod.git"
    }
    agent any 

    stages {
        stage('Docker Build') { 
            steps {
                script {
                    sh '''
                    docker rm -f jenkins || true
                    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                    sleep 6
                    '''
                }
            }
        }

        stage('Docker Run') { 
            steps {
                script {
                    sh '''
                    docker run -d -p 5000:5000 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    sleep 10
                    '''
                }
            }
        }

        stage('Test Acceptance') { 
            steps {
                script {
                    sh '''
                    echo "Attente du démarrage de l'application sur localhost:5000..."
                    until curl -s localhost:5000 > /dev/null; do
                      echo "L'application n'est pas encore prête. Nouvelle tentative dans 5 secondes..."
                      sleep 5
                    done
                    curl localhost:5000
                    '''
                }
            }
        }

        stage('Docker Push') { 
            environment {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                script {
                    sh '''
                    docker login -u $DOCKER_ID -p $DOCKER_PASS
                    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        stage('Update Kubernetes YAML Files') {
            steps {
                script {
                    sh '''
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/deployment.yaml
                    '''
                }
            }
        }

        stage('Deploiement en dev') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                    kubectl apply -f k8s/deployment.yaml -n dev
                    kubectl apply -f k8s/service.yaml -n dev
                    kubectl apply -f k8s/pv.yaml -n dev
                    kubectl apply -f k8s/pvc.yaml -n dev
                    kubectl apply -f k8s/hpa.yaml -n dev
                    '''
                }
            }
        }

        stage('Deploiement en staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                    kubectl apply -f k8s/deployment.yaml -n staging
                    kubectl apply -f k8s/service.yaml -n staging
                    kubectl apply -f k8s/pv.yaml -n staging
                    kubectl apply -f k8s/pvc.yaml -n staging
                    kubectl apply -f k8s/hpa.yaml -n staging
                    '''
                }
            }
        }

        stage('Push Kubernetes Manifests to Git') {
            environment {
                GIT_SSH_KEY = credentials('github-ssh-key')
            }
            steps {
                script {
                    sh '''
                        # Configure Git SSH
                        mkdir -p ~/.ssh
                        echo "$GIT_SSH_KEY" > ~/.ssh/id_rsa
                        chmod 600 ~/.ssh/id_rsa
                        ssh-keyscan github.com >> ~/.ssh/known_hosts

                        # Clone the repository
                        git clone $GITHUB_REPO_URL k8s-repo || true
                        
                        # Copy the updated manifests
                        cp k8s/*.yaml k8s-repo/
                        
                        # Commit and push
                        cd k8s-repo
                        git config --global user.email "jenkins@example.com"
                        git config --global user.name "Jenkins"
                        git add .
                        git commit -m "Update kubernetes manifests for version $DOCKER_TAG" || true
                        git push origin main
                        
                        # Cleanup
                        rm -f ~/.ssh/id_rsa
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f jenkins || true'
        }
    }
}