# Docker Usage Guide for Fraudubot

This guide explains how to build, run, and manage the Fraudubot application using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system.
- [Docker Compose](https://docs.docker.com/compose/install/) (if not included with Docker Desktop).

## 1. Build the Docker Image

From the project root directory, run:

```bash
docker build -t fraudubot .
```

This command builds the Docker image using the provided `Dockerfile`.

## 2. Run the Container

To start the application in a container:

```bash
docker run -it --rm -p 8501:8501 fraudubot
```

- `-p 8501:8501` maps the app’s port to your local machine (adjust if your app uses a different port).
- `--rm` removes the container after it stops.

## 3. Using Docker Compose

To start all services defined in `docker-compose.yml`:

```bash
docker-compose up --build
```

- This will build images (if needed) and start the containers as defined in the compose file.

To stop the services:

```bash
docker-compose down
```

## 4. Volumes and Data

- The application may use local folders (e.g., `logs/`, `Datos/`, `Modelos_Entrenados/`) for data persistence.
- You can map these as volumes in `docker-compose.yml` to persist data outside the container.

## 5. Environment Variables

- If your application requires environment variables, set them in the `docker-compose.yml` or pass them with `-e` when running `docker run`.

## 6. Troubleshooting

- If you encounter permission issues with mounted volumes, ensure your user has the correct permissions.
- Check logs with `docker logs <container_id>` for debugging.

## 7. Updating the Image

If you make changes to the code or dependencies, rebuild the image:

```bash
docker-compose build
```
or
```bash
docker build -t fraudubot .
```