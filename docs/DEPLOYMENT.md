# JourneyAI Production Deployment Guide

This guide explains how to deploy JourneyAI in production using Docker Compose.

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed on the VM.
    ```
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    ```
- Access to external API services (OpenAI, Groq, etc.)

### 2. Environment Setup

Create a `.env.prod` file in the root directory with your production configuration. Should be derived from `.env.example`.

### 3. Deploy

#### Using Make (Recommended)
```bash
make run-production
```

### 4. Verify Deployment

- API Health Check: `http://your-server:8000/`
- API Documentation: `http://your-server:8000/docs`
- Qdrant Dashboard: `http://your-server:6333/dashboard`

## Services Overview

The production setup includes:

- **app**: Main FastAPI application (Port 8000)
- **artifacts-worker**: Background worker for artifact processing
- **agents-worker**: Background worker for agent processing  
- **messages-worker**: Background worker for message processing
- **mongodb**: MongoDB database (Port 27017)
- **redis**: Redis cache/message broker (Port 6379)
- **qdrant**: Vector database (Ports 6333, 6334)

## Local Development

For local development, use the local Docker Compose file:

```bash
make run-local
```

This uses `docker-compose.local.yaml` which only runs the infrastructure services (MongoDB, Redis, Qdrant) while running the application processes directly on your machine.

## Monitoring

### Health Checks
The main application includes health checks. Check service status:
```bash
docker compose ps
```

### Logs
View logs for all services:
```bash
docker compose logs -f
```

View logs for specific service:
```bash
docker compose logs -f app
docker compose logs -f agents-worker
```

### Resource Usage
Monitor resource usage:
```bash
docker stats
```

## Maintenance

### Stop Services
```bash
make stop-production
# or
docker compose down
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### Backup Data
```bash
# Backup MongoDB
docker exec journeyai-mongodb mongodump --out /data/backup

# Backup Qdrant (if needed)
docker exec journeyai-qdrant qdrant-backup

# Copy backups to host
docker cp journeyai-mongodb:/data/backup ./mongodb-backup
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 27017, 6379, 6333, 6334, 3100 are available
2. **Environment variables**: Double-check your `.env.prod` file
3. **API keys**: Ensure all external API keys are valid
4. **Memory**: Ensure sufficient memory for all services

### Debug Commands

```bash
# Check service status
docker compose ps

# View service logs
docker compose logs [service-name]

# Execute commands in containers
docker compose exec app bash
docker compose exec mongodb mongo

# Check network connectivity
docker compose exec app ping mongodb
docker compose exec app ping redis
```

## Security Notes

- Change default passwords and API keys
- Use proper firewall rules
- Enable SSL/TLS for production
- Regularly update Docker images
- Monitor logs for suspicious activity 