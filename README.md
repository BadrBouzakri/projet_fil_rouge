# Application de Gestion d'Équipes

**Application créée par Badr**

Cette application permet de générer des équipes équilibrées à partir d'une liste de joueurs. Elle dispose également d'une console d'administration pour ajouter des joueurs et gérer leurs scores.

## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Prérequis](#prérequis)
3. [Installation avec Docker](#installation-avec-docker)
4. [Exécution](#exécution)
5. [Accès à l'administration](#accès-à-ladministration)
6. [Structure des fichiers](#structure-des-fichiers)
7. [API](#api)
8. [Contributeurs](#contributeurs)

## Fonctionnalités

- Sélectionnez jusqu'à 10 joueurs pour générer des équipes équilibrées.
- Affichage dynamique des équipes générées.
- Console d'administration pour ajouter et gérer des joueurs.
- Authentification pour accéder à la console d'administration.
- Texte de pied de page **"Application créée par Badr"** présent sur toutes les pages.
- Affichage dynamique de l'année courante dans le pied de page.

## Prérequis

- **Docker** : Vous aurez besoin de Docker pour exécuter l'application dans un conteneur.

## Installation avec Docker

### Étape 1 : Cloner le projet

Clonez ce dépôt Git sur votre machine locale :

```bash
git clone git@github.com:BadrBouzakri/futsal_team_selector.git
cd futsal_team_selector
```

### Étape 2 : Construire l'image Docker

Construisez l'image Docker en utilisant le fichier **`Dockerfile`** fourni. Assurez-vous d'être dans le répertoire du projet.

```bash
docker build -t application-equipes .
```

### Étape 3 : Lancer le conteneur

Une fois l'image Docker construite, vous pouvez exécuter l'application à l'aide de Docker. Utilisez cette commande pour démarrer un conteneur à partir de l'image :

```bash
docker run -d -p 5050:5050 --name app-equipes application-equipes
```

- `-d` exécute le conteneur en mode détaché (en arrière-plan).
- `-p 5050:5050` mappe le port 5050 du conteneur au port 5050 de votre machine.
- `--name app-equipes` nomme le conteneur pour une gestion plus facile.

### Étape 4 : Accéder à l'application

Une fois le conteneur en cours d'exécution, vous pouvez accéder à l'application via un navigateur en visitant :

```
http://localhost:5050
```

## Exécution (Docker)

Pour vérifier si le conteneur est en cours d'exécution, utilisez la commande suivante :

```bash
docker ps
```

Pour arrêter le conteneur :

```bash
docker stop app-equipes
```

Pour relancer le conteneur :

```bash
docker start app-equipes
```

Pour supprimer le conteneur :

```bash
docker rm -f app-equipes
```

## Accès à l'administration

L'application dispose d'une console d'administration accessible via l'URL suivante :

```
http://localhost:5050/admin
```

Les identifiants par défaut pour accéder à la console d'administration sont :

- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `admin'

Vous pouvez utiliser cette console pour ajouter de nouveaux joueurs et modifier leurs scores.

## Structure des fichiers

Voici la structure des fichiers principaux de l'application :

```
.
├── app.py                  # Fichier principal de l'application Flask
├── templates/
│   ├── base.html           # Modèle de base pour les pages
│   ├── index.html          # Page d'accueil
│   ├── teams.html          # Page des équipes générées
│   ├── admin.html          # Page de connexion à l'administration
│   └── admin_console.html  # Console d'administration pour ajouter des joueurs
├── static/
│   ├── css/                # Fichiers CSS (optionnel)
│   └── js/                 # Fichiers JavaScript (optionnel)
├── requirements.txt        # Liste des dépendances Python
├── Dockerfile              # Pour créer une image Docker de l'application
└── README.md               # Fichier que vous lisez actuellement
```

## Dockerfile

Voici un aperçu du **Dockerfile** utilisé pour construire l'image Docker :

```Dockerfile
# Utilisation de Python comme image de base
FROM python:3.9-slim

# Définir le répertoire de travail à /app
WORKDIR /app

# Copier les fichiers requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . .

# Exposer le port 5050
EXPOSE 5050

# Définir la commande pour démarrer l'application
CMD ["python", "app.py"]
```

## API

### Routes principales

1. **`/`** : Page d'accueil où vous pouvez sélectionner des joueurs pour générer des équipes.
2. **`/teams`** : Affiche les équipes générées.
3. **`/admin`** : Page de connexion pour accéder à la console d'administration.
4. **`/admin/console`** : Console d'administration pour ajouter ou modifier des joueurs.

### Exemples de routes API (pour une future extension)

Vous pouvez envisager d'ajouter des routes API si vous souhaitez étendre l'application avec une fonctionnalité RESTful.

## Contributeurs

- **Badr** - Développeur principal de l'application.

---

Ce **README** vous guide sur la façon de **construire** et **exécuter** l'application en utilisant Docker, ce qui simplifie l'installation et la gestion des dépendances. Si vous avez des modifications ou des améliorations à ajouter, vous pouvez facilement ajuster ce fichier.
