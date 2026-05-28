# Auto Print - Projet Flask

Ce projet est une application Flask (`test_server.py`) avec des templates Jinja et un dossier `static/`.

## Hébergement GitHub

- Le code peut être stocké sur GitHub.
- **GitHub Pages ne peut pas héberger ce projet**, car il s'agit d'une application Python dynamique.
- Pour déployer l'application, utilise plutôt un service comme Render, Railway, PythonAnywhere, Fly ou Heroku.

## Préparation du dépôt

1. Vérifie tes modifications :
   ```bash
   git status
   ```
2. Ajoute les fichiers utiles :
   ```bash
   git add .gitignore README.md Procfile
   ```
3. Fais un commit :
   ```bash
   git commit -m "Ajout de fichiers d'aide pour GitHub et déploiement"
   ```
4. Pousse vers GitHub :
   ```bash
   git push origin main
   ```

> Si ta branche principale s'appelle `master`, remplace `main` par `master`.

## Déploiement recommandé

### Render
- Crée un compte sur https://render.com
- Ajoute un nouveau service Web
- Pointez-le sur ton dépôt GitHub
- Render détectera le fichier `render.yaml` et utilisera les paramètres suivants :
  - `buildCommand`: `pip install -r requirements.txt`
  - `startCommand`: `gunicorn test_server:app`
- Render installera `requirements.txt` automatiquement.

### Railway / PythonAnywhere
- Ces services supportent aussi les applications Flask et sont simples à configurer.

## Notes importantes

- Ton application enregistre des images dans `uploads/`, donc ce dossier n'est pas inclus dans le dépôt Git.
- Si tu veux une version purement statique, il faut supprimer le backend Flask et transformer les pages en HTML statique.
