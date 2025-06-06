from qdrant import qd
from qdrant_client.models import SearchRequest
import  json
from concurrent.futures import ThreadPoolExecutor
# from redis_setup import store_recommendations,get_recommendations
from posgres import db,ProductsDB
import pandas as pd
from redis_setup import r
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
# qd = Qdrant()

all_ids = qd.ids_for_pipeline()


# def get_data():

# #     try:
# #         product_db= ProductsDB(db)
# #         logging.info("Database connected")

# #         try:
# #             data = product_db.model_training_data()
# #             logging.info("Data Extracted from Database for content pipeline")

# #             df = pd.DataFrame(data,columns=['product_id','title'])
# #             logging.info("Pipeline data converted to Dataframe")

# #             all_ids = list(df['product_id'])
# #             logging.info("Extracted Product Ids from dataframe")

# #             return all_ids

# #         except Exception as e:
# #             return f"Error fetching data:{e}"

# #     except Exception as e:
# #         return f"Database connection error:{e}"


# # all_ids = get_data()

# batch_size = 5000

# batches = [all_ids[i :i+batch_size] for i in range(0,len(all_ids),batch_size)]


# def find_batch_similarity(batch_id):
#     try:
#         ## Batch 
#         single_batch = batches[batch_id]

#         # Vectors for which we need to find similar vectors
#         product_vectors = qd.retreve(collection_name='product_date',ids=single_batch,with_vectors=True)

#         if isinstance(product_vectors,str):
#             logging.info(f"Error from retreve API: {product_vectors}")
#             return []
 
#         # if not product_vectors:
#         #     logging.warning(f"No vectors found for batch {batch_id}")
#         #     return []

#         search_products = [SearchRequest(vector=i.vector, limit=5) for i in product_vectors]

#         similar_vectors = qd.batch_search(collection_name='product_date',product_ids=search_products)

#         # return similar_vectors
#         output = []
#         for product_id, sim_points in zip(single_batch, similar_vectors):
#             recommendations = [
#                 {"id": point.id, "score": point.score} for point in sim_points
#             ] if sim_points else []
#             output.append({
#                 "product_id": product_id,
#                 "recommendations": recommendations
#             })

#         return output
#     except Exception as e:
#         logging.error(f"Error processing batch {batch_id}: {e}")

# with ThreadPoolExecutor(max_workers=3) as executor:
#         result = list(executor.map(find_batch_similarity,range(len(batches))))




# def store_bulk_batch(batch_data, redis_batch_size=2000):
#     """Store data in Redis using batched pipelines"""
#     pipe = r.pipeline()
#     count = 0
    
#     for data in batch_data:
#         product_id = data['product_id']
#         recommendations = data['recommendations']
#         pipe.set(f"product:{product_id}", json.dumps(recommendations))
#         count += 1
        
#         # Execute pipeline when batch size is reached
#         if count >= redis_batch_size:
#             pipe.execute()
#             pipe = r.pipeline()  # Reset pipeline
#             count = 0
    
#     # Execute remaining items in pipeline
#     if count > 0:
#         pipe.execute()


# ## Data Added to Redis in batches
# for batch_result in result:
#     store_bulk_batch(batch_result, redis_batch_size=50)
#     logging.info(f"Stored batch of {len(batch_result)} products to Redis")



# def get_data():
#     try:
#         product_db = ProductsDB(db)
#         logging.info("Database connected")

#         try:
#             data = product_db.model_training_data()
#             logging.info("Data Extracted from Database for content pipeline")

#             df = pd.DataFrame(data, columns=['product_id', 'title'])
#             logging.info("Pipeline data converted to Dataframe")

#             all_ids = list(df['product_id'])
#             logging.info("Extracted Product Ids from dataframe")

#             return all_ids

#         except Exception as e:
#             return f"Error fetching data:{e}"

#     except Exception as e:
#         return f"Database connection error:{e}"


# all_ids = get_data()



batch_size = 500

batches = [all_ids[i:i+batch_size] for i in range(0, len(all_ids), batch_size)]


def find_batch_similarity(batch_id):
    try:
        ## Batch 
        single_batch = batches[batch_id]
        logging.info(f"Processing batch {batch_id} with {len(single_batch)} products")

        # Vectors for which we need to find similar vectors
        product_vectors = qd.retreve(collection_name='product_vectors', ids=single_batch, with_vectors=True)
        
        # Check if product_vectors is valid
        if isinstance(product_vectors, str):
            logging.error(f"Error from retreve API: {product_vectors}")
            return []
        
        if not product_vectors:
            logging.warning(f"No vectors found for batch {batch_id}")
            return []

        search_products = []
        for i, vector_obj in enumerate(product_vectors):
            if hasattr(vector_obj, 'vector'):
                search_products.append(SearchRequest(vector=vector_obj.vector, limit=5))
            else:
                logging.error(f"Vector object at index {i} has no vector attribute: {type(vector_obj)}")

        if not search_products:
            logging.warning(f"No valid search products for batch {batch_id}")
            return []

        similar_vectors = qd.batch_search(collection_name='product_vectors', product_ids=search_products)
        
        # Check if similar_vectors is valid
        if isinstance(similar_vectors, str):
            logging.error(f"Error from batch_search API: {similar_vectors}")
            return []

        # return similar_vectors
        output = []
        for product_id, sim_points in zip(single_batch, similar_vectors):
            if isinstance(sim_points, str):
                logging.error(f"sim_points is string: {sim_points}")
                recommendations = []
            elif sim_points and hasattr(sim_points, '__iter__'):
                recommendations = []
                for point in sim_points:
                    if hasattr(point, 'id') and hasattr(point, 'score'):
                        recommendations.append({"id": point.id, "score": point.score})
                    else:
                        logging.error(f"Point object missing id/score: {type(point)}")
            else:
                recommendations = []
                
            output.append({
                "product_id": product_id,
                "recommendations": recommendations
            })

        logging.info(f"Successfully processed batch {batch_id}")
        return output
    
    except Exception as e:
        logging.error(f"Error processing batch {batch_id}: {e}")
        return []


with ThreadPoolExecutor(max_workers=3) as executor:
    result = list(executor.map(find_batch_similarity, range(len(batches))))


def store_bulk_batch(batch_data, redis_batch_size=50):
    """Store data in Redis using batched pipelines"""
    pipe = r.pipeline()
    count = 0
    
    for data in batch_data:
        product_id = data['product_id']
        recommendations = data['recommendations']
        pipe.set(f"product:{product_id}", json.dumps(recommendations))
        count += 1
        
        # Execute pipeline when batch size is reached
        if count >= redis_batch_size:
            pipe.execute()
            pipe = r.pipeline()  # Reset pipeline
            count = 0
    
    # Execute remaining items in pipeline
    if count > 0:
        pipe.execute()


# Data Added to Redis in batches
for batch_result in result:
    store_bulk_batch(batch_result, redis_batch_size=2000)
    logging.info(f"Stored batch of {len(batch_result)} products to Redis")












# def store_bulk(data):
#     pipe = r.pipeline()
#     product_id = data['product_id']
#     recommendations = data['recommendations']
#     pipe.set(f"product:{product_id}", json.dumps(recommendations))

#     pipe.execute()  

## Data Added to 
# for i in (result):
#     for j in i:
#         store_bulk(j)



# recs = []

# for i in range(len(prodcuts[0])):
#     product_id = prodcuts[0][i].id
#     ## Extracted products ids from the 
        
#     data = qd.retreve(collection_name='product_date',ids=[product_id],with_vectors=True)
#     vec = data[0].vector

#     d = {'product_id':product_id,'recommendations':[]}

#     simi_vecs = qd.search(collection_name='product_date',query_vector=vec,limit=5,with_vectors=False)
#     # dics = dict(simi_vecs)
#     for point in simi_vecs:
#         vec_id = point.id             # ← This gives the ID
#         score = point.score 

#         vec_dict = {'id':vec_id,'score':score}
#         d['recommendations'].append(vec_dict)
#     recs.append(d)







