pipeline {
    environment { 
        // Informations Docker
        DOCKER_ID = "bouzakri" 
        DOCKER_IMAGE = "foot_app"
        DOCKER_TAG = "v.${BUILD_ID}.0"
        
        // Informations GitHub
        GITHUB_REPO_OWNER = "BadrBouzakri"
        GITHUB_REPO_NAME = "k8s-projet-prod"
        GITHUB_BRANCH = "main"
    }
    
    agent any 
    
    options {
        // Nettoyer l'espace de travail avant de commencer
        skipDefaultCheckout(false)
        // Garder les derniers builds
        buildDiscarder(logRotator(numToKeepStr: '5'))
        // Timeout global du pipeline
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Préparation') {
            steps {
                // Nettoyage des conteneurs existants
                sh 'docker rm -f jenkins || true'
                
                // Affiche les informations du build
                echo "Construction de l'image: ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }

        stage('Construction') { 
            steps {
                script {
                    sh '''
                    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                    sleep 6
                    '''
                }
            }
        }

        stage('Déploiement local') { 
            steps {
                script {
                    sh '''
                    docker run -d -p 5000:5000 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    sleep 10
                    '''
                }
            }
        }

        stage('Tests') { 
            steps {
                script {
                    sh '''
                    echo "Attente du démarrage de l'application sur localhost:5000..."
                    timeout=60
                    elapsed=0
                    
                    until curl -s localhost:5000 > /dev/null; do
                      if [ $elapsed -ge $timeout ]; then
                        echo "Timeout atteint. L'application n'a pas démarré dans les $timeout secondes."
                        exit 1
                      fi
                      
                      echo "L'application n'est pas encore prête. Nouvelle tentative dans 5 secondes..."
                      sleep 5
                      elapsed=$((elapsed+5))
                    done
                    
                    echo "Application démarrée avec succès!"
                    curl -s localhost:5000
                    '''
                }
            }
        }

        stage('Publication de l\'image') { 
            environment {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                script {
                    sh '''
                    echo "Publication de l'image Docker vers Docker Hub..."
                    docker login -u $DOCKER_ID -p $DOCKER_PASS
                    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        stage('Mise à jour des manifestes K8s') {
            steps {
                script {
                    sh '''
                    echo "Mise à jour des fichiers de déploiement Kubernetes..."
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/deployment.yaml
                    '''
                }
            }
        }

        stage('Déploiement en DEV') {
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

        stage('Déploiement en STAGING') {
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

        stage('Sauvegarde des manifestes K8s') {
            environment {
                // Utiliser des identifiants de type username/password pour GitHub
                GIT_CREDENTIALS = credentials('github-credentials')
            }
            steps {
                script {
                    sh '''
                    # Nettoyer l'ancien répertoire si présent
                    rm -rf k8s-repo
                    
                    # URL du dépôt avec identifiants
                    REPO_URL="https://$GIT_CREDENTIALS_USR:$GIT_CREDENTIALS_PSW@github.com/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME.git"
                    
                    # Cloner le dépôt
                    echo "Clonage du dépôt..."
                    if git clone $REPO_URL k8s-repo; then
                        echo "Dépôt cloné avec succès."
                    else
                        echo "Échec du clonage. Initialisation d'un nouveau dépôt..."
                        mkdir -p k8s-repo
                        cd k8s-repo
                        git init
                        git remote add origin $REPO_URL
                        cd ..
                    fi
                    
                    # Copier les manifestes Kubernetes
                    echo "Copie des manifestes Kubernetes..."
                    cp -f k8s/*.yaml k8s-repo/
                    
                    # Configurer Git
                    cd k8s-repo
                    git config user.email "jenkins@example.com"
                    git config user.name "Jenkins CI"
                    
                    # Détecter la branche par défaut ou utiliser main
                    if git show-ref --verify --quiet refs/remotes/origin/$GITHUB_BRANCH; then
                        echo "Utilisation de la branche existante: $GITHUB_BRANCH"
                        git checkout $GITHUB_BRANCH || git checkout -b $GITHUB_BRANCH
                    else
                        echo "Création d'une nouvelle branche: $GITHUB_BRANCH"
                        git checkout -b $GITHUB_BRANCH
                    fi
                    
                    # Ajouter les fichiers modifiés
                    echo "Ajout des fichiers modifiés..."
                    git add .
                    
                    # Vérifier s'il y a des modifications à committer
                    if git diff --staged --quiet; then
                        echo "Aucun changement détecté, rien à committer."
                    else
                        echo "Commit des changements..."
                        git commit -m "Update kubernetes manifests for version $DOCKER_TAG"
                        
                        # Push des changements
                        echo "Push des changements vers GitHub..."
                        if ! git push origin $GITHUB_BRANCH; then
                            echo "Échec du push, tentative avec une nouvelle branche..."
                            TIMESTAMP=$(date +%Y%m%d%H%M%S)
                            NEW_BRANCH="${GITHUB_BRANCH}-${TIMESTAMP}"
                            git checkout -b $NEW_BRANCH
                            git push origin $NEW_BRANCH
                        fi
                    fi
                    
                    # Retour au répertoire de travail et nettoyage
                    cd ..
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Nettoyage des ressources..."
            sh 'docker rm -f jenkins || true'
        }
        
        success {
            echo "Pipeline terminé avec succès !"
        }
        
        failure {
            echo "Le pipeline a échoué. Veuillez vérifier les logs pour plus de détails."
        }
    }
}