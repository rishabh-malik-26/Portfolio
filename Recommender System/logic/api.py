import fastapi 
from fastapi import FastAPI,Body
from preprocessing import *
import logging
from gensim.models import Word2Vec
from fastapi.middleware.cors import CORSMiddleware
import requests
logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

# app = FastAPI()

# Allow all origins (in dev only


# logging.basicConfig(filename='logs.log',level= logging.INFO,
#                     format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/recommended")
# def recommendations(title:str,product_count: int=5):
#     logging.info("Data received")
#     recommended_products = get_similar_titles(title,limit=product_count)
#     logging.info("Similar products found")
#     return {"Products":recommended_products}

# @app.post('/receive-data')
# def receive_data(data: dict):
#     print(data)
#     return {"received": data}



@app.post('/recommend')
def recommendations(data: dict=Body(...)):

    # data = request.get_json()
    logging.info(f"Data received for recommendation:{data}")

    product_id = data['product_id']

    ### Content Based Model ###
    product_name = data['product_name']
    model = Word2Vec.load(r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\models\word2vec_model.model")
    logging.info(f"Model Loaded")
    
    procesed_text = preprocess(product_name)
    logging.info(f"Text Preprocessed {procesed_text}")

    title_tokens = tokens_to_vec(procesed_text,model=model)

    client = Qdrant()
    similar_titles = client.search("product_date",query_vector =title_tokens,limit = 5)
    all_titles = [{'id':title.id} for title in similar_titles]


    # headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json'
    #     }
        
    # response = requests.post(flask_url,json = {"similar_titles":all_titles},headers = headers)
    # if response.status_code == 200:
    #     logging.info("Successfully sent data to Flask API")
    # else:
    #     logging.error("Failed to send data to Flask API")

    return {"similar_titles":similar_titles}










