# 🛒 Hybrid Product Recommender System

A production-grade product recommendation engine combining **content-based filtering** and **collaborative filtering**. The system is designed to deliver relevant product suggestions to both new and returning users, simulating a real-world e-commerce recommendation pipeline.

---

## 🚀 Features

- **Hybrid Recommendation** using:
  - `Word2Vec` embeddings for content-based similarity
  - `SVD` (Singular Value Decomposition) for collaborative filtering
- **Large-scale pipeline** using vector DB (**Qdrant**) and caching with **Redis**
- Fast and modular **Flask API** for serving recommendations
- Frontend simulation using **HTML, CSS, and JavaScript**
- Infrastructure containerized with **Docker**
- Built-in support for future **Kafka-based streaming** for real-time personalization

---

## 📦 Tech Stack

| Component                 | Technology Used                      |
|--------------------------|--------------------------------------|
| Embeddings               | Gensim Word2Vec                      |
| Collaborative Filtering  | Surprise SVD                         |
| Vector Database          | Qdrant                               |
| Backend APIs             | Flask                                |
| Caching Layer            | Redis                                |
| Database                 | PostgreSQL                           |
| Event Streaming (Planned)| Kafka                                |
| Frontend                 | HTML, CSS, JS                        |
| Containerization         | Docker                               |

---



## 📈 Dataset Used

- **Source**: [Amazon Reviews Dataset](https://nijianmo.github.io/amazon/index.html)
- **Category**: Appliances  
- Contains over **1M+ products**, user ratings, reviews, and metadata.

---

## ⚙️ Project Workflow

### 🔹 Content-Based Pipeline
1. Preprocess product names
2. Generate Word2Vec embeddings
3. Store embeddings in Qdrant
4. Retrieve top-N similar products
5. Cache results in Redis for fast access

### 🔹 Collaborative Filtering Pipeline
1. Build user-item matrix
2. Train SVD model using Surprise
3. Generate top-N product recommendations per user
4. Cache in Redis via Qdrant for quick lookup

---

## ❗ Challenges Faced

- Sparse user-item matrix affecting collaborative model quality
- Difficulty mimicking real-world infrastructure with limited resources
- No live user activity for A/B testing and active user targeting

---

## ✅ Problems Solved

- Tackled cold-start problem for new users with content-based filtering
- Delivered personalized recommendations for existing users
- Created a scalable, modular system simulating real-world recommendation architecture

---

## 🔮 Future Enhancements

- Integrate **Kafka** for real-time event tracking and dynamic personalization
- Add **Visual Search** using image embeddings
- Upgrade to **Two-Tower Neural Networks** or integrate **LLMs** for smarter ranking
- Add user interaction logging and feedback-based learning



