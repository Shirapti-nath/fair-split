FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY pytest.ini .
COPY --from=frontend /frontend/dist ./frontend/dist

ENV PYTHONUNBUFFERED=1
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
