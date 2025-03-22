#!/bin/bash
# Script de nettoyage et redéploiement pour le namespace prod

# Nettoyage du namespace prod
echo "Nettoyage du namespace prod..."

# 1. Supprimer le HPA
kubectl delete hpa foot-app-hpa -n prod --ignore-not-found=true

# 2. Supprimer les pods
kubectl delete pod --all -n prod --force --grace-period=0

# 3. Supprimer les deployments
kubectl delete deployment --all -n prod

# 4. Supprimer les services
kubectl delete svc --all -n prod

# 5. Supprimer l'ingress
kubectl delete ingress --all -n prod

# 6. Supprimer les PVCs anciens
kubectl delete pvc foot-app-pvc -n prod --ignore-not-found=true
kubectl delete pvc foot-app-pvc-new -n prod --ignore-not-found=true

# 7. Supprimer les PVs anciens
kubectl delete pv foot-app-pv --ignore-not-found=true
kubectl delete pv foot-app-pv-new --ignore-not-found=true

echo "Nettoyage terminé"

# Attendre que tout soit bien supprimé
echo "Attente de 10 secondes pour s'assurer que tout est nettoyé..."
sleep 10

# Déploiement des nouvelles configurations
echo "Déploiement des nouvelles ressources..."

# 1. Créer la StorageClass
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/storage-class.yaml

# 2. Déployer le PVC
# Assurez-vous que le fichier pvc.yaml est celui avec le nouveau contenu
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/pvc.yaml

# 3. Déployer le service
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/service.yaml

# 4. Déployer le Deployment
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/deployment.yaml

# 5. Déployer l'ingress
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/ingress.yaml

# 6. Déployer le HPA
kubectl apply -f /data/tech/cours/projet_fil_rouge/k8s/prod/hpa.yaml

echo "Déploiement terminé"
echo "Vérification des ressources..."

# Vérification des ressources
kubectl get pvc -n prod
kubectl get pods -n prod
kubectl get deployments -n prod
kubectl get svc -n prod
kubectl get ingress -n prod

echo "Configuration terminée!"