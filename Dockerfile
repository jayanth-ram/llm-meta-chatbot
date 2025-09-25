# ---- base ----
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1  PYTHONUNBUFFERED=1
WORKDIR /srv

# (optional) build tools if you use packages needing gcc
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- deps ----
# requirements.txt is now at the repo root
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# ---- app code ----
# copy backend sources into the image working dir
COPY backend/app ./app

# ---- run ----
ENV PORT=8000
EXPOSE 8000
CMD ["bash","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
