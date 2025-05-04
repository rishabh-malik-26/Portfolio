
import time
import joblib
import streamlit as st
from utils import main,validate_and_convert
import numpy as np

st.title("Phishing URL Detection")
st.write("This is a best phishing URL detection system")

model = joblib.load("phishing_detection_model.pkl")

url_input = st.text_input(label="Enter URL", placeholder="https://www.google.com")
if st.button("Check"):
    if url_input:
        url = validate_and_convert(url_input)
        with st.spinner("Checking..."):
            
            features = main(url)
            input_data = np.reshape(features, (1, -1))
            prediction = model.predict(input_data)
            time.sleep(1.5)

        result = "Phishing ⚠️" if prediction == 1 else "Legitimate ✅"
        st.success(f"The URL is: {result}")
    else:
        st.warning("Please enter a valid URL.")

