# Optimisation d'Actions avec Algorithmes en Python

Ce projet implémente 2 algorithmes pour optimiser la sélection d'actions financières en fonction de leurs coûts et bénéfices, avec des visualisations interactives à l'aide de Dash et Plotly.

---

## 📖 Sommaire

1. [Configuration du projet](#configuration-du-projet)

   - [Cloner le dépôt](#1-cloner-le-dépôt)
   - [Créer et activer un environnement virtuel](#2-créer-et-activer-un-environnement-virtuel)
   - [Installer les dépendances](#3-installer-les-dépendances)

2. [Lancement](#lancement)

## Configuration du projet

### 1. Cloner le dépôt

Pour commencer, clonez ce dépôt sur votre machine locale :

```sh
git clone https://github.com/ThomasDpr/6_algorithmes_en_python.git
cd 6_algorithmes_en_python
```

### 2. Créer et activer un environnement virtuel

Pour créer et activer un environnement virtuel, utilisez la commande suivante :

#### Linux / MacOS

```sh
python3 -m venv env
source env/bin/activate
```

#### Windows

```sh
python -m venv env
env\Scripts\activate
```

### 3. Installer les dépendances

#### Option 1 : Avec le fichier `requirements.txt`

Une fois l'environnement virtuel activé, installez les dépendances en utilisant le fichier `requirements.txt` :

```sh
pip install -r requirements.txt
```

#### Option 2 : Avec `pipenv`

Si vous préférez utiliser `pipenv` :

```sh
pipenv install
pipenv shell
```

## Lancement

### Exécution des algorithmes

Pour exécuter les algorithmes, utilisez les commandes suivantes :

```sh
python nom_de_l_algoritme.py
```

Remplacez `nom_de_l_algoritme` par le nom de l'algorithme que vous souhaitez exécuter.

### Visualisation des résultats

Une fois les algorithmes exécutés, vous pourrez visualiser les résultats en dans un dashboard interactif, pensez à checker l'url dans le terminal pour accéder au dashboard, même si celui-ci devrait s'ouvrir automatiquement.
