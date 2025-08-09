from dotenv import load_dotenv
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import storage
import xgboost as xgb
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env

app = FastAPI()
model = None

# Pydantic model for input validation with constraints
class PenguinData(BaseModel):
    bill_length_mm: float = Field(..., gt=0, description="Bill length in millimeters")
    bill_depth_mm: float = Field(..., gt=0, description="Bill depth in millimeters")
    flipper_length_mm: float = Field(..., gt=0, description="Flipper length in millimeters")
    body_mass_g: float = Field(..., gt=0, description="Body mass in grams")

# Feature names for XGBoost model
FEATURE_NAMES = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]

def load_model():
    """Load the XGBoost model from Google Cloud Storage or local file in test mode."""
    try:
        if os.getenv("TEST_MODE") == "1":
            model_path = "penguin_model.json"
            logger.info("Running in TEST_MODE, loading local model from penguin_model.json")
        else:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            logger.info(f"Environment variable GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
            
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
            model_path = "model.json"
            blob.download_to_filename(model_path)
        
        # Load XGBoost model
        model = xgb.Booster()
        model.load_model(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
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
        if model is None:
            raise ValueError("Model not initialized")
        
        # Convert input data to DMatrix for XGBoost
        input_data = [[
            data.bill_length_mm,
            data.bill_depth_mm,
            data.flipper_length_mm,
            data.body_mass_g
        ]]
        dmatrix = xgb.DMatrix(input_data, feature_names=FEATURE_NAMES)
        
        # Make prediction
        prediction = model.predict(dmatrix)
        
        # Map prediction to class labels
        class_labels = ["Adelie", "Chinstrap", "Gentoo"]
        predicted_class = class_labels[int(np.argmax(prediction[0]))]
        
        return {"prediction": predicted_class}
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")