from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

def upload_model_to_gcs():
    """Upload the trained model to Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        blob_name = os.getenv("GCS_BLOB_NAME")
        model_path = "penguin_model.json"

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(model_path)
        
        print(f"Model successfully uploaded to gs://{bucket_name}/{blob_name}")
    except Exception as e:
        print(f"Failed to upload model: {str(e)}")

if __name__ == "__main__":
    upload_model_to_gcs()