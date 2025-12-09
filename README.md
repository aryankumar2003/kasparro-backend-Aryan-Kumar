# Data Ingestion and API System

## Overview
This system ingests cryptocurrency data from CoinPaprika API and CSV files, normalizes it, stores it in PostgreSQL, and exposes it via a FastAPI backend.

## Design
- **Ingestion**: Modular sources (API, CSV) fetch data.
- **Orchestrator**: Coordinates ingestion, handles raw data storage (JSONB), and normalizes to a unified schema.
- **Storage**: PostgreSQL with `RawData` (audit trail) and `UnifiedData` (queryable) tables.
- **API**: FastAPI provides endpoints for data retrieval and system health.

## Setup
### Prerequisites
- Docker and Docker Compose

### Running the System
1. **Start**:
   ```bash
   make up
   ```
   The API will be available at `http://localhost:8000`.

2. **Stop**:
   ```bash
   make down
   ```

3. **Run Tests**:
   ```bash
   make test
   ```

## API Endpoints
- `POST /api/v1/ingest`: Trigger ingestion.
- `GET /api/v1/data`: Retrieve data (supports `skip`, `limit`, `symbol`, `source`).
- `GET /api/v1/health`: Check system health.
