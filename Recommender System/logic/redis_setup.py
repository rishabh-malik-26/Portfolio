import redis
import json
import logging

logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")



r = redis.Redis(host='localhost',port=6379,db = 0) # 0 has content recommendations
r1 = redis.Redis(host='localhost',port=6379,db = 1) # 1 has user recommendations

def store_recommendations(product_id,recommended_products):
    key = f"product:{product_id}"
    r.set(key,json.dumps(recommended_products))


def get_recommendations(product_id):
    key = f"product:{product_id}"
    raw_data = r.get(key)
    if raw_data is None:
        return [{'id': 1560, 'score': 1.0},
                 {'id': 76611, 'score': 0.9930348}, 
                 {'id': 42667, 'score': 0.9631963}, 
                 {'id': 4980, 'score': 0.9609887}, 
                 {'id': 39854, 'score': 0.9575501}]
        # return(f"No recommendations found in Redis for {product_id}")
    
    result  = json.loads(r.get(key))
    return result


def store_bulk(data):
    pipe = r.pipeline()
    for key, val in data.items():
        pipe.set(key, val) 
        pipe.execute()  


def store_user_recommendations(user_id,recommended_products):
    key = f"user:{user_id}"
    r1.set(key,json.dumps(recommended_products))


def store_bulk_user_recs(data):
    try:
        logging.info(f'{data} received')
        try:
            pipe = r1.pipeline()
            logging.info("Pipeline started")
            for key, val in data.items():
                logging.info(f'key:{key}, value: {val}')
                pipe.set(key, val) 
                pipe.execute()
                logging.info(f"User Id and it's recommendations added to redis ")
        except Exception as e:
            logging.info(f"Error initiating pipeline: {e}")
    except Exception as e:
        logging.info(f"Error retrieving data: {e}")



def get_user_recommendations(user_id):
    key = f"product:{user_id}"
    # raw_data = r.get(key)
    # if raw_data is None:
    #     return [{'id': 1560, 'score': 1.0},
    #              {'id': 76611, 'score': 0.9930348}, 
    #              {'id': 42667, 'score': 0.9631963}, 
    #              {'id': 4980, 'score': 0.9609887}, 
    #              {'id': 39854, 'score': 0.9575501}]
    #     # return(f"No recommendations found in Redis for {product_id}")
    
    result  = json.loads(r1.get(key))
    return result






