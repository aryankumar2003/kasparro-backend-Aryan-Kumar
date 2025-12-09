# Deployment Guide - Google Cloud Platform

This guide explains how to deploy the Data Ingestion System to Google Cloud Platform (GCP) using Cloud Run, Cloud SQL, and Cloud Scheduler.

## Prerequisites
1.  **GCP Project**: Create a new project in the Google Cloud Console.
2.  **gcloud CLI**: Install and authenticate the Google Cloud SDK.
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```
3.  **APIs Enabled**: Enable the following APIs:
    *   Cloud Run API
    *   Cloud SQL Admin API
    *   Cloud Build API
    *   Cloud Scheduler API

## Deployment Steps

### 1. Configure the Script
Open `deploy.sh` and update the configuration variables at the top:
*   `PROJECT_ID`: Your GCP Project ID.
*   `DB_PASSWORD`: A strong password for your database.

### 2. Run the Deployment Script
Run the script from your terminal (Git Bash or WSL on Windows):
```bash
bash deploy.sh
```

### 3. Verify Deployment
*   **Public API**: The script will output the Service URL. Visit `$SERVICE_URL/api/v1/health` to check status.
*   **Scheduled ETL**: Go to the Cloud Scheduler console to see the `ingestion-trigger` job. You can click "Run Now" to test it.
*   **Logs**: View logs in the Cloud Run console under the "Logs" tab.

## Manual Configuration (Optional)
If you prefer to deploy manually or need to troubleshoot:

1.  **Build Image**:
    ```bash
    gcloud builds submit --tag gcr.io/PROJECT_ID/ingestion-api
    ```

2.  **Deploy Cloud Run**:
    ```bash
    gcloud run deploy ingestion-api --image gcr.io/PROJECT_ID/ingestion-api --platform managed --allow-unauthenticated
    ```

3.  **Set Environment Variables**:
    Ensure `DATABASE_URL` and `API_KEY` are set in the Cloud Run revision settings.

## Generic Docker Deployment (VPS/EC2)
You can also deploy this image to any server with Docker installed.

1.  **Build & Push**:
    ```bash
    docker build -t your-username/ingestion-api .
    docker push your-username/ingestion-api
    ```

2.  **Run on Server**:
    ```bash
    # Run Database
    docker run -d --name db -e POSTGRES_PASSWORD=password postgres:15-alpine

    # Run App (Link to DB)
    docker run -d -p 80:8000 \
      --link db:db \
      -e DATABASE_URL=postgresql://postgres:password@db:5432/postgres \
      -e API_KEY=secret-key \
      your-username/ingestion-api
    ```
