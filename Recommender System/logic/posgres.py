import psycopg2 
import random



class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(database = 'recommender_database',
                                     user = 'postgres',
                                     host = 'localhost',
                                     password = '1234',
                                     port = 5433)
        self.cur = self.conn.cursor()

    def _ensure_cursor(self):
        if self.cur.closed:
            self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def execute(self,query,params=None):
        self.cur.execute(query,params) 

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()
    
    def fetchmany(self):
        return self.cur.fetchmany()

    def close(self):
        self.cur.close()
        self.conn.close()




class User_info_DB:
    def __init__(self,db_manager):
        self.db = db_manager

    def add_user(self,user_name,password):
        query = 'Insert Into user_data(user_name,user_password) Values(%s,%s)'
        params = (user_name,password)
        self.db.execute(query=query,params=params)
        self.db.commit()
        # self.db.close()

    def check_user_data(self,user_name):
        query = 'Select user_name from user_data WHERE user_name = %s'
        params = (user_name,)
        self.db.execute(query,params)
        results = self.db.fetchall()
        return results
        
    def get_user_id(self,user_name):
        query = 'Select user_id from user_data WHERE user_name = %s'
        params  = (user_name,)
        self.db.execute(query,params)
        results = self.db.fetchall()
        return results

    def get_user_name(self,user_name):
        query = 'Select user_name from user_data WHERE user_id = %s'
        params  = (user_name,)
        self.db.execute(query,params)
        results = self.db.fetchall()
        return results




class User_Interaction_DB:
    def __init__(self,db_manager):
        self.db  =db_manager

    def add_intercation(self,user_id, product_id, product_name,event_type):
        query = 'Insert Into user_interaction(user_id, product_id, product_name,event_type) Values(%s,%s,%s,%s)'
        params = (user_id, product_id, product_name,event_type)
        self.db.execute(query=query,params=params)
        self.db.commit()
        self.db.close()



class ProductsDB():
    def __init__(self,db_manager):
        self.db = db_manager

    def get_product_details(self,product_id):
        # query = 'Select * from  products WHERE product_id = %s'
        query = 'Select product_id,main_category,title,price,images from products WHERE product_id = %s'
        params = (product_id,)
        self.db.execute(query=query,params=params)
        results = self.db.fetchall()
        return results


    def get_featured_products(self):
        query = 'SELECT product_id,main_category,title,price,images FROM products LIMIT 100' 

        self.db.execute(query=query,params=None)
        results = self.db.fetchall()
        featured_products = random.sample(results,k=10)
        return featured_products
    

    def model_training_data(self):
        query = 'Select product_id,title from products'
        self.db.execute(query = query,params= None)
        all_products = self.db.fetchall()
        return all_products


    def pipeline_data(self,batch_size):
        query = 'Select product_id,title from products'
        self.db.execute(query = query,params= None)

    def get_column_names(self,table_name):
        query = 'Select column_name from information_schema.columns WHERE table_name = %s'
        params = (table_name,)
        self.db.execute(query = query,params= params)
        column_names = self.db.fetchall()
        return column_names




class User_review_DB():
    def __init__(self,db_manager):
        self.db = db_manager
        
    def model_data(self):
        # query = 'SELECT customer_id, item_id, rating from products_table'
        query = 'SELECT customer_id, product_id, rating from user_reviews'

        self.db.execute(query,params = None)
        all_reviews = self.db.fetchall()
        return all_reviews


## Main DB
db = DBManager()
product_db= ProductsDB(db)

import ast
prod = product_db.get_product_details(12)

def image_thumbnail(details):
    str_details = ast.literal_eval(details[0][4])
    image = str_details[0]['large']
    return image


# print(image_thumbnail(prod))
# # # product_db.model_training_data()

# d = ast.literal_eval(prod[0][4])
# print(d[0]['thumb'])

# all_data = product_db.model_training_data()

# print(all_data[0])



# cat_products = product_db.get_featured_products()

# print((cat_products)[25][8][0]) 

# all_dics = []

# for i in range(len(cat_products)):
#     print(cat_products[i][9])
#     ids = cat_products[i][0]
#     category_name= cat_products[i][1]
#     titles = cat_products[i][2]
#     prices = cat_products[i][7]

#     dic = {'id':ids,'name':titles,'price':prices,'category':category_name}
#     all_dics.append(dic)

# print(all_dics)




# -- -- ALTER TABLE products_table ADD COLUMN item_id bigint;
# -- UPDATE products_table pt
# -- SET item_id = p.product_id
# -- FROM products p
# -- WHERE pt.parent_asin = p.parent_asin;

