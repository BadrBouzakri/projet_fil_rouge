pipeline {
    environment { 
        DOCKER_ID = "bouzakri" 
        DOCKER_IMAGE = "foot_app"
        DOCKER_TAG = "v.${BUILD_ID}.0"
        GITHUB_REPO_OWNER = "BadrBouzakri"
        GITHUB_REPO_NAME = "k8s-projet-prod"
        K8S_SUBFOLDER = "K8S_Prod"  // Sous-dossier pour les fichiers Kubernetes
    }
    
    agent any 
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 30, unit: 'MINUTES')
    }

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
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/dev/deployment.yaml
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/staging/deployment.yaml
                    sed -i "s+image:.*+image: $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG+g" k8s/prod/deployment.yaml
                    '''
                }
            }
        }

        stage('Create Namespaces') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                        for ns in dev staging prod; do
                            if ! kubectl get namespace $ns >/dev/null 2>&1; then
                                echo "Création du namespace $ns..."
                                kubectl create namespace $ns
                                echo "Namespace $ns créé avec succès"
                            else
                                echo "Le namespace $ns existe déjà"
                            fi
                        done
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
                    kubectl apply -f k8s/dev/deployment.yaml -n dev
                    kubectl apply -f k8s/dev/service.yaml -n dev
                    kubectl apply -f k8s/dev/pv.yaml -n dev
                    kubectl apply -f k8s/dev/pvc.yaml -n dev
                    kubectl apply -f k8s/dev/hpa.yaml -n dev
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
                    kubectl apply -f k8s/staging/deployment.yaml -n staging
                    kubectl apply -f k8s/staging/service.yaml -n staging
                    kubectl apply -f k8s/staging/pv.yaml -n staging
                    kubectl apply -f k8s/staging/pvc.yaml -n staging
                    kubectl apply -f k8s/staging/hpa.yaml -n staging
                    '''
                }
            }
        }

        stage('Push Kubernetes Manifests to Git') {
            environment {
                // Token d'accès personnel GitHub
                GITHUB_TOKEN = credentials('github-token')
            }
            steps {
                script {
                    sh '''
                        # Nettoyage préalable
                        rm -rf k8s-repo
                        
                        # URL du dépôt avec le token
                        REPO_URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}.git"
                        
                        # Cloner le dépôt
                        echo "Clonage du dépôt GitHub..."
                        if git clone "$REPO_URL" k8s-repo; then
                            echo "Dépôt cloné avec succès."
                        else
                            echo "Échec du clonage. Initialisation d'un nouveau dépôt..."
                            mkdir -p k8s-repo
                            cd k8s-repo
                            git init
                            echo "# Kubernetes manifests pour ${GITHUB_REPO_NAME}" > README.md
                            git add README.md
                            git commit -m "Initial commit"
                            git branch -M main
                            git remote add origin "$REPO_URL"
                            cd ..
                        fi
                        
                        # Créer le sous-dossier K8S_Prod s'il n'existe pas
                        echo "Création du sous-dossier ${K8S_SUBFOLDER}..."
                        mkdir -p k8s-repo/${K8S_SUBFOLDER}
                        
                        # Copier les manifestes Kubernetes dans le sous-dossier
                        echo "Copie des manifestes Kubernetes dans ${K8S_SUBFOLDER}..."
                        cp -f k8s/*.yaml k8s-repo/${K8S_SUBFOLDER}/
                        
                        # Configurer Git
                        cd k8s-repo
                        git config user.email "bouzakri.badr@gmail.com"
                        git config user.name "Jenkins CI"
                        
                        # S'assurer d'être sur main
                        git checkout main 2>/dev/null || git checkout -b main
                        
                        # Ajouter les fichiers modifiés
                        echo "Ajout des fichiers modifiés..."
                        git add .
                        
                        # Vérifier s'il y a des modifications
                        if git diff --staged --quiet; then
                            echo "Aucun changement détecté, rien à committer."
                        else
                            echo "Commit des changements..."
                            git commit -m "Update kubernetes manifests in ${K8S_SUBFOLDER} for version ${DOCKER_TAG}"
                            
                            # Push vers GitHub
                            echo "Push des changements vers GitHub..."
                            if git push origin main; then
                                echo "Push réussi!"
                            else
                                echo "Échec du push vers main. Création d'une branche alternative..."
                                BRANCH_NAME="update-k8s-${BUILD_ID}"
                                git checkout -b "${BRANCH_NAME}"
                                git push origin "${BRANCH_NAME}"
                                echo "Changements poussés vers la branche: ${BRANCH_NAME}"
                            fi
                        fi
                        
                        # Sauvegarde locale (backup)
                        echo "Création d'une sauvegarde locale..."
                        cd ..
                        tar -czf k8s-manifests-${BUILD_ID}.tar.gz k8s-repo/${K8S_SUBFOLDER}/*.yaml
                        echo "Sauvegarde créée: k8s-manifests-${BUILD_ID}.tar.gz"
                    '''
                    
                    // Archiver la sauvegarde locale
                    archiveArtifacts artifacts: "k8s-manifests-${env.BUILD_ID}.tar.gz", fingerprint: true
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f jenkins || true'
        }
        
        success {
            echo "Pipeline terminé avec succès!"
        }
        
        failure {
            echo "Le pipeline a échoué. Veuillez vérifier les logs."
        }
    }
}