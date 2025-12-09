import requests
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = os.getenv("PORT", "8000")
API_URL = f"http://localhost:{PORT}/api/v1"
API_KEY = os.getenv("API_KEY", "secret-key")

def trigger_ingestion():
    max_retries = 5
    for i in range(max_retries):
        try:
            logger.info(f"Attempting to trigger ingestion (Attempt {i+1}/{max_retries})...")
            response = requests.post(
                f"{API_URL}/ingest",
                headers={"X-API-Key": API_KEY}
            )
            if response.status_code == 202:
                logger.info("Ingestion triggered successfully.")
                return
            else:
                logger.warning(f"Failed to trigger ingestion: {response.status_code} {response.text}")
        except Exception as e:
            logger.warning(f"Connection failed: {e}")
        
        time.sleep(5)
    logger.error("Could not trigger ingestion after multiple attempts.")

if __name__ == "__main__":
    # Wait for API to be ready
    time.sleep(5)
    trigger_ingestion()
