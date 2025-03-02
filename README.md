# Application de Gestion d'Équipes - CI/CD avec Jenkins et Kubernetes

**Application créée par Badr**

Cette application permet de générer des équipes équilibrées à partir d'une liste de joueurs. Elle dispose également d'une console d'administration pour ajouter des joueurs et gérer leurs scores.

## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Prérequis](#prérequis)
3. [Installation locale avec Docker](#installation-locale-avec-docker)
4. [Installation avec Kubernetes](#installation-avec-kubernetes)
5. [Pipeline CI/CD avec Jenkins](#pipeline-cicd-avec-jenkins)
6. [Structure des fichiers](#structure-des-fichiers)
7. [Accès à l'application](#accès-à-lapplication)
8. [Contributeurs](#contributeurs)

## Fonctionnalités

- Sélectionnez jusqu'à 10 joueurs pour générer des équipes équilibrées.
- Affichage dynamique des équipes générées.
- Console d'administration pour ajouter et gérer des joueurs.
- Authentification pour accéder à la console d'administration.
- Intégration continue avec Jenkins
- Déploiement continu sur Kubernetes (environnements dev et staging)

## Prérequis

- **Docker** : Pour exécuter l'application dans un conteneur.
- **Kubernetes** : Pour le déploiement dans des environnements dev et staging.
- **Jenkins** : Pour l'intégration continue et le déploiement continu.
- **kubectl** : Client en ligne de commande pour Kubernetes.
- **Git** : Pour la gestion du code source.

## Installation locale avec Docker

### Développement local avec Docker Compose

```bash
# Cloner le projet
git clone git@github.com:BadrBouzakri/futsal_team_selector.git
cd futsal_team_selector

# Démarrer l'application avec Docker Compose
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

L'application sera accessible à l'adresse http://localhost:5000.

## Installation avec Kubernetes

### Préparation

1. Assurez-vous que votre cluster Kubernetes est opérationnel et que kubectl est correctement configuré.
2. Créez les répertoires pour les volumes persistants :

```bash
# Sur tous les nœuds du cluster où les pods pourraient être programmés
sudo mkdir -p /mnt/data/futsal-dev /mnt/data/futsal-staging
sudo chmod 777 /mnt/data/futsal-dev /mnt/data/futsal-staging
```

### Déploiement dans l'environnement de développement

```bash
# Créer le namespace et les ressources Kubernetes
kubectl apply -f kubernetes/dev/namespace.yaml
kubectl apply -f kubernetes/dev/persistent-volume.yaml
kubectl apply -f kubernetes/dev/persistent-volume-claim.yaml
kubectl apply -f kubernetes/dev/configmap.yaml
kubectl apply -f kubernetes/dev/deployment.yaml
kubectl apply -f kubernetes/dev/service.yaml

# Vérifier le déploiement
kubectl get all -n futsal-dev
```

### Déploiement dans l'environnement de staging

```bash
# Créer le namespace et les ressources Kubernetes
kubectl apply -f kubernetes/staging/namespace.yaml
kubectl apply -f kubernetes/staging/persistent-volume.yaml
kubectl apply -f kubernetes/staging/persistent-volume-claim.yaml
kubectl apply -f kubernetes/staging/configmap.yaml
kubectl apply -f kubernetes/staging/deployment.yaml
kubectl apply -f kubernetes/staging/service.yaml

# Vérifier le déploiement
kubectl get all -n futsal-staging
```

## Pipeline CI/CD avec Jenkins

Ce projet utilise Jenkins pour l'intégration continue et le déploiement continu. Le pipeline est défini dans le fichier `Jenkinsfile`.

### Configuration de Jenkins

1. Installez Jenkins (avec Docker) :

```bash
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkinsci/blueocean
```

2. Récupérez le mot de passe initial :

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

3. Accédez à http://localhost:8080 et suivez les instructions pour terminer l'installation.

4. Installez les plugins suivants :
   - Docker Pipeline
   - Kubernetes CLI
   - Credentials Plugin

5. Configurez les identifiants Jenkins :
   - Ajoutez votre fichier kubeconfig dans Jenkins (ID: `kubeconfig`)
   - Configurez l'URL de votre registre Docker (ID: `docker-registry`)

6. Créez un nouveau pipeline dans Jenkins :
   - Sélectionnez "New Item"
   - Choisissez "Pipeline"
   - Dans la configuration, sélectionnez "Pipeline script from SCM"
   - Spécifiez l'URL de votre dépôt Git et le chemin du Jenkinsfile

### Exécution du pipeline

Le pipeline Jenkins s'exécutera automatiquement à chaque push sur le dépôt Git. Il comprend :
1. Checkout du code
2. Construction de l'image Docker
3. Tests
4. Push de l'image vers le registre
5. Déploiement en environnement dev
6. Déploiement en environnement staging (avec validation manuelle)

## Structure des fichiers

```
futsal_team_selector/
├── app/                         # Application Flask
├── Dockerfile                   # Fichier de construction Docker
├── docker-compose.yaml          # Configuration pour le développement local
├── Jenkinsfile                  # Configuration du pipeline CI/CD
├── kubernetes/                  # Configurations Kubernetes
│   ├── dev/                     # Environnement de développement
│   └── staging/                 # Environnement de staging
└── README.md                    # Documentation du projet
```

## Accès à l'application

### Via NodePort (accès direct)
- **Environnement de développement** : http://[ADRESSE_IP_NODE]:30080
- **Environnement de staging** : http://[ADRESSE_IP_NODE]:30081

### Via Ingress (nom de domaine)
- **Environnement de développement** : https://dev.foot.badr.cloud
- **Environnement de staging** : https://foot.badr.cloud

### Administration
- **Admin** : Ajoutez `/admin` à l'URL (identifiants: admin/admin)

## Contributeurs

- **Badr** - Développeur principal de l'application.