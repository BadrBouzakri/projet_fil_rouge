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
                        # Nettoyer d'abord
                        rm -rf k8s-repo
                        rm -f ~/.ssh/id_rsa ~/.ssh/known_hosts
                        
                        # Configure Git SSH avec les bonnes permissions
                        mkdir -p ~/.ssh
                        cat "$GIT_SSH_KEY" > ~/.ssh/id_rsa
                        chmod 600 ~/.ssh/id_rsa
                        ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
                        chmod 644 ~/.ssh/known_hosts
                        
                        # Test SSH connection avant de continuer
                        ssh -T -o StrictHostKeyChecking=no git@github.com || true
                        
                        # Clone the repository (avec gestion d'erreur)
                        git clone $GITHUB_REPO_URL k8s-repo || {
                            # Si le clone échoue, vérifier que le dépôt existe et est accessible
                            echo "Erreur lors du clonage. Vérification des branches disponibles..."
                            git ls-remote --heads $GITHUB_REPO_URL || true
                            # Créer un répertoire vide comme fallback
                            mkdir -p k8s-repo
                            cd k8s-repo
                            git init
                            git remote add origin $GITHUB_REPO_URL
                        }
                        
                        # Vérifier la branche par défaut (main ou master)
                        cd k8s-repo
                        DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5 || echo "main")
                        echo "La branche par défaut est: $DEFAULT_BRANCH"
                        
                        # Fetch pour obtenir la dernière version
                        git fetch origin || true
                        
                        # Checkout de la branche principale si elle existe
                        git checkout $DEFAULT_BRANCH || git checkout -b $DEFAULT_BRANCH
                        
                        # Copier les manifests Kubernetes mis à jour
                        cp -f ../k8s/*.yaml ./
                        
                        # Configurer git
                        git config --global user.email "bouzakri.badr@gmail.com"
                        git config --global user.name "BadrBouzakri"
                        
                        # Commit et push des changements
                        git add .
                        git commit -m "Update kubernetes manifests for version $DOCKER_TAG" || echo "Aucun changement à commit"
                        
                        # Pousser vers la branche principale avec détail des erreurs
                        git push origin $DEFAULT_BRANCH || {
                            echo "Erreur lors du push. Détails:"
                            git remote -v
                            git branch
                            git status
                        }
                        
                        # Nettoyage sécuritaire
                        cd ..
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