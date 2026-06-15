# Image Python légère et reproductible
FROM python:3.11-slim

# Empêche Python d'écrire des .pyc et force les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# Dépendances système minimales pour compiler certaines libs Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Étape critique pour le cache Docker ---
# On copie UNIQUEMENT requirements.txt en premier.
# Tant que ce fichier ne change pas, Docker réutilise le cache
# et ne réinstalle pas toutes les dépendances à chaque build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le reste du code source APRÈS l'installation des deps
COPY . .

# Utilisateur non-root pour la sécurité (bonne pratique production)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Port exposé par FastAPI
EXPOSE 8000

# Healthcheck : Docker sait si le conteneur est vraiment opérationnel
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Lancement de l'API depuis le bon module (api/main.py -> api.main)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]