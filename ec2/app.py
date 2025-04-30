import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(page_title="Iris Classifier 🌸", layout="centered")

# Sidebar for server input
st.sidebar.title("🔧 API Settings")
server_url = st.sidebar.text_input(
    "FastAPI Server URL (e.g. http://<public-ip>:8000)",
    value="http://localhost:8000"
)

# Verify server connection
try:
    response = requests.get(f"{server_url}")
    if response.status_code == 200:
        st.sidebar.success("✅ Connected to API server")

        # Display model info
        try:
            model_info = requests.get(f"{server_url}/model-info").json()
            st.sidebar.info(f"Model status: {model_info.get('status')}")
            if 'type' in model_info:
                st.sidebar.info(f"Model type: {model_info.get('type')}")
        except:
            st.sidebar.warning("⚠️ Could not fetch model info")
    else:
        st.sidebar.error("❌ Could not connect to API server")
except:
    st.sidebar.warning("⚠️ API server not reachable")

# Main UI
st.title("🌸 Iris Flower Classifier")
st.markdown("Predict the Iris flower species by entering the measurements below.")

# Spacing
st.markdown("---")

# Two-column layout for inputs
col1, col2 = st.columns(2)

with col1:
    sepal_length = st.slider("Sepal length (cm)", 4.0, 8.0, 5.4)
    petal_length = st.slider("Petal length (cm)", 1.0, 7.0, 1.3)
with col2:
    sepal_width = st.slider("Sepal width (cm)", 2.0, 4.5, 3.4)
    petal_width = st.slider("Petal width (cm)", 0.1, 2.5, 0.2)

# Predict Button
if st.button("🔍 Predict"):
    features = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width
    }

    try:
        with st.spinner('Predicting...'):
            response = requests.post(f"{server_url}/predict", json=features, timeout=10)

            if response.status_code == 200:
                result = response.json()
                st.success(f"🌼 Predicted species: **{result['prediction'].title()}**")
            else:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                except:
                    pass
                st.error(f"❌ API error (HTTP {response.status_code}): {error_detail}")

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the API server. Please check the URL and ensure the server is running.")
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The server might be overloaded.")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

# Data upload section (for admin)
with st.expander("Admin: Upload & Retrain"):
    uploaded_file = st.file_uploader("Upload new training data (CSV)", type=["csv"])

    if uploaded_file is not None:
        if st.button("Upload to Server"):
            try:
                files = {"file": uploaded_file}
                response = requests.post(f"{server_url}/upload-data", files=files)

                if response.status_code == 200:
                    st.success("✅ Data uploaded successfully")
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Upload error: {str(e)}")

    # Retrain model section
    st.subheader("Retrain Model")
    model_options = ["random_forest", "svm", "knn", "logreg"]
    selected_model = st.selectbox("Model type", model_options)

    if st.button("Retrain Model"):
        try:
            with st.spinner("Training in progress..."):
                response = requests.post(f"{server_url}/retrain?model_type={selected_model}")

                if response.status_code == 200:
                    st.success(f"✅ Model retrained successfully: {response.json()['status']}")
                else:
                    st.error(f"❌ Training failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Training error: {str(e)}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit and FastAPI by Yen Fred")
