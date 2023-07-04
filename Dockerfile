FROM node:18-alpine AS base

WORKDIR /app

COPY frontend/package.json ./
COPY frontend/package-lock.json ./
COPY frontend/tsconfig.json ./
COPY frontend/src/ src/
COPY frontend/public/ public/
RUN npm install
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libmariadb-dev pkg-config
RUN pip3 install --upgrade pip

COPY backend/airports/ airports/
COPY backend/api/ api/
COPY backend/flask_app/ flask_app/
COPY backend/clustering/ clustering/
COPY backend/database/ database/
COPY backend/haversine/ haversine/
COPY backend/threads/ threads/
COPY backend/profiling_decorators.py backend/run.py ./
COPY backend/pyproject.toml pyproject.toml

RUN cc -O3 -fPIC -shared -o haversine/distance.so haversine/distance.c
RUN pip3 install .

COPY --from=base /app/build/ flask_app/static/react/

EXPOSE 8000

CMD ["python3", "run.py"]


