import os
import shutil
import joblib
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import our utility functions
from classifier import load_model, predict, train_model
from s3_utils import download_from_s3, upload_to_s3

counter_file = "compteur.txt"

def get_next_file_number():
    if os.path.exists(counter_file):
        # Read last counter number
        with open(counter_file, "r") as f:
            counter = int(f.read().strip())
    else:
        # If the file does not exist, it starts at 0
        counter = 0
    
    # Increment for next file
    next_number = counter + 1
    
    # Save new number
    with open(counter_file, "w") as f:
        f.write(str(next_number))
    
    return next_number

# Define the model path
MODEL_PATH = "iris_model.pkl"

# Load the trained model
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None  # We'll check this later and handle appropriately

# Define FastAPI app
app = FastAPI(title="Iris Classifier API")

# Request body schema
class IrisFeatures(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def read_root():
    return {"msg": "Iris classifier is up and running!"}

@app.post("/predict")
def predict_species(features: IrisFeatures):
    # Check if model is loaded
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please train or upload a model first.")

    input_data = [
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width,
    ]

    try:
        prediction = predict(model, input_data)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    file_location = "data.csv"
    try:
        # Save the uploaded file
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Upload to S3
        file_number = get_next_file_number()
        file_name = f"iris_data_{file_number}.csv"
        success = upload_to_s3(file_location, file_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload to S3")

        return {"status": "Uploaded to S3", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/retrain")
def retrain(model_type: str = "random_forest"):
    global model

    # Validate model type
    if model_type not in ["random_forest", "svm", "knn", "logreg"]:
        raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")

    try:
        # Try to download the latest data from S3
        data_path = "latest.csv"
        s3_download_success = download_from_s3("iris_data.csv", data_path)

        if not s3_download_success:
            print("Could not download from S3, using default dataset")

        # Train the model (if S3 download failed, the function will use the built-in dataset)
        model_path = f"{model_type}_model.pkl"
        model = train_model(data_path, model_type=model_type, save_path=model_path)

        # Update the global model reference
        model = load_model(model_path)

        return {"status": f"{model_type} model trained and loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

# Endpoint to check model status
@app.get("/model-info")
def model_info():
    if model is None:
        return {"status": "No model loaded"}

    # Get basic info about the model
    model_type = type(model).__name__
    return {
        "status": "Model loaded",
        "type": model_type
    }
