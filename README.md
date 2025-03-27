### Application de Gestion d'Équipes de Football - CI/CD avec Jenkins et Kubernetes

**Application créée par Badr Bouzakri**

Cette application web permet de générer des équipes équilibrées pour les matchs de football (futsal) à partir d'une liste de joueurs avec leurs niveaux respectifs. Elle dispose également d'une console d'administration pour gérer les joueurs et leurs évaluations.


## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Installation locale avec Docker](#installation-locale-avec-docker)
5. [Installation avec Kubernetes](#installation-avec-kubernetes)
6. [Pipeline CI/CD avec Jenkins](#pipeline-cicd-avec-jenkins)
7. [Déploiement sur AWS EKS](#déploiement-sur-aws-eks)
8. [Structure des fichiers](#structure-des-fichiers)
9. [Accès à l'application](#accès-à-lapplication)
10. [Guide d'utilisation](#guide-dutilisation)
11. [Contributeurs](#contributeurs)

## Fonctionnalités

- **Sélection et équilibrage d'équipes**:
  - Sélectionnez jusqu'à 10 joueurs pour générer deux équipes équilibrées
  - Plusieurs algorithmes d'équilibrage : par compétence, par serpent (1-2-2-1), ou aléatoire
  - Visualisation du pourcentage d'équilibre entre les équipes

- **Administration des joueurs**:
  - Interface sécurisée par authentification
  - Ajout, modification et suppression de joueurs
  - Attribution de scores de compétence (0-100%)
  - Recherche rapide parmi les joueurs disponibles

- **Interface responsive**:
  - Compatible mobile et desktop
  - Animations et transitions visuelles

## Architecture

L'application est construite avec les technologies suivantes:
- **Backend**: Flask (Python 3.9)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Base de données**: Stockage des données persistant via volumes Kubernetes
- **Conteneurisation**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins

L'architecture de déploiement comprend:
- Environnement de développement (dev)
- Environnement de staging
- Environnement de production (sur AWS EKS)

## Prérequis

- **Docker** : Pour exécuter l'application dans un conteneur
- **Kubernetes** : Pour le déploiement dans les différents environnements
- **Jenkins** : Pour l'intégration continue et le déploiement continu
- **kubectl** : Client en ligne de commande pour Kubernetes
- **Git** : Pour la gestion du code source
- **Accès AWS** (facultatif): Pour le déploiement sur AWS EKS

## Installation locale avec Docker

```bash
# Cloner le projet
git clone git@github.com:BadrBouzakri/futsal_team_selector.git
cd futsal_team_selector

# Démarrer l'application avec Docker Compose
docker build -t footselectorimage .

docker run -d -p 5000:5000 -name footselector footselectorimage 
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
kubectl apply -f kubernetes/dev/hpa.yaml

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
kubectl apply -f kubernetes/staging/hpa.yaml

# Vérifier le déploiement
kubectl get all -n futsal-staging
```

## Pipeline CI/CD avec Jenkins

Un pipeline d'intégration continue et de déploiement continu est configuré dans le fichier `Jenkinsfile`. Il automatise:

1. **Build** : Construction de l'image Docker
2. **Test** : Vérification du fonctionnement de l'application
3. **Push** : Publication de l'image sur Docker Hub
4. **Deploy** : Déploiement sur les environnements Kubernetes
5. **Backup** : Sauvegarde des manifestes Kubernetes

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

3. Configurez les identifiants Jenkins :
   - Ajoutez votre fichier kubeconfig (ID: `config`)
   - Configurez les accès Docker Hub (ID: `DOCKER_HUB_PASS`)

4. Créez un pipeline pointant vers le repository Git.

## Déploiement sur AWS EKS

L'application peut être déployée sur un cluster Amazon EKS. Ce déploiement est géré par une infrastructure Terraform séparée disponible dans le repository [badr-project-k8s-iac](https://github.com/BadrBouzakri/badr-project-k8s-iac).

Pour déployer sur l'infrastructure AWS:

1. Déployez d'abord l'infrastructure avec Terraform
2. Configurez les variables d'environnement appropriées
3. Exécutez le pipeline Jenkins avec les paramètres EKS

Pour plus de détails, voir la section [Déploiement sur AWS EKS](#déploiement-sur-aws-eks).

## Structure des fichiers

```
futsal_team_selector/
├── app/                         # Application Flask
├── Dockerfile                   # Fichier de construction Docker
├── docker-compose.yaml          # Configuration pour le développement local
├── Jenkinsfile                  # Configuration du pipeline CI/CD
├── kubernetes/                  # Configurations Kubernetes
│   ├── dev/                     # Environnement de développement
│   ├── staging/                 # Environnement de staging
│   └── prod/                    # Environnement de production
├── templates/                   # Templates HTML pour l'interface utilisateur
│   ├── index.html              
│   ├── teams.html              
│   ├── admin.html              
│   └── admin_console.html      
└── README.md                    # Documentation du projet
```

## Accès à l'application

### Via NodePort (accès direct)
- **Environnement de développement** : http://[ADRESSE_IP_NODE]:30080
- **Environnement de staging** : http://[ADRESSE_IP_NODE]:30081

### Via Ingress (nom de domaine)
- **Environnement de développement** : https://dev.foot.badr.cloud
- **Environnement de production** : https://foot.badr.cloud

### Administration
- **Admin** : Ajoutez `/admin` à l'URL (identifiants par défaut: admin/admin)

## Guide d'utilisation

1. **Page d'accueil** : Sélectionnez 10 joueurs et choisissez une méthode d'équilibrage
2. **Génération d'équipes** : Cliquez sur "Générer des équipes"
3. **Visualisation** : Les équipes s'affichent avec leurs statistiques
4. **Administration** : Accédez à `/admin` et connectez-vous pour gérer les joueurs

## Contributeurs

- **Badr Bouzakri** - Développeur principal