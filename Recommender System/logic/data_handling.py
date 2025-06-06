
import json
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import psycopg2
import gzip
import csv
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

filepath = r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\product_data\Appliances\meta_Appliances.jsonl"
output_file = r'logic\products.csv'

review_file = r"C:\Users\Rishabh\Desktop\Python New\Amazon Recommender System\product_data\Appliances\Appliances.jsonl"

# def jsonl_to_df(file_path):
#     try:
#         all_data = []
#         with gzip.open(file_path,"rt", encoding="utf-8") as file:
#             for line in file:
#                 data_line = json.loads(line.strip())
#                 all_data.append(data_line)
#             df = pd.DataFrame(all_data)
#         return df.iloc[0:100]
#     except Exception as e:
#         return f"Error Occuerd: {e}"

# new_Df = jsonl_to_df(filepath)



# def jsonl_to_csv(file_path,output_csv):
#     try:
#         with open(file_path,"r", encoding="utf-8") as file, open (output_csv,'w',newline="",encoding="utf-8", errors="ignore") as csv_file:
#             writer = None
#             for line in file:
#                 try:
#                     data_line = json.loads(line.strip())
#                     if writer is None:
#                         writer = csv.DictWriter(csv_file,fieldnames=data_line.keys())
#                         writer.writeheader()
#                     writer.writerow(data_line)
#                 except json.JSONDecodeError as json_error:
#                     print('JSONDecodeError')
#         logging.info(f"JSONL file successfully converted to CSV: {output_csv}")
#     except Exception as e:
#         return f"Error Occuerd: {e}"

# jsonl_to_csv(filepath,output_file)



# import json
# import csv
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def jsonl_to_csv(file_path, output_csv):
    """
    Converts a JSONL file to a CSV file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file, open(output_csv, "w", newline="",encoding="utf-8", errors="ignore") as csv_file:
            writer = None
            line_number = 0  # Track the line number for debugging
            for line in file:
                line_number += 1
                try:
                    data_line = json.loads(line.strip())
                    if writer is None:
                        writer = csv.DictWriter(csv_file, fieldnames=data_line.keys())
                        writer.writeheader()
                    writer.writerow(data_line)
                except json.JSONDecodeError as json_error:
                    logging.error(f"JSONDecodeError on line {line_number}: {json_error}")
                except Exception as e:
                    logging.error(f"Error processing line {line_number}: {e}")
        logging.info(f"JSONL file successfully converted to CSV: {output_csv}")
    except Exception as e:
        logging.error(f"Error in jsonl_to_csv: {e}")
        raise

# jsonl_to_csv(filepath, output_file)

# df = pd.read_csv(r"logic/products.csv")

def generate_create_table_sql(df, table_name):
    sql = f"CREATE TABLE {table_name} (\n"
    for col in df.columns:
        sql += f"    \"{col}\" TEXT,\n"  # everything as TEXT to simplify
    sql = sql.rstrip(',\n') + "\n);"
    return sql


# print(generate_create_table_sql(df, "products"))


def is_gzipped(file_path):
    with open(file_path, 'rb') as f:
        return f.read(2) == b'\x1f\x8b'
    
      # GZIP magic number

# print(is_gzipped(filepath))  # True means gzipped



def df_to_sql(df,table_name):
    try:
        engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/recommender_database')
        with engine.connect() as connection:
            df.to_sql(table_name,con = connection,if_exists = 'append',index = False)
            print("data added")
    except Exception as e:
        print(f"Error occured:{e}")
        raise



def jsonl_to_df(file_path):

    reviews = []
    try:
        with gzip.open(file_path, "rt", encoding="utf-8") as fp:
            for line in fp:
                data_line = json.loads(line.strip())
                reviews.append(data_line)
    except Exception as e:
        print(f"Error converting:{e}")
        raise
        
    df = pd.DataFrame(reviews)
    return df



# def jsonl_to_db(file_path,table_name):

#     batch_size = 50000
#     total_records = 0
#     reviews = []
#     try:
#         with gzip.open(file_path, "rt", encoding="utf-8") as fp:
#             for line in fp:
#                 data_line = json.loads(line.strip())
#                 reviews.append(data_line)

#                 if len(reviews) >= batch_size:
#                     batch_counter += 1
#                     df = pd.DataFrame(reviews)
#                     logging.info(f"Dataframe created:{df.head(3)}")
#                     df = df.astype(str)

#     except Exception as e:
#         print(f"Error converting:{e}")
        
#     # df = pd.DataFrame(reviews)
#     # logging.info(f"Dataframe created:{df.head(3)}")

#     # df = df.astype(str)

#     try:
#         df_to_sql(df,table_name=table_name)
#         logging.info(f"Batch #{batch_counter} successfully loaded. Total records so far: {total_records}")
#         # logging.info(f"Data updated to table {table_name}")
#     except Exception as e:
#         logging.error(f"Error processing batch #{batch_counter}: {e}")
#         # logging.error(f"Error in jsonl_to_db: {e}")
#         return f"Error updating data {e}"
    
def jsonl_to_db(file_path, table_name, batch_size=10000):
    """
    Processes a JSONL file and loads data into a database table in batches.
    
    Args:
        file_path: Path to the JSONL file (can be gzipped)
        table_name: Name of the target database table
        batch_size: Number of records to process in each batch (default: 1000)
    """
    batch_counter = 0
    total_records = 0
    current_batch = []

    try:
        with gzip.open(file_path, "rt", encoding="utf-8") as fp:
            for line in fp:
                try:
                    data_line = json.loads(line.strip())
                    current_batch.append(data_line)
                    
                    # When batch size is reached, process the batch
                    if len(current_batch) >= batch_size:
                        batch_counter += 1
                        df = pd.DataFrame(current_batch)
                        df = df.astype(str)
                        
                        logging.info(f"Processing batch #{batch_counter} with {len(df)} records")
                        
                        try:
                            df_to_sql(df, table_name=table_name)
                            total_records += len(df)
                            logging.info(f"Batch #{batch_counter} successfully loaded. Total records so far: {total_records}")
                        except Exception as batch_error:
                            logging.error(f"Error processing batch #{batch_counter}: {batch_error}")
                        
                        # Clear the current batch
                        current_batch = []
                
                except json.JSONDecodeError as json_err:
                    logging.warning(f"Skipping invalid JSON line: {json_err}")
        
        # Process any remaining records in the final batch
        if current_batch:
            batch_counter += 1
            df = pd.DataFrame(current_batch)
            df = df.astype(str)
            
            logging.info(f"Processing final batch #{batch_counter} with {len(df)} records")
            
            try:
                df_to_sql(df, table_name=table_name)
                total_records += len(df)
                logging.info(f"Final batch successfully loaded. Total records: {total_records}")
            except Exception as final_batch_error:
                logging.error(f"Error processing final batch: {final_batch_error}")
    
    except Exception as e:
        logging.error(f"Error opening or reading file: {e}")
        return f"Error processing file: {e}"
    
    return f"Successfully loaded {total_records} records into {table_name} in {batch_counter} batches"

jsonl_to_db(review_file,"products_table")


# applliance_df = jsonl_to_df(review_file)
# print(generate_create_table_sql(applliance_df, "products"))

# print(generate_create_table_sql(applliance_df,"user_reviews"))

# df_to_sql(df)

# def df_to_sql(df):
#     try:
#         # Check if df is valid
#         if df is None or isinstance(df, str):
#             print(f"Invalid DataFrame object: {df}")
#             return False
        
#         # Create the engine
#         engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/recommender_database')
        
#         # Use a connection explicitly
#         with engine.connect() as connection:
#             # Use the connection directly
#             df.to_sql("products", con=connection, if_exists='replace', index=False)
            
#         print("Data added to database successfully")
#         return True
#     except SQLAlchemyError as e:
#         print(f"SQLAlchemy error in df_to_sql: {e}")
#         return False
#     except Exception as e:
#         print(f"General error in df_to_sql: {e}")
#         return False

# df_to_sql(new_Df)





# def data_to_db(file_path):
#     try:
#         new_df = jsonl_to_df(file_path)
#         print("Data Cleaned")
#         df_to_sql(new_df)
#         print("Data added to DB")
#     except  Exception as e:
#         return f"Error in data_to_db: {e}"






