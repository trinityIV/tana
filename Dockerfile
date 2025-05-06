FROM python:3.10-slim

WORKDIR /app

# Copier les fichiers source
COPY id_protector.py discord_bot.py requirements.txt ./
COPY .env ./

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Création du volume pour la persistance
VOLUME /app/data

# Création du répertoire data s'il n'existe pas
RUN mkdir -p /app/data

# Définition des variables d'environnement
ENV CONFIG_PATH=/app/data/config.json
ENV PYTHONUNBUFFERED=1

# Point d'entrée
CMD ["python", "discord_bot.py"]
