from faker import Faker
import logging
import pandas as pd
import psycopg2

logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

faker = Faker()
# print (fake.password(length=10))
# print(fake.name())


try:
    conn = psycopg2.connect(database = 'recommender_database',
                                        user = 'postgres',
                                        host = 'localhost',
                                        password = '1234',
                                        port = 5433)
    cur = conn.cursor()
    logging.info("Connected")
except Exception as e:
    print(e)

# cur.execute("SELECT DISTINCT user_id FROM user_reviews")
# unique_user_ids = [row[0] for row in cur.fetchall()]

# print(len(unique_user_ids))

# print(unique_user_ids[0:10])


# batch_size = 10000

# # Connect to DB (assuming conn and cur already set)
# cur.execute("SELECT DISTINCT user_id FROM user_reviews")
# unique_user_ids = [row[0] for row in cur.fetchall()]

# def generate_fake_credentials(user_ids):
#     creds = []
#     for user_id in user_ids:
#         username = faker.user_name()
#         password = faker.password(length=10)
#         creds.append((username, password, user_id))
#     return creds

# update_query = "UPDATE user_reviews SET username = %s, password = %s WHERE user_id = %s"

# for i in range(0, len(unique_user_ids), batch_size):
#     batch_user_ids = unique_user_ids[i:i+batch_size]
#     batch_creds = generate_fake_credentials(batch_user_ids)
    
#     # Execute batch updates in a single transaction
#     try:
#         for uname, pwd, uid in batch_creds:
#             cur.execute(update_query, (uname, pwd, uid))
#         conn.commit()
#         print(f"Updated batch {i} to {i + len(batch_user_ids)}")
#     except Exception as e:
#         conn.rollback()
#         print(f"Error updating batch {i} to {i + len(batch_user_ids)}: {e}")

# # Close cursor and connection when done
# cur.close()
# conn.close()






# data = cur.fetchall()
# columns = [desc[0] for desc in cur.description]


# df = pd.DataFrame(data,columns=columns)
# print(df['username'].info())

from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

# Configure logging


# def get_db_connection():
#     """Create database connection"""
#     return psycopg2.connect(
#         database='recommender_database',
#         user='postgres',
#         host='localhost',
#         password='1234',
#         port=5433
#     )

# def generate_credentials_batch(user_ids, existing_usernames=None):
#     """Generate credentials for a batch of user IDs - optimized version"""
#     if existing_usernames is None:
#         existing_usernames = set()
    
#     creds = []
#     batch_usernames = set()
    
#     for user_id in user_ids:
#         # Generate username more efficiently
#         attempts = 0
#         while attempts < 10:  # Limit attempts to avoid infinite loops
#             username = faker.user_name()
#             if username not in existing_usernames and username not in batch_usernames:
#                 batch_usernames.add(username)
#                 break
#             attempts += 1
#         else:
#             # Fallback: append random number
#             username = f"{faker.user_name()}_{faker.random_int(1000, 9999)}"
        
#         # Simple password without hashing for speed (use hashing in production)
#         password = faker.password(length=10)
#         creds.append((username, password, user_id))
    
#     return creds

# def bulk_update_optimized():
#     """Super optimized version using execute_values"""
#     start_time = time.time()
    
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         logging.info("Connected to database")
        
#         # Get user IDs more efficiently
#         cur.execute("SELECT user_id FROM user_reviews WHERE username IS NULL OR username = '' ORDER BY user_id")
#         unique_user_ids = [row[0] for row in cur.fetchall()]
#         total_users = len(unique_user_ids)
#         logging.info(f"Found {total_users} users to update")
        
#         if not unique_user_ids:
#             logging.info("No users to update")
#             return
        
#         # Process in larger batches for better performance
#         batch_size = 50000  # Increased batch size
#         total_updated = 0
        
#         for i in range(0, len(unique_user_ids), batch_size):
#             batch_start = time.time()
#             batch_user_ids = unique_user_ids[i:i+batch_size]
            
#             # Generate credentials for entire batch
#             batch_creds = generate_credentials_batch(batch_user_ids)
            
#             try:
#                 # Use execute_values for maximum performance
#                 execute_values(
#                     cur,
#                     "UPDATE user_reviews SET username = data.username, password = data.password FROM (VALUES %s) AS data(username, password, user_id) WHERE user_reviews.user_id = data.user_id",
#                     batch_creds,
#                     template=None,
#                     page_size=10000
#                 )
                
#                 conn.commit()
#                 total_updated += len(batch_creds)
#                 batch_time = time.time() - batch_start
                
#                 logging.info(f"Batch {i//batch_size + 1}: Updated {len(batch_creds)} users in {batch_time:.2f}s (Total: {total_updated}/{total_users})")
                
#             except Exception as e:
#                 conn.rollback()
#                 logging.error(f"Error in batch starting at {i}: {e}")
#                 continue
        
#         total_time = time.time() - start_time
#         logging.info(f"Completed: Updated {total_updated} users in {total_time:.2f} seconds")
#         logging.info(f"Rate: {total_updated/total_time:.2f} users/second")
        
#     except Exception as e:
#         logging.error(f"Database error: {e}")
#     finally:
#         if 'cur' in locals():
#             cur.close()
#         if 'conn' in locals():
#             conn.close()

# def super_fast_version():
#     """Ultra-fast version using COPY and temporary table"""
#     start_time = time.time()
    
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         # Get user IDs
#         cur.execute("SELECT user_id FROM user_reviews WHERE username IS NULL OR username = ''")
#         user_ids = [row[0] for row in cur.fetchall()]
#         total_users = len(user_ids)
#         logging.info(f"Processing {total_users} users")
        
#         if not user_ids:
#             return
        
#         # Generate all credentials at once
#         logging.info("Generating credentials...")
#         all_creds = generate_credentials_batch(user_ids)
        
#         # Create temporary table
#         cur.execute("""
#             CREATE TEMP TABLE temp_user_creds (
#                 user_id INTEGER,
#                 username VARCHAR(255),
#                 password VARCHAR(255)
#             )
#         """)
        
#         # Use COPY for ultra-fast insertion
#         logging.info("Inserting into temp table...")
#         from io import StringIO
        
#         # Prepare data for COPY
#         copy_data = StringIO()
#         for username, password, user_id in all_creds:
#             copy_data.write(f"{user_id}\t{username}\t{password}\n")
#         copy_data.seek(0)
        
#         # COPY data to temp table
#         cur.copy_from(copy_data, 'temp_user_creds', columns=('user_id', 'username', 'password'))
        
#         # Update main table from temp table
#         logging.info("Updating main table...")
#         cur.execute("""
#             UPDATE user_reviews 
#             SET username = temp_user_creds.username,
#                 password = temp_user_creds.password
#             FROM temp_user_creds
#             WHERE user_reviews.user_id = temp_user_creds.user_id
#         """)
        
#         updated_count = cur.rowcount
#         conn.commit()
        
#         total_time = time.time() - start_time
#         logging.info(f"Ultra-fast version: Updated {updated_count} users in {total_time:.2f} seconds")
#         logging.info(f"Rate: {updated_count/total_time:.2f} users/second")
        
#     except Exception as e:
#         logging.error(f"Error in super fast version: {e}")
#         conn.rollback()
#     finally:
#         cur.close()
#         conn.close()

# if __name__ == "__main__":
#     # Choose your preferred method:
    
#     # Method 1: Optimized batch processing
#     bulk_update_optimized()
    
    # Method 2: Ultra-fast using COPY (uncomment to use)
    # super_fast_version()

from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
import logging
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

faker = Faker()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        database='recommender_database',
        user='postgres',
        host='localhost',
        password='1234',
        port=5433
    )

def generate_user_credentials(unique_user_ids):
    """Generate ONE set of credentials per unique user"""
    user_credentials = {}
    used_usernames = set()
    
    for user_id in unique_user_ids:
        # Generate unique username
        username = faker.user_name()
        counter = 1
        base_username = username
        
        while username in used_usernames:
            username = f"{base_username}{counter}"
            counter += 1
        
        used_usernames.add(username)
        password = faker.password(length=10)
        
        # Store credentials for this user_id
        user_credentials[user_id] = (username, password)
        
    return user_credentials

def bulk_update_all_user_records():
    """Update ALL records for each user with the same credentials"""
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Connected to database")
        
        # Get DISTINCT user IDs (only unique users)
        cur.execute("""
            SELECT DISTINCT user_id 
            FROM user_reviews 
            WHERE username IS NULL OR username = '' OR password IS NULL OR password = ''
        """)
        unique_user_ids = [row[0] for row in cur.fetchall()]
        
        logging.info(f"Found {len(unique_user_ids)} unique users to update")
        
        if not unique_user_ids:
            logging.info("No users to update")
            return
        
        # Generate credentials for unique users only
        logging.info("Generating credentials for unique users...")
        user_credentials = generate_user_credentials(unique_user_ids)
        
        # Update ALL records for each user in batches
        batch_size = 10000
        total_updated = 0
        
        for i in range(0, len(unique_user_ids), batch_size):
            batch_start = time.time()
            batch_user_ids = unique_user_ids[i:i+batch_size]
            
            # Prepare update data for this batch
            update_data = []
            for user_id in batch_user_ids:
                username, password = user_credentials[user_id]
                update_data.append((username, password, user_id))
            
            try:
                # Update ALL records for these users (not just one record per user)
                execute_values(
                    cur,
                    """
                    UPDATE user_reviews 
                    SET username = data.username, password = data.password 
                    FROM (VALUES %s) AS data(username, password, user_id) 
                    WHERE user_reviews.user_id = data.user_id
                    """,
                    update_data,
                    page_size=5000
                )
                
                affected_rows = cur.rowcount
                conn.commit()
                total_updated += affected_rows
                
                batch_time = time.time() - batch_start
                logging.info(f"Batch {i//batch_size + 1}: Updated {affected_rows} records for {len(batch_user_ids)} users in {batch_time:.2f}s")
                
            except Exception as e:
                conn.rollback()
                logging.error(f"Error in batch starting at {i}: {e}")
                continue
        
        # Get final statistics
        cur.execute("SELECT COUNT(*) FROM user_reviews WHERE username IS NOT NULL AND username != ''")
        total_records_with_creds = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM user_reviews WHERE username IS NOT NULL AND username != ''")
        total_users_with_creds = cur.fetchone()[0]
        
        total_time = time.time() - start_time
        logging.info(f"Completed: Updated {total_updated} records for {len(unique_user_ids)} unique users in {total_time:.2f} seconds")
        logging.info(f"Final stats: {total_records_with_creds} total records, {total_users_with_creds} unique users have credentials")
        logging.info(f"Rate: {total_updated/total_time:.2f} records/second")
        
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def verify_consistency():
    """Verify that all records for each user have the same credentials"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check for users with inconsistent credentials
        cur.execute("""
            SELECT user_id, COUNT(DISTINCT username) as username_count, COUNT(DISTINCT password) as password_count
            FROM user_reviews 
            WHERE username IS NOT NULL AND password IS NOT NULL
            GROUP BY user_id
            HAVING COUNT(DISTINCT username) > 1 OR COUNT(DISTINCT password) > 1
        """)
        
        inconsistent_users = cur.fetchall()
        
        if inconsistent_users:
            logging.warning(f"Found {len(inconsistent_users)} users with inconsistent credentials!")
            for user_id, username_count, password_count in inconsistent_users[:5]:  # Show first 5
                logging.warning(f"User {user_id}: {username_count} different usernames, {password_count} different passwords")
        else:
            logging.info("✓ All users have consistent credentials across their records")
        
        # Show summary statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as records_with_username
            FROM user_reviews
        """)
        
        stats = cur.fetchone()
        logging.info(f"Summary: {stats[0]} total records, {stats[1]} unique users, {stats[2]} records with usernames")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Verification error: {e}")

def show_sample_data():
    """Show sample of the data to verify results"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT user_id, username, password, COUNT(*) as record_count
            FROM user_reviews 
            WHERE username IS NOT NULL 
            GROUP BY user_id, username, password
            ORDER BY user_id
            LIMIT 10
        """)
        
        results = cur.fetchall()
        logging.info("Sample data (first 10 users):")
        for user_id, username, password, count in results:
            logging.info(f"User {user_id}: {username} / {password} ({count} records)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Sample data error: {e}")

if __name__ == "__main__":
    # Update all user records
    bulk_update_all_user_records()
    
    # Verify consistency
    verify_consistency()
    
    # Show sample results
    show_sample_data()


# INSERT INTO user_data (user_name, user_password)
# SELECT DISTINCT username, password
# FROM user_reviews 
# WHERE username IS NOT NULL 
# AND password IS NOT NULL 
# AND username != '' 
# AND password != ''
# AND NOT EXISTS (
#     SELECT 1 FROM user_data 
#     WHERE user_name = username
# );