# ---- Base image
FROM python:3.11-slim

# ---- Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Workdir
WORKDIR /app

# ---- Install deps into a venv
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:${PATH}"

# ---- Copy code
# If your FastAPI app lives at backend/app, keep this line.
# If it's somewhere else, update the path accordingly.
COPY backend/app ./app

# ---- Ports
# Railway will map the container port; we still expose one for clarity.
EXPOSE 8000

# ---- Start
# Respect Railway/Heroku-style $PORT if present, default to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
