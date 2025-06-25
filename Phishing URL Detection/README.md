# 🛡️ Phishing URL Detection Using Machine Learning

A machine learning-based binary classifier designed to detect phishing URLs using handcrafted lexical and structural features. The project includes a complete workflow from feature engineering to deployment, with real-time predictions and SHAP-based model interpretability.

---

## 🚀 Features

- Detects phishing vs. legitimate URLs using ML models
- Hand-engineered features such as URL entropy, length, digit/char ratio
- Final model built using **XGBoost** for robustness
- **SHAP** visualizations to explain individual predictions
- Interactive UI built with **Streamlit**, deployed on Hugging Face Spaces
- REST API via **Flask** for backend serving

---

## 📦 Tech Stack

| Component             | Technology/Library                      |
|----------------------|------------------------------------------|
| Models               | Random Forest (initial), XGBoost (final) |
| Feature Extraction   | Pandas, NumPy, NLTK                      |
| Interpretability     | SHAP                                     |
| Model Serving        | Flask                                    |
| User Interface       | Streamlit                                |
| Deployment           | Hugging Face Spaces                      |

---

## 📊 Dataset

- Publicly available dataset with labeled URLs (phishing vs. legitimate)
- Contains structural and lexical patterns commonly found in real phishing attempts
- Labeled data used for binary classification task

---

## 🧠 Feature Engineering

- Extracted ~30 lexical and structural features from each URL:
  - **URL length, domain length, subdomain count**
  - **Entropy score**: randomness in URL structure
  - **Special character counts**: `@`, `-`, `.`, `//`, etc.
  - **Digit-to-character ratio**, use of **shortening services**
  - Presence of **IP addresses** instead of domain names
  - **Suspicious keywords** (e.g., login, confirm, secure)
- Normalized features and applied log scaling where necessary

---

## 📈 Performance Metrics

| Metric                   | Value          |
|--------------------------|----------------|
| Accuracy                 | ~90%           |
| Recall (Legitimate URLs) | 0.94           |
| Recall (Phishing URLs)   | 0.73           |
| Precision                | Balanced       |
| F1 Score                 | Stable across thresholds |

---

## 🔍 Model Insights

- Initial overfitting due to high-leakage features (`has_https`, `has_www`) — removed them for generalization
- Fine-tuning **Random Forest** showed limited gains → switched to **XGBoost**
- Explored threshold tuning (starting from 0.22), but recall and F1 remained constant across precision ranges
- **SHAP** used to visualize and rank feature importance, aiding in debugging and decision explanation

---

## 🖥️ Interface & Deployment

- Built **Streamlit UI** to accept URL input and show predictions with confidence scores
- Integrated SHAP-based local explanation for individual results
- Deployed live app on **Hugging Face Spaces** for public testing

Project URL -- https://huggingface.co/spaces/rishabh2608/phishing-url-identification 
---

