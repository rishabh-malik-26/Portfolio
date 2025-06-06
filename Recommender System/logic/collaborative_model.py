import pandas as pd 
import numpy as np
import json
import gzip
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
from posgres import * 
from qdrant import *
import logging
from redis_setup import r1

logging.basicConfig(
    level=logging.INFO,   
    format='%(asctime)s - %(levelname)s - %(message)s')


def model_training():
    try:

        reviews_db= User_review_DB(db)
        logging.info("Database connected for collaborative Model Training")
        
        try:
            data = reviews_db.model_data()
            logging.info("Data Received")
        except Exception as e:
            logging.info(f"Data couldn't fetched{e}")
            return None
        
    except Exception as e:
        logging.info(f"Database connection errro:{e}")


    df = pd.DataFrame(data)
    df = df.dropna()
    # df = df.iloc[0:100]
    logging.info("Data converted to df")

    # # Define the format
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df, reader)
    logging.info("Dataset Loaded")

    # # Train-test split
    trainset, testset = train_test_split(data, test_size=0.2)
    logging.info("Data Splitted")

    # # Train SVD model
    model = SVD()
    model.fit(trainset)
    logging.info("Model initiated and fitted")

    # # Predict and evaluate
    predictions = model.test(testset)
    logging.info(f"RMSE:{accuracy.rmse(predictions)}")

    user_matrix = model.pu
    item_matrix = model.qi 

    user_ids = [trainset.to_raw_uid(i) for i in range(user_matrix.shape[0])]
    item_ids = [trainset.to_raw_iid(j) for j in range(item_matrix.shape[0])]

    user_latent_df = pd.DataFrame(user_matrix,index =user_ids)
    item_latent_df = pd.DataFrame(item_matrix,index=item_ids)
   
    # return item_latent_df

    try:
        vec_points = [
            PointStruct(id=str(idx), vector=row.tolist())
            for idx, row in user_latent_df.iterrows()
        ]
        logging.info(f"User latent factors to vectors ")        
        try:
            qd.add_bulk_vectors(collection_name='user_latent',batch_size= 1000,cores=4,points=vec_points)
            logging.info("User Vectors added to Qdrant successfully")

        except Exception as e:
            logging.error(f"Error adding vectors to Qdrant: {e}")

    except Exception as e:
        logging.info(f"Error converting user_df to vectors {e}")


    # try:
    #     vec_points_item = [
    #         PointStruct(id=int(idx), vector=row.tolist())
    #         for idx, row in item_latent_df.iterrows()
    #     ]
    #     logging.info(f"Item latent factors to vectors ")

    #     try:
    #         qd.add_bulk_vectors(collection_name='item_latent',batch_size= 1000,cores=4,points=vec_points_item)
    #         logging.info("Item Vectors added to Qdrant successfully")
    #     except Exception as e:
    #         logging.error(f"Error adding item vectors to Qdrant: {e}")

    # except Exception as e:
    #     logging.info(f"Error converting item_df to vectors {e}")


# model_training()


user_ids = qd.ids_for_collaborative()


batch_size = 1000

batches = [user_ids[i:i+batch_size] for i in range(0, len(user_ids), batch_size)]


def find_item_similarity(batch_id):
    try:
        single_batch = batches[batch_id]

        user_vectors = qd.retreve(collection_name='user_latent', ids=single_batch, with_vectors=True)


        if isinstance(user_vectors, str):
            logging.error(f"Error from retreve API: {user_vectors}")
            return []

        if not user_vectors:
            logging.warning(f"No vectors found for batch {batch_id}")
            return []

        search_users = []
        for i, vector_obj in enumerate(user_vectors):
                if hasattr(vector_obj, 'vector'):
                    search_users.append(SearchRequest(vector=vector_obj.vector, limit=5))
                else:
                    logging.error(f"Vector object at index {i} has no vector attribute: {type(vector_obj)}")

        if not search_users:
            logging.warning(f"No valid search products for batch {batch_id}")
            return []


        similar_vectors = qd.batch_search(collection_name='item_latent', product_ids=search_users)

        if isinstance(similar_vectors, str):
            logging.error(f"Error from batch_search API: {similar_vectors}")
            return []
        
        output  = []
        for user_id,sim_points in zip(single_batch, similar_vectors):
            if isinstance(sim_points, str):
                recommendations = []
            elif sim_points and hasattr(sim_points, '__iter__'):
                recommendations = []
                for point in sim_points:
                        if hasattr(point, 'id') and hasattr(point, 'score'):
                            recommendations.append({"id": point.id, "score": point.score})
                        else:
                            logging.error(f"Point object missing id/score: {type(point)}")
            else:
                return []

            output.append({
                    "user_id": user_id,
                    "recommendations": recommendations
                })

        logging.info(f"Successfully processed batch {batch_id}")
        return output
    except Exception as e:
        logging.error(f"Error processing batch {batch_id}: {e}")
        return []



with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(find_item_similarity,range(len(batches))))
    


def store_bulk_batch(batch_data, redis_batch_size):
    """Store data in Redis using batched pipelines"""
    pipe = r1.pipeline()
    count = 0
    
    for data in batch_data:
        user_id = data['user_id']
        recommendations = data['recommendations']
        pipe.set(f"product:{user_id}", json.dumps(recommendations))
        count += 1
    
        # Execute pipeline when batch size is reached
        if count >= redis_batch_size:
            pipe.execute()
            pipe = r1.pipeline()  # Reset pipeline
            count = 0
    
    # Execute remaining items in pipeline
    if count > 0:
        pipe.execute()



for batch_result in results:
    store_bulk_batch(batch_result,redis_batch_size=2000)
    logging.info(f"Stored batch of {len(batch_result)} products to Redis")




# print(results[0:2])

# search_products = [SearchRequest(vector=i[0][1].vector, limit=5) for i in user_ids]
# user_ids[0][1].vector
# print(type(search_products))
# print(type(user_ids))
# print(user_ids[0][1].vector)

# print(user_ids)

# for i in  user_ids:
#     print(i[0])
# similar_vectors = qd.batch_search(collection_name='item_latent',product_ids=search_products)


# print(similar_vectors[100])

# user_vecs = qd.ids_for_collaborative()
# user_vecs = qd.scroll_data(collection_name='user_latent',limit=5,with_vectors=True)
# batch_size = 500

# batches = [user_vecs[i:i+batch_size] for i in range(0, len(user_vecs), batch_size)]

# search_requests = [
#         SearchRequest(
#             vector=user.vector, 
#             limit=5,
#             with_payload=True  # Include metadata if needed
#         ) 
#         for user in user_vecs
#     ]

# print(search_requests)


# user_vecs = qd.ids_for_collaborative()
# batch_size = 1000

# batches = [user_vecs[i:i+batch_size] for i in range(0, len(user_vecs), batch_size)]

# def find_similar_latent_products(batch_id):
    
#     single_batch = batches[batch_id]
#     logging.info(f"Processing batch {batch_id} with {len(single_batch)} products")

#     # search_products = [SearchRequest(vector=i.vector, limit=5) for i in single_batch]
#     search_requests = [
#         SearchRequest(
#             vector=user.vector, 
#             limit=5,
#             with_payload=True  # Include metadata if needed
#         ) 
#         for user in single_batch
#     ]


#     similar_vectors = qd.batch_search(collection_name='item_latent',product_ids=search_requests)
# # 
#     batch_results = {}
    
#     for i, user in enumerate(single_batch):
#         user_id = user.id  # Assuming user object has an id attribute
#         similar_items = similar_vectors[i]  # Results for this user
        
#         # Extract similar item IDs
#         similar_item_ids = [item.id for item in similar_items]
#         batch_results[user_id] = similar_item_ids
        
#         logging.debug(f"User {user_id} -> Similar items: {similar_item_ids}")
    
#     return batch_results


# with ThreadPoolExecutor(max_workers=8) as executor:
#     results = list(executor.map(find_similar_latent_products,range(len(batches))))

# print(results)



# OPTIMAL_BATCH_SIZE = 1000  # Larger batches for better throughput
# MAX_WORKERS = 8  # Adjust 
# user_vecs = qd.ids_for_collaborative()
# logging.info(f"Loaded {len(user_vecs)} user vectors")



# import logging
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import List, Dict, Any
# import numpy as np
# from collections import defaultdict

# # Debug function to check batch_search return format
# def debug_batch_search_format():
#     """
#     Debug function to understand the exact format returned by batch_search
#     """
#     # Take a small sample for testing
#     sample_users = user_vecs[:2]  # Just 2 users for testing
    
#     search_requests = [
#         SearchRequest(vector=user.vector, limit=3, with_payload=False)
#         for user in sample_users
#     ]
    
#     try:
#         results = qd.batch_search(
#             collection_name='item_latent',
#             product_ids=search_requests
#         )
        
#         print(f"batch_search return type: {type(results)}")
#         print(f"Number of results: {len(results)}")
        
#         if len(results) > 0:
#             print(f"First result type: {type(results[0])}")
#             print(f"First result: {results[0]}")
            
#             if len(results[0]) > 0:
#                 print(f"First item type: {type(results[0][0])}")
#                 print(f"First item: {results[0][0]}")
#                 print(f"First item attributes: {dir(results[0][0])}")
                
#                 # Try different attribute access patterns
#                 first_item = results[0][0]
#                 if hasattr(first_item, 'id'):
#                     print(f"Item ID via .id: {first_item.id}")
#                 if hasattr(first_item, 'point'):
#                     print(f"Item has .point attribute: {first_item.point}")
#                     if hasattr(first_item.point, 'id'):
#                         print(f"Item ID via .point.id: {first_item.point.id}")
#                 if hasattr(first_item, 'payload'):
#                     print(f"Item payload: {first_item.payload}")
                    
#     except Exception as e:
#         print(f"Debug error: {str(e)}")
#         import traceback
#         traceback.print_exc()

# # Call this function first to understand the format
# print("=== DEBUGGING BATCH SEARCH FORMAT ===")
# debug_batch_search_format()
# print("=" * 50)

# # Get user vectors (consider caching this if called frequently)
# # user_vecs = qd.ids_for_collaborative()

# # Create larger batches for better efficiency

# # batches = [user_vecs[i:i+OPTIMAL_BATCH_SIZE] for i in range(0, len(user_vecs), OPTIMAL_BATCH_SIZE)]
# # logging.info(f"Created {len(batches)} batches of size ~{OPTIMAL_BATCH_SIZE}")

# # def find_similar_latent_products_optimized(batch_id: int) -> Dict[str, List[str]]:
# #     """
# #     Optimized batch processing with debugging and flexible result handling
# #     """
# #     single_batch = batches[batch_id]
#     batch_size = len(single_batch)
    
#     logging.info(f"Processing batch {batch_id} with {batch_size} users")
    
#     # Pre-allocate search requests list for better memory efficiency
#     search_requests = []
#     user_ids = []  # Keep track of user IDs separately for faster access
    
#     # Build requests and user ID list in single pass
#     for user in single_batch:
#         search_requests.append(SearchRequest(
#             vector=user.vector,
#             limit=5,
#             with_payload=False  # Disable payload for faster search unless needed
#         ))
#         user_ids.append(user.id)
    
#     try:
#         # Batch search with optimized parameters
#         similar_vectors = qd.batch_search(
#             collection_name='item_latent',
#             product_ids=search_requests
#         )
        
#         # Debug: Check the structure of the first result
#         if batch_id == 0 and len(similar_vectors) > 0:
#             logging.info(f"Debug - similar_vectors type: {type(similar_vectors)}")
#             logging.info(f"Debug - similar_vectors[0] type: {type(similar_vectors[0])}")
#             if len(similar_vectors[0]) > 0:
#                 logging.info(f"Debug - similar_vectors[0][0] type: {type(similar_vectors[0][0])}")
#                 logging.info(f"Debug - similar_vectors[0][0] content: {similar_vectors[0][0]}")
        
#         # Flexible result construction to handle different return formats
#         batch_results = {}
        
#         for i in range(batch_size):
#             user_id = user_ids[i]
#             similar_items = similar_vectors[i]
            
#             # Handle different possible formats
#             if isinstance(similar_items, list):
#                 # Check if items have .id attribute or are already strings/IDs
#                 if len(similar_items) > 0:
#                     first_item = similar_items[0]
#                     if hasattr(first_item, 'id'):
#                         # Standard Qdrant point objects
#                         similar_item_ids = [item.id for item in similar_items]
#                     elif hasattr(first_item, 'point'):
#                         # Some Qdrant versions return ScoredPoint with .point.id
#                         similar_item_ids = [item.point.id for item in similar_items]
#                     elif isinstance(first_item, (str, int)):
#                         # Already IDs
#                         similar_item_ids = [str(item) for item in similar_items]
#                     else:
#                         # Try to convert to string as fallback
#                         logging.warning(f"Unexpected item type: {type(first_item)}, converting to string")
#                         similar_item_ids = [str(item) for item in similar_items]
#                 else:
#                     similar_item_ids = []
#             else:
#                 logging.warning(f"Unexpected similar_items type: {type(similar_items)}")
#                 similar_item_ids = []
            
#             batch_results[user_id] = similar_item_ids
        
#         logging.info(f"Completed batch {batch_id} successfully")
#         return batch_results
        
#     except Exception as e:
#         logging.error(f"Error in batch {batch_id}: {str(e)}")
#         return {}

# def process_all_batches_parallel():
#     """
#     Process all batches in parallel with optimized thread management
#     """
#     all_results = {}
    
#     # Use optimal number of workers based on system and Qdrant capacity
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         # Submit all tasks
#         future_to_batch = {
#             executor.submit(find_similar_latent_products_optimized, batch_id): batch_id 
#             for batch_id in range(len(batches))
#         }
        
#         # Process completed tasks as they finish (faster than waiting for all)
#         for future in as_completed(future_to_batch):
#             batch_id = future_to_batch[future]
#             try:
#                 batch_results = future.result()
#                 all_results.update(batch_results)
#                 logging.info(f"Completed batch {batch_id}, total results: {len(all_results)}")
#             except Exception as e:
#                 logging.error(f"Batch {batch_id} failed: {str(e)}")
    
#     return all_results

# # Alternative: Memory-efficient streaming approach for very large datasets
# def process_batches_streaming(redis_client=None, chunk_size=4):
#     """
#     Process batches in chunks to manage memory usage for very large datasets
#     """
#     total_results = 0
    
#     # Process batches in smaller chunks to avoid memory issues
#     for chunk_start in range(0, len(batches), chunk_size):
#         chunk_end = min(chunk_start + chunk_size, len(batches))
#         chunk_batch_ids = range(chunk_start, chunk_end)
        
#         logging.info(f"Processing chunk: batches {chunk_start} to {chunk_end-1}")
        
#         with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(chunk_batch_ids))) as executor:
#             chunk_results = list(executor.map(find_similar_latent_products_optimized, chunk_batch_ids))
        
#         # Combine results and optionally store in Redis immediately
#         for batch_results in chunk_results:
#             total_results += len(batch_results)
            
#             # Optional: Store in Redis immediately to free memory
#             if redis_client:
#                 pipeline = redis_client.pipeline()
#                 for user_id, similar_items in batch_results.items():
#                     pipeline.set(f"user_similar_items:{user_id}", 
#                                ','.join(similar_items))  # More memory efficient than JSON
#                 pipeline.execute()
        
#         logging.info(f"Completed chunk, total processed: {total_results}")
    
#     return total_results

# # Usage examples:
# if __name__ == "__main__":
#     import time
    
#     # Method 1: Fast parallel processing (for moderate datasets)
#     start_time = time.time()
#     results = process_all_batches_parallel()
#     end_time = time.time()
    
#     print(f"Processed {len(results)} users in {end_time - start_time:.2f} seconds")
#     print(f"Sample results: {dict(list(results.items())[:3])}")
    
#     # Method 2: Memory-efficient streaming (for very large datasets)
#     # total_processed = process_batches_streaming(redis_client)
#     # print(f"Streamed {total_processed} user recommendations to Redis")

# # Your original approach (optimized):
# def quick_parallel_execution():
#     """Your original approach but with optimizations"""
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         # Use list() only at the end, let executor manage the work
#         futures = [executor.submit(find_similar_latent_products_optimized, i) 
#                   for i in range(len(batches))]
        
#         results = []
#         for future in as_completed(futures):
#             try:
#                 results.append(future.result())
#             except Exception as e:
#                 logging.error(f"Future failed: {str(e)}")
#                 results.append({})  # Empty dict for failed batch
    
#     return results

# quick_parallel_execution()




