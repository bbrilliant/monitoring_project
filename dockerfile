# ---- Image de base ----
FROM python:3.11-slim

# ---- Variables d'environnement ----
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ---- Dossier de travail ----
WORKDIR /app

# ---- Installation des dépendances ----
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copie du projet ----
COPY . /app/

# ---- Exposition du port ----
EXPOSE 8001

# ---- Commande de démarrage ----
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
