from dotenv import load_dotenv
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import xgboost as xgb
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env

app = FastAPI()
model = None

# Pydantic model for input validation
class PenguinData(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

def load_model():
    """Load the XGBoost model from Google Cloud Storage."""
    try:
        # Get credentials path from environment variable
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        logger.info(f"Environment variable GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
        
        # Log all environment variables for debugging
        env_vars = {k: v for k, v in os.environ.items() if "CREDENTIALS" in k}
        logger.info(f"All credentials-related environment variables: {env_vars}")
        
        # Fallback to default path if unset or incorrect
        if not credentials_path or not os.path.exists(credentials_path):
            credentials_path = "C:\\Users\\dosid\\secure-keys\\sa-key.json"
            logger.warning(f"GOOGLE_APPLICATION_CREDENTIALS unset or invalid, using fallback: {credentials_path}")
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Service account key file not found at {credentials_path}")
        
        logger.info(f"Loading credentials from: {credentials_path}")
        client = storage.Client.from_service_account_json(credentials_path)
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        blob_name = os.getenv("GCS_BLOB_NAME")
        
        if not bucket_name or not blob_name:
            raise ValueError("GCS_BUCKET_NAME or GCS_BLOB_NAME not set in .env")
        
        logger.info(f"Accessing bucket: {bucket_name}, blob: {blob_name}")
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename("model.json")
        
        # Load XGBoost model
        model = xgb.Booster()
        model.load_model("model.json")
        logger.info("Model loaded successfully from GCS")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from GCS: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    """Load the model when the FastAPI app starts."""
    global model
    model = load_model()

@app.post("/predict")
async def predict(data: PenguinData):
    """Make a prediction using the XGBoost model."""
    try:
        # Convert input data to DMatrix for XGBoost
        input_data = [[
            data.bill_length_mm,
            data.bill_depth_mm,
            data.flipper_length_mm,
            data.body_mass_g
        ]]
        dmatrix = xgb.DMatrix(input_data)
        
        # Make prediction
        prediction = model.predict(dmatrix)
        
        # Map prediction to class labels
        class_labels = ["Adelie", "Chinstrap", "Gentoo"]
        predicted_class = class_labels[int(np.argmax(prediction[0]))]
        
        return {"prediction": predicted_class}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")