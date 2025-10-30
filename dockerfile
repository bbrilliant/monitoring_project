# --- Étape 1 : Image de base ---
FROM python:3.11-slim

# --- Étape 2 : Variables d'environnement ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : Répertoire de travail ---
WORKDIR /app

# --- Étape 5 : Installation des dépendances Python ---
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Étape 6 : Copie du code du projet ---
COPY . /app/

# --- Étape 7 : Script d’attente du service Redis ---
COPY ./wait_for_redis.sh /wait_for_redis.sh
RUN chmod +x /wait_for_redis.sh

# --- Étape 8 : Exposition du port ---
EXPOSE 8001

# --- Étape 9 : Commande par défaut ---
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
