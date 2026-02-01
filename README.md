# StockSteward AI - DevOps Project

This is a basic DevOps-ready project structure for StockSteward AI. It includes a FastAPI backend, a React frontend, and a complete infrastructure setup for containerization and CI/CD.

## Project Structure

```text
.
├── backend/            # FastAPI Backend
│   ├── app/           # Application source code
│   └── Dockerfile     # Backend container configuration
├── frontend/           # React Frontend
│   ├── src/           # Component source code
│   └── Dockerfile     # Frontend container configuration
├── infra/              # Infrastructure and configuration
│   └── env.sample     # Example environment variables
├── docker-compose.yml  # Local orchestration
├── Makefile            # Developer helper scripts
└── bitbucket-pipelines.yml # CI/CD configuration
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Make (optional, but recommended)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://bitbucket.org/selva-projects/stocksteward-ai.git
   cd stocksteward-ai
   ```

2. **Setup environment variables:**
   ```bash
   cp infra/env.sample .env
   ```

3. **Start the application:**
   Using Make:
   ```bash
   make up
   ```
   Or using Docker Compose directly:
   ```bash
   docker-compose up -d
   ```

4. **Access the services:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)

### DevOps Commands

The `Makefile` provides several helper commands:

- `make build`: Rebuild the containers.
- `make logs`: View container logs.
- `make down`: Stop all services.
- `make ps`: Check container status.

## CI/CD

This project uses **Bitbucket Pipelines** for automated building and testing. The configuration is defined in `bitbucket-pipelines.yml`.


This is a basic DevOps-ready project structure for StockSteward AI. It includes a FastAPI backend, a React frontend, and a complete infrastructure setup for containerization and CI/CD.

## Project Structure

```text
.
├── backend/            # FastAPI Backend
│   ├── app/           # Application source code
│   └── Dockerfile     # Backend container configuration
├── frontend/           # React Frontend
│   ├── src/           # Component source code
│   └── Dockerfile     # Frontend container configuration
├── infra/              # Infrastructure and configuration
│   └── env.sample     # Example environment variables
├── docker-compose.yml  # Local orchestration
├── Makefile            # Developer helper scripts
└── bitbucket-pipelines.yml # CI/CD configuration
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Make (optional, but recommended)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://bitbucket.org/selva-projects/stocksteward-ai.git
   cd stocksteward-ai/main
   ```

2. **Setup environment variables:**
   ```bash
   cp infra/env.sample .env
   ```

3. **Start the application:**
   Using Make:
   ```bash
   make up
   ```
   Or using Docker Compose directly:
   ```bash
   docker-compose up -d
   ```

4. **Access the services:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)

### DevOps Commands

The `Makefile` provides several helper commands:

- `make build`: Rebuild the containers.
- `make logs`: View container logs.
- `make down`: Stop all services.
- `make ps`: Check container status.

## CI/CD

This project uses **Bitbucket Pipelines** for automated building and testing. The configuration is defined in `bitbucket-pipelines.yml`.
