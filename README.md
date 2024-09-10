# Nussbaum scraper

Un web scraper écrit en Python qui permet de télécharger tous les cours d'informatique de MP2I.

De plus, le programme va automatiquement simplifier chaque fichier PDF avec [mp2i-thiers/pdf-cleaner](https://github.com/mp2i-thiers/pdf-cleaner), 
pour améliorer leur lisibilité.

## ⚠️ Avertissement

Il faut éviter d'utiliser ce programme trop souvent, afin d'éviter de surcharger le site. Téléchargez tout une fois, et ça devrait être bon.

## Installation

Tout d'abord, installez [Git](https://git-scm.com/) (normalement disponible de base sur Linux), et Python.

Puis, dans un terminal, lancez :
```
git clone --recursive https://github.com/mp2i-thiers/nussbaum-scraper.git
cd nussbaum-scraper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
(Note : sur windows les commandes peuvent changer)

## Utilisation

Lancez le programme avec `python nussbaum_scraper.py`. Il va créer automatiquement un dossier `nussbaum` dans le répertoire courant avec tous les cours simplifiés.
