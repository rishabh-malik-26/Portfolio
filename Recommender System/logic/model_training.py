import os 
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import gensim
from gensim.utils import simple_preprocess
import pandas as pd
from posgres import ProductsDB,db

import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")
stop_words = stopwords.words("english")

from qdrant import PointStruct,qd
import numpy as np
import logging
logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")


# from gensim.models import Word2Vec

## Preprocess text ##

# # def data_preprocessing():
# try:
#     # db = DBManager()
#     product_db= ProductsDB(db)
#     logging.info("Data base initialized")
# except Exception as e:
#     raise ConnectionError

# product_data = product_db.model_training_data()
# logging.info("Data Extracted from Database")

# df = pd.DataFrame(product_data,columns=['product_id','product_name'])
# logging.info(f'DataFrame Created')

# df['cleaned_text'] = df['product_name'].apply(lambda x: preprocess(str(x) if pd.notnull(x) else ""))
# logging.info("Data Processed")

# model = gensim.models.Word2Vec(df['cleaned_text'],min_count = 1)


# def tokens_to_vec(token_text, vector_size=100):
#     # Filter tokens in the model's vocabulary
#     valid_tokens = [token for token in token_text if token in model.wv]
    
#     # Handle empty valid_tokens gracefully
#     if not valid_tokens:
#         return np.zeros((1, vector_size))  # Return zero vector if no valid tokens
    
#     # Get embeddings for valid tokens
#     token_embeddings = model.wv[valid_tokens]
    
#     # Compute mean embedding
#     mean_embedding = np.mean(token_embeddings, axis=0)

#     return mean_embedding.tolist() 
    
# df['vecs'] = df['cleaned_text'].apply(lambda x: list(tokens_to_vec(x)))   
# logging.info("Tokens converted to vectors")

# vec_points = [
#     PointStruct(id=row['product_id'], vector=row['vecs'])
#     for row in df.to_dict('records')
# ]



# try:
#     qd = Qdrant()
#     qd.add_bulk_vectors(collection_name='product_date',batch_size= 500,cores=4,points=vec_points)
#     logging.info("Vectors added to Qdrant successfully")
# except Exception as e:
#     logging.error(f"Error adding vectors to Qdrant: {e}")


def preprocess(text):
    tokens = simple_preprocess(text,deacc= True)
    return [word for word in tokens if word not in stop_words]


def tokens_to_vec(token_text, model, vector_size=100):
    # Filter tokens in the model's vocabulary
    valid_tokens = [token for token in token_text if token in model.wv]
    
    # Handle empty valid_tokens gracefully
    if not valid_tokens:
        return np.zeros((1, vector_size))  # Return zero vector if no valid tokens
    
    # Get embeddings for valid tokens
    token_embeddings = model.wv[valid_tokens]
    
    # Compute mean embedding
    mean_embedding = np.mean(token_embeddings, axis=0)

    return mean_embedding.tolist() 


def main():

    try:
        product_db= ProductsDB(db)
        logging.info("Data base initialized")

        product_data = product_db.model_training_data()
        logging.info("Data Extracted from Database")

        df = pd.DataFrame(product_data,columns=['product_id','product_name'])
        logging.info(f'DataFrame Created')

        df['cleaned_text'] = df['product_name'].apply(lambda x: preprocess(str(x) if pd.notnull(x) else ""))
        logging.info("Data Processed")

        model = gensim.models.Word2Vec(df['cleaned_text'],min_count = 1)

        df['vecs'] = df['cleaned_text'].apply(lambda x: list(tokens_to_vec(x,model)))   
        logging.info("Tokens converted to vectors")

        vec_points = [
            PointStruct(id=row['product_id'], vector=row['vecs'])
            for row in df.to_dict('records')
        ]
  
        try:
            # qd = Qdrant()
            qd.add_bulk_vectors(collection_name='product_vectors',batch_size= 500,cores=4,points=vec_points)
            logging.info("Vectors added to Qdrant successfully")
        except Exception as e:
            logging.error(f"Error adding vectors to Qdrant: {e}")

    except Exception as e:
        raise ConnectionError


# import sys
# print(sys.path)

# def custom_search(query):

#     try:

#         preprocessed_query = preprocess(query)
#         logging.info("Query Processed")

#         model = Word2Vec.load(r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\models\word2vec_model.model")

#         query_vec = tokens_to_vec(preprocessed_query,model)   
#         # logging.info(f"Tokens converted to vectors: {query_vec}")

#         products= qd.search(collection_name = 'product_date',query_vector=query_vec,limit = 5 ,with_vectors= False)
#         logging.info(f"Searched Simialar Products:{products}")

#         product_ids = [i.id for i in products]

#         return product_ids

#     except Exception as e:
#         return f"Query Search Failed"


# qd = Qdrant()
# qd.add_bulk_vectors(collection_name='product_date',batch_size= 500,cores=4,points=vec_points)


# for index, row in df.iterrows():
#     qd.add_vectors(collection_name='products',id =row['product_id'],vector=row['vecs'])
    # logging.info("Data added to Qdrant")




# for index, row in df.iterrows():
#     qdrant_client.upsert(
#         collection_name='products',
#         points=[PointStruct(id=row['product_id'], vector=row['embedding'])]
#     )
# print(qd.count_vecs())






