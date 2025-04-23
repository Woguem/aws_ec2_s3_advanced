import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
import xgboost 
from sklearn.svm import SVC
from sklearn.datasets import load_iris

def train_model(data_path, model_type="random_forest", save_path="iris_model.pkl"):
    # In a real application, you would load data from data_path
    # For now, we're using the built-in dataset as a fallback
    try:
        # Code to load data from the CSV would go here
        # For now, using the built-in dataset
        iris = load_iris()
        X, y = iris.data, iris.target   #type: ignore
    except Exception as e:
        print(f"Error loading data from {data_path}, using built-in dataset: {e}")
        iris = load_iris()
        X, y = iris.data, iris.target   #type: ignore

    if model_type == "random_forest":
        model = RandomForestClassifier()
    elif model_type == "svm":
        model = SVC(probability=True)
    elif model_type == "knn":
        model = KNeighborsClassifier()
    elif model_type == "xgboost":
        model = xgboost.XGBClassifier() 
    else:
        raise ValueError("Unsupported model type")

    model.fit(X, y)
    joblib.dump(model, save_path)
    return model

def load_model(model_path="iris_model.pkl"):
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        # If model doesn't exist, train a new one
        print(f"Model not found at {model_path}, training a new one...")
        return train_model(None, save_path=model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        # Return a default model
        return train_model(None, save_path=model_path)

def predict(model, input_data):
    input_array = np.array(input_data).reshape(1, -1)
    prediction = model.predict(input_array)[0]
    iris = load_iris()
    return iris.target_names[prediction] #type:ignore
