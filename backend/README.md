# Backend JWT API (FastAPI)

Aplicación Web API con FastAPI que implementa autenticación JWT.

## Requisitos

- Python 3.11+
- Poetry
- Docker y Docker Compose (opcional)

## Instalación con Poetry

```bash
cd backend
poetry install
cp .env.example .env
```

## Ejecutar localmente

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### 1) Obtener token

`POST /token`

Body JSON:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Respuesta:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 300
}
```

### 2) Refrescar token

`POST /refresh`

Header:

```text
Authorization: Bearer <jwt>
```

Respuesta:

```json
{
  "access_token": "<nuevo_jwt>",
  "token_type": "bearer",
  "expires_in": 300
}
```

## Ejecutar con Docker

Desde la carpeta `backend`:

```bash
cp .env.example .env
docker compose up --build
```

API disponible en `http://localhost:8000`.
