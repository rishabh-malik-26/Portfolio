from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct,SearchRequest,HnswConfigDiff,SearchParams
from concurrent.futures import ThreadPoolExecutor,as_completed
## Docker Command - docker start qdrant 
from typing import List, Dict, Any, Optional, Tuple
import time
from functools import lru_cache
import logging

class Qdrant():

    def __init__(self,host = "localhost", port=6333,timeout=60):
        try:
            self.client=QdrantClient(host=host,port=port,timeout=timeout)
        except Exception as e:
            raise ConnectionError(f"Qdrant Connection failed {e}")


    def create_collection(self,collection_name,vector_size):
        try:
            self.client.recreate_collection(
            collection_name = collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),)
        except Exception as e:
            return f"Error Creating Colletion: {e}"


    def add_vectors(self,collection_name,id,vector):

        try:
            self.client.upsert(
            collection_name=collection_name,
            points=[PointStruct(id = id,vector=vector)])
        except Exception as e:
            return f"Error adding vectors: {e}"


    def add_bulk_vectors(self, collection_name, batch_size, cores, points):
        try:
            # Split the points into batches
            batches = [points[i:i + batch_size] for i in range(0, len(points), batch_size)]
            
            print(f"Starting upload of {len(points)} points in {len(batches)} batches")
            
            def process_batch(batch_idx):
                batch = batches[batch_idx]
                try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=batch,
                        wait=True  # Change to True for debugging
                    )
                    print(f"Batch {batch_idx+1}/{len(batches)} uploaded successfully ({len(batch)} points)")
                    return len(batch)
                except Exception as e:
                    print(f"Batch {batch_idx+1}/{len(batches)} failed: {e}")
                    return 0
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=cores) as executor:
                results = list(executor.map(process_batch, range(len(batches))))
                
            total_uploaded = sum(results)
            print(f"Total points uploaded: {total_uploaded}/{len(points)}")
            
            return f"Successfully uploaded {total_uploaded} points to {collection_name}"
        except Exception as e:
            print(f"Overall upload process failed: {e}")
            return f"Error uploading data: {e}"
    
    def retreve(self,collection_name,ids,with_vectors= True):
        try:
            data = self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_payload=False,
                with_vectors=with_vectors)
            return data
        except Exception as e:
            return f"Error retreiving data: {e}"


    def search(self,collection_name,query_vector,limit,with_vectors):
        try:
            result = self.client.search(collection_name = collection_name,query_vector=query_vector,limit = limit ,with_vectors= with_vectors)
            return result
        except Exception as e:
            return f"Error searching vectors: {e}"


    def batch_search(self,collection_name,product_ids):
        try:
            result = self.client.search_batch(collection_name = collection_name,requests=product_ids)
            return result
        except Exception as e:
            return f"Error searching vectors: {e}"

    # def batch_search(self, collection_name, product_ids, hnsw_ef=128):
    #     try:
    #         # Add hnsw_ef to each request
    #         requests_with_params = []
    #         for req in product_ids:
    #             req["params"] = SearchParams(hnsw_ef=hnsw_ef)
    #             requests_with_params.append(req)

    #         result = self.client.search_batch(
    #             collection_name=collection_name,
    #             requests=requests_with_params
    #         )
    #         return result
    #     except Exception as e:
    #         return f"Error searching vectors: {e}"



    def scroll_data(self,collection_name,limit,with_vectors):
        try:
            result = self.client.scroll(collection_name=collection_name,
                                        limit=limit,with_vectors=with_vectors)
            return result
        except Exception as e:
            return f"Error scrolling vectors: {e}"


    def check_collections(self):
        try:
            result = self.client.get_collections()
            return result
        except Exception as e:
            return f"Error fetching collections: {e}"
        

    def delete_collect(self,collection_name):
        try:
            self.client.delete_collection(collection_name=collection_name)
        
        except Exception as e:
            return f"Error Deleting Collection: {e}" 
     
        
    def count_vecs(self,collection_name):
        collection_info  =self.client.get_collection(collection_name)
        print(collection_info)
        return collection_info.vectors_count

    
    def ids_for_pipeline(self):
        collection_name = "product_vectors"
        all_ids = []
        scroll_offset = None

        while True:
            response = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=None,
                limit=1000,  # adjust batch size as needed
                offset=scroll_offset,
                with_payload=False,
                with_vectors=False,
            )
            
            for point in response[0]:
                all_ids.append(point.id)

            if response[1] is None:
                break
            else:
                scroll_offset = response[1]

        return all_ids
        

    # def ids_for_collaborative(self):
    #         collection_name = "user_latent"
    #         all_ids = []
    #         scroll_offset = None

    #         while True:
    #             response = self.client.scroll(
    #                 collection_name=collection_name,
    #                 scroll_filter=None,
    #                 limit=1000,  # adjust batch size as needed
    #                 offset=scroll_offset,
    #                 with_payload=False,
    #                 with_vectors=False,
    #             )
                
    #             for point in response[0]:
    #                 all_ids.append(point.id)

    #             if response[1] is None:
    #                 break
    #             else:
    #                 scroll_offset = response[1]

    #         return all_ids
        
    def batch_search(self, collection_name: str, product_ids: List[SearchRequest]) -> List[Any]:
    # """Optimized batch search with error handling"""
        try:
            result = self.client.search_batch(
                collection_name=collection_name,
                requests=product_ids
            )
            return result
        except Exception as e:
            logging.error(f"Error in batch_search: {e}")
            return []

    def retrieve_vectors_batch(self, collection_name: str, ids: List[str], with_vectors: bool = True) -> List[Any]:
        """Optimized vector retrieval"""
        try:
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_vectors=with_vectors,
                with_payload=False  # Skip payload if not needed
            )
            return result
        except Exception as e:
            logging.error(f"Error retrieving vectors: {e}")
            return []

    def ids_for_collaborative(self, collection_name: str = "user_latent", batch_size: int = 5000) -> List[str]:
        """Optimized ID retrieval with larger batch sizes"""
        all_ids = []
        scroll_offset = None
        
        while True:
            try:
                response = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=None,
                    limit=batch_size,  # Increased from 1000 to 5000
                    offset=scroll_offset,
                    with_payload=False,
                    with_vectors=False,
                )
                
                # More efficient list extension
                all_ids.extend(point.id for point in response[0])
                
                if response[1] is None:
                    break
                scroll_offset = response[1]
                
            except Exception as e:
                logging.error(f"Error in scroll operation: {e}")
                break
                
        logging.info(f"Retrieved {len(all_ids)} user IDs")
        return all_ids



    # def ids_for_collaborative(self):
    #     collection_name = "user_latent"
    #     all_ids = []
    #     scroll_offset = None

    #     while True:
    #         response = self.client.scroll(
    #             collection_name=collection_name,
    #             scroll_filter=None,
    #             limit=3000,  # adjust batch size as needed
    #             offset=scroll_offset,
    #             with_payload=False,
    #             with_vectors=True,
    #         )
            
    #         for point in response[0]:
    #             all_ids.append(point)

    #         if response[1] is None:
    #             break
    #         else:
    #             scroll_offset = response[1]

    #     return all_ids
    

    # def ids_for_collaborative(self):
    #     collection_name = "user_latent"
    #     scroll_offset = None
    #     all_user_vectors = []
    #     while True:
    #         user_points = self.client.scroll(
    #                 collection_name=collection_name,
    #                 scroll_filter=None,
    #                 limit=1000,  # adjust batch size as needed
    #                 offset=scroll_offset,
    #                 with_payload=False,
    #                 with_vectors=True,
    #             )
    #         all_user_vectors.extend([(point.id, point.vector) for point in user_points[0]])
    #         if scroll_offset is None:
    #             break
    #     return all_user_vectors





# # collection_info = client.get_collection("your_collection_name")
# print(f"Number of vectors: {collection_info.vectors_count}")



qd = Qdrant()



# print(len(qd.ids_for_collaborative()))
# print(qd.scroll_data(collection_name='product_date',limit=5,with_vectors=True))
# print(qd.ids_for_pipeline())
# print(qd.check_collections())
# print(qd.count_vecs(collection_name='user_latent'))


print(qd.count_vecs(collection_name='user_latent'))
# print(qd.count_vecs(collection_name='item_latent'))
# print(qd.retreve(collection_name='user_latent',ids=['6cd2a264-c199-414f-9b35-137b1ddae8c9'],with_vectors=True))
# data = qd.retreve(collection_name='product_date',ids=[1],with_vectors=True)
# vec = data[0].vector
# print(data)

# d = {'product_id':data[0].id,'recommendations':[]}

# simi_vecs = qd.search(collection_name='product_date',query_vector=vec,limit=5,with_vectors=False)
# # dics = dict(simi_vecs)
# for point in simi_vecs:
#     vec_id = point.id             # ← This gives the ID
#     score = point.score 
#     vec_dict = {'id':vec_id,'score':score}
#     d['recommendations'].append(vec_dict)

# print(d)     


# print(qd.count_vecs("product_date"))

# print(qd.scroll_data(collection_name = 'product_date',limit=10))





