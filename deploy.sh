
# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="ingestion-api"
DB_INSTANCE_NAME="ingestion-db"
DB_PASSWORD="your-db-password"

echo "Deploying to GCP Project: $PROJECT_ID"

# 1. Build and Push Image
echo "Building and pushing Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 2. Create Cloud SQL Instance (if not exists)
# echo "Creating Cloud SQL instance..."
# gcloud sql instances create $DB_INSTANCE_NAME --database-version=POSTGRES_15 --cpu=1 --memory=4GB --region=$REGION --root-password=$DB_PASSWORD

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://postgres:$DB_PASSWORD@/postgres?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME" \
  --set-env-vars "API_KEY=secret-key" \
  --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME

# 4. Create Cloud Scheduler Job
echo "Creating Cloud Scheduler job..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

gcloud scheduler jobs create http ingestion-trigger \
  --schedule "0 * * * *" \
  --uri "$SERVICE_URL/api/v1/ingest" \
  --http-method POST \
  --headers "X-API-Key=secret-key" \
  --location $REGION

echo "Deployment Complete!"
echo "Service URL: $SERVICE_URL"
