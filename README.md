# PDF Toolkit

Un compresseur de PDF simple, avec une interface web en français et un lancement en une commande avec Docker. Sélectionnez un document, choisissez la qualité et téléchargez le résultat.

## Démarrage rapide avec Docker

Prérequis : Docker Engine ou Docker Desktop, avec Docker Compose v2.
Depuis le dossier du projet :

```bash
docker compose up --build -d
```

Ouvrez **http://localhost:8080**. Aucun compte, service externe ou volume à configurer.

```bash
# Voir les journaux
docker compose logs -f

# Arrêter l’application
docker compose down
```

Pour utiliser un autre port :

```bash
PORT=8090 docker compose up -d
```

Sur PowerShell : `$env:PORT=8090` puis `docker compose up -d`.

Sans Compose :

```bash
docker build -t pdf-toolkit .
docker run --rm -p 127.0.0.1:8080:8080 pdf-toolkit
```

## Utilisation

1. Choisissez un fichier PDF (envoi limité à **50 Mio**, formulaire compris).
2. Sélectionnez le niveau de qualité.
3. Cliquez sur **Compresser le PDF**, puis sur **Télécharger le PDF**.

| Réglage | Usage |
| --- | --- |
| Forte (`screen`) | Lecture à l’écran, images moins détaillées |
| Équilibrée (`ebook`) | Partage courant, réglage par défaut |
| Légère (`printer`) | Documents destinés à l’impression |
| Haute qualité (`prepress`) | Priorité à la qualité des images |

La réduction dépend du contenu : un PDF essentiellement textuel ou déjà optimisé peut peu changer. Si la sortie est plus volumineuse, l’application renvoie le fichier original. La compression réécrit le PDF : utilisez l’original pour conserver les signatures numériques et vérifiez le rendu des documents importants.

## Confidentialité et limites

- Les documents sont traités sur la machine qui héberge l’application, sans service tiers.
- Les fichiers temporaires sont supprimés après traitement ; aucun historique n’est conservé.
- Une compression est limitée à 120 secondes. Deux traitements peuvent être exécutés simultanément.
- Compose utilise un compte sans privilèges, un système de fichiers en lecture seule et un espace temporaire en mémoire de 512 Mio, avec une limite de 1 Gio de mémoire par conteneur.
- Le port est accessible uniquement depuis votre machine par défaut. Cette application personnelle n’intègre pas d’authentification : une exposition publique nécessite une protection adaptée.

## Développement local

Python 3.12 et Ghostscript sont nécessaires. Sous Debian/Ubuntu :

```bash
sudo apt-get update
sudo apt-get install -y ghostscript python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 8080
```

Le serveur Flask sert au développement ; l’image Docker utilise Gunicorn.

### Interface bureau optionnelle

L’interface CustomTkinter reste disponible hors Docker, avec Python, Ghostscript et Tk installés :

```bash
# Debian/Ubuntu : sudo apt-get install python3-tk
pip install -r requirements-desktop.txt
python main.py
```

La compression s’exécute en arrière-plan pour garder la fenêtre réactive.

### Tests

```bash
python -m unittest discover -s tests -v
```

Les tests couvrent les erreurs, les limites d’envoi, la préservation des fichiers et la compression réelle avec Ghostscript pour les quatre niveaux de qualité. Le test réel est ignoré si Ghostscript manque. GitHub Actions installe Ghostscript, exécute les tests et vérifie le démarrage Docker.

## Organisation

```text
app.py                    Interface web Flask
compressor.py             Compression Ghostscript partagée
gui.py / main.py          Interface bureau optionnelle
templates/ / static/      Interface web (sans CDN)
tests/                    Tests unitaires et intégration
Dockerfile / compose.yaml Déploiement local
```

Les dépendances Python web et bureau sont séparées. Le module Python `ghostscript`, `pdf2image` et `pymupdf` ne sont pas nécessaires : la compression utilise directement l’exécutable système `gs`.

Références : [gestion des fichiers avec Flask](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/) et [configuration Gunicorn](https://docs.gunicorn.org/en/stable/settings.html).
