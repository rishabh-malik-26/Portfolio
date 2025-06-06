import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import ast
import logging
logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'logic'))
# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(parent_dir)
# from .model_training import tokens_to_vec,preprocess


def custom_search(query):
    from logic.model_training import tokens_to_vec,preprocess
    # from logic.posgres import ProductsDB,db

    from gensim.models import Word2Vec
    from logic.qdrant import qd

    try:

        preprocessed_query = preprocess(query)
        logging.info("Query Processed")

        model = Word2Vec.load(r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\models\word2vec_model.model")

        query_vec = tokens_to_vec(preprocessed_query,model)   
        # logging.info(f"Tokens converted to vectors: {query_vec}")

        products= qd.search(collection_name = 'product_date',query_vector=query_vec,limit = 5 ,with_vectors= False)
        logging.info(f"Searched Simialar Products:{products}")

        product_ids = [i.id for i in products]

        return product_ids

    except Exception as e:
        return f"Query Search Failed"

# print(custom_search("grease filter"))

# print("hi")

def image_thumbnail(details):
    str_details = ast.literal_eval(details[0][4])
    image = str_details[0]['thumb']
    return image


def image_high_res(details):
    str_details = ast.literal_eval(details[0][4])
    image = str_details[0]['hi_res']
    return image


def clean_amazon_image_url(image_url):
    # Remove the ._AC_ or ._SX300_ or similar Amazon modifiers safely
    return re.sub(r'\._[^.]+_', '', image_url)



def get_generic_products():
    # from logic.model_training import db,ProductsDB

    from logic.posgres import ProductsDB,db
    product_db = ProductsDB(db)
    category_products = product_db.get_featured_products()
    logging.info(f"Category Products : {category_products}")
    products = []

    for i in range(len(category_products)):

        ids = category_products[i][0]
        logging.info(f"Product Id: {ids}")

        category_name= category_products[i][1]
        logging.info(f"Category Products: {category_name}")

        titles = category_products[i][2]
        logging.info(f"Title : {titles}")

        prices = category_products[i][3]
        logging.info(f"Price: {prices}")

        image_url = image_thumbnail([category_products[i]])
        logging.info(f"Image: {image_url}")
        
        dic = {'id':ids,'name':titles,'price':prices,'category':category_name,'image_url':image_url}
        logging.info(f"Dict of products:{dic}")

        products.append(dic)
    logging.info(f"Returned All products: {products}")
    return products

print(get_generic_products())

    # product_db = ProductsDB(db)
    # products = product_db.get_featured_products()

    # featured_products = []
    # for product in products:
    #     image_url = image_thumbnail([product])
    #     featured_products.append({
    #         'id': product[0],
    #         'name': product[2],
    #         'price': product[3],
    #         'category': product[1],
    #         'image_url': image_url
    #     })
    # return featured_products
# print(clean_amazon_image_url("https://m.media-amazon.com/images/I/219jqVVcnEL._AC_US75_.jpg"))