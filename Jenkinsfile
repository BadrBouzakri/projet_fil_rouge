pipeline {
    agent any
    
    environment {
        // Définir les variables d'environnement pour le pipeline
        DOCKER_REGISTRY = "BadrBouzakri"
        DOCKER_IMAGE = 'futsal-team-selector'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        DOCKER_FULL_IMAGE = "${DOCKER_IMAGE}:${DOCKER_TAG}"
        // Utiliser des credentials pour kubectl
        KUBECONFIG = credentials('kubeconfig')
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Récupérer le code source
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                // Construire l'image Docker
                sh "docker build -t ${DOCKER_FULL_IMAGE} ."
                echo "Image Docker construite: ${DOCKER_FULL_IMAGE}"
            }
        }
        
        stage('Run Tests') {
            steps {
                // Ici, vous pourriez ajouter des tests unitaires si nécessaire
                echo "Exécution des tests..."
                // Exemple: sh "docker run --rm ${DOCKER_FULL_IMAGE} python -m pytest"
            }
        }
        
        stage('Push to Registry') {
            steps {
                // Pousser l'image vers un registre Docker (local ou distant)
                withCredentials([string(credentialsId: 'docker-registry', variable: 'DOCKER_REGISTRY')]) {
                    sh "docker tag ${DOCKER_FULL_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_FULL_IMAGE}"
                    sh "docker push ${DOCKER_REGISTRY}/${DOCKER_FULL_IMAGE}"
                    echo "Image poussée vers ${DOCKER_REGISTRY}/${DOCKER_FULL_IMAGE}"
                }
            }
        }
        
        stage('Deploy to Dev') {
            steps {
                // Mettre à jour l'image dans le fichier de déploiement
                sh "sed -i 's|image:.*|image: ${DOCKER_REGISTRY}/${DOCKER_FULL_IMAGE}|' kubernetes/dev/deployment.yaml"
                
                // Déployer sur l'environnement de développement
                sh "kubectl apply -f kubernetes/dev/namespace.yaml"
                sh "kubectl apply -f kubernetes/dev/persistent-volume.yaml"
                sh "kubectl apply -f kubernetes/dev/persistent-volume-claim.yaml"
                sh "kubectl apply -f kubernetes/dev/configmap.yaml"
                sh "kubectl apply -f kubernetes/dev/deployment.yaml"
                sh "kubectl apply -f kubernetes/dev/service.yaml"
                sh "kubectl apply -f kubernetes/dev/horizontal-pod-autoscaler.yaml"
                
                echo "Déploiement sur l'environnement dev terminé!"
            }
        }
        
        stage('Deploy to Staging') {
            when {
                // Déployer sur staging uniquement depuis la branche main
                branch 'main'
            }
            steps {
                // Attendre la validation manuelle avant de déployer en staging
                input message: 'Déployer en environnement de staging?', ok: 'Déployer'
                
                // Mettre à jour l'image dans le fichier de déploiement
                sh "sed -i 's|image:.*|image: ${DOCKER_REGISTRY}/${DOCKER_FULL_IMAGE}|' kubernetes/staging/deployment.yaml"
                
                // Déployer sur l'environnement de staging
                sh "kubectl apply -f kubernetes/staging/namespace.yaml"
                sh "kubectl apply -f kubernetes/staging/persistent-volume.yaml"
                sh "kubectl apply -f kubernetes/staging/persistent-volume-claim.yaml"
                sh "kubectl apply -f kubernetes/staging/configmap.yaml"
                sh "kubectl apply -f kubernetes/staging/deployment.yaml"
                sh "kubectl apply -f kubernetes/staging/service.yaml"
                sh "kubectl apply -f kubernetes/staging/horizontal-pod-autoscaler.yaml"
                
                echo "Déploiement sur l'environnement staging terminé!"
            }
        }
    }
    
    post {
        success {
            echo "Pipeline terminé avec succès!"
        }
        failure {
            echo "Échec du pipeline. Vérifiez les logs pour plus d'informations."
        }
    }
}