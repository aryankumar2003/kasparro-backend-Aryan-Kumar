# Data Ingestion and API System

## Overview
This system is a robust ETL (Extract, Transform, Load) pipeline designed to ingest cryptocurrency data from multiple sources, normalize it into a unified schema, and expose it via a high-performance REST API. It features fault tolerance, execution tracking, and audit logging.

## Features
- **Multi-Source Ingestion**:
    - **API**: Fetches live data from CoinPaprika.
    - **CSV**: Ingests historical data from CSV files.
    - **RSS**: Parses news feeds for sentiment analysis or updates.
- **Robust Orchestration**:
    - **Checkpointing**: Resumes from the last successful state in case of failure.
    - **Normalization**: Converts disparate data formats into a single `UnifiedData` schema.
    - **Audit Trail**: Stores raw data payloads in a `RawData` table for debugging and replayability.
- **Storage**: PostgreSQL database using `JSONB` for raw data and structured columns for unified data.
- **API**: FastAPI-based backend with:
    - Asynchronous ingestion triggering.
    - Rich filtering (source, symbol, pagination).
    - detailed execution statistics and comparison.
    - Health monitoring.

## Architecture
1.  **Ingestion Layer**: `ingestion/` contains source connectors (`api_source.py`, `csv_source.py`, `rss_source.py`).
2.  **Orchestrator**: `ingestion/orchestrator.py` manages the ETL workflow.
3.  **Service Layer**: `services/` handles database connections, monitoring, and checkpointing.
4.  **API Layer**: `api/` exposes endpoints.

## Setup & Deployment

### Prerequisites
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Configuration
Create a `.env` file in the root directory (or use the defaults in `docker-compose.yml`):
```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=ingestion_db
DATABASE_URL=postgresql://user:password@db:5432/ingestion_db
COINPAPRIKA_API_URL=https://api.coinpaprika.com/v1
COIN_IDS=["btc-bitcoin", "eth-ethereum"]
API_KEY=your_secure_api_key_here
```

### Running the System
The project includes a `Makefile` for common operations.

1.  **Start the System**:
    ```bash
    make up
    ```
    This builds the Docker image and starts the API (port 8000) and Database (port 5432).

2.  **Stop the System**:
    ```bash
    make down
    ```

3.  **Run Tests**:
    ```bash
    make test
    ```

4.  **Clean Builds**:
    ```bash
    make clean
    ```

### Manual Deployment
If you prefer not to use Make:
```bash
docker-compose up --build -d
```

## API Reference

### Authentication
All endpoints (except health) require an `x-api-key` header.
Default Key (dev): `test-api-key`

### Endpoints

#### 1. Trigger Ingestion
**POST** `/api/v1/ingest`
Triggers the ETL process in the background.
- **Response**: `202 Accepted`

#### 2. Retrieve Data
**GET** `/api/v1/data`
- **Params**:
    - `skip`: Offset (default 0)
    - `limit`: Max records (default 100)
    - `symbol`: Filter by coin symbol (e.g., `btc`, `eth`)
    - `source`: Filter by source (e.g., `coinpaprika`)
- **Response**: JSON list of unified data points.

#### 3. View Job Stats
**GET** `/api/v1/stats`
See history of ETL runs (success/failure, items processed).

#### 4. Compare Runs
**GET** `/api/v1/compare-runs`
- **Params**: `run_id_1`, `run_id_2`
- **Response**: Diff of items processed and errors between two specific runs.

#### 5. Health Check
**GET** `/api/v1/health`
Returns database connectivity status and last ETL run time.

