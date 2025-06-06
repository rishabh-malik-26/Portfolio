import logging 
# import gensim
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import image_thumbnail,clean_amazon_image_url,get_generic_products,image_high_res
from logic.redis_setup import get_recommendations,get_user_recommendations
from logic.kafka_producer import add_data

from logic.posgres import ProductsDB,User_info_DB,db

logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
# from logic.posgres import db
from flask import Flask, render_template, request, redirect, url_for,session,jsonify
app = Flask(__name__)


app.secret_key = "mysecret123"



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        user_name = request.form.get('Username')
        user_pass_word = request.form.get('password')
        logging.info(f"Data received: {user_name} and {user_pass_word}")

        user_info_database = User_info_DB(db)
        logging.info("Database connected")

        ## verify if username exists or not
        output = user_info_database.check_user_data(user_name=user_name)
        logging.info(f"Verified Data {output[0][0]}")

        if output[0][0] is None:
             logging.info(f"{output[0][0]} does not exist")
             error = "User Does not Exists"
             return render_template('login.html', error=error)
 
        else:
            user_id = user_info_database.get_user_id(user_name)
            logging.info(f"Extracted user_id: {user_id}")

            session['user_id'] = user_id

            logging.info(f"Session created for user_id: {session.get('user_id')}")

            return redirect(url_for('category'))

    return render_template('login.html')



@app.route('/register', methods=['POST'])
def register():

    user_name = request.form.get('name')
    password = request.form.get('password')

    user_info_database = User_info_DB(db)
    existing_user = user_info_database.check_user_data(user_name=user_name)
    logging.info(f"Check if username already exists: {existing_user}")

    if existing_user:
            error = "User Already Exists"
            return render_template('login.html', error=error)
    
    else:

        user_info_database.add_user(user_name=user_name,password=password)
        logging.info(f"User registered successfully: {user_name}")
        success_message = "Successfully Registered"
        # return render_template('login.html', success_message=success_message)
        return render_template('category.html')
        # return redirect(url_for('category')) 
    
            # session['user_id'] = user_id 
        # logging.info(f"Session created for user_id: {session.get('user_id')}")
    # logging.info(f"User registered successfully: {full_name}")
    # return redirect(url_for('login'))  





@app.route('/product/<int:product_id>',methods=['GET'])
def product_page(product_id):
    
        session_user_id = session.get('user_id')
        logging.info(f"{session_user_id} received")

        product_db= ProductsDB(db)
        details = product_db.get_product_details(product_id)
        
        logging.info(f"Details: {details}")
        # if not details:
        #     logging.error(f"Product not found: {product_id}")
        #     return "Product not found", 404
        
        id = details[0][0]
        logging.info(f"Product Id extracted {id}")

        title =  details[0][2]
        logging.info(f"Title extracted {title}")    

        category = details[0][1]
        logging.info(f"Category extracted {category}")

        price = details[0][3]
        logging.info(f"Price extracted {price}")  

        image = image_thumbnail(details=details)
        org_image = clean_amazon_image_url(image)
        logging.info(f"Image URL:{org_image}")

        logging.info(f"Details retrieved: {details}")
        product_details = {"id": id,
                        "name": title,
                        "price": price,
                        "category": category,
                            "image": org_image,
                            "description": "No description available"  
        }

        recommended_products = get_recommendations(id)
        similar_products = []

        for i in recommended_products:
            
            recommended_product_id= i['id']
            recommended_product_details = product_db.get_product_details(recommended_product_id)
            recommended_product_title =  recommended_product_details[0][2]
            recommended_product_category = recommended_product_details[0][1]
            recommended_product_price = recommended_product_details[0][3]
            recommended_product_iamge = image_thumbnail(recommended_product_details)
            similar_titles_dic = {'id':recommended_product_id,'name':recommended_product_title,
                                  'price':recommended_product_price,
                                  'category':recommended_product_category
                                  ,'image':recommended_product_iamge}
            print(f"Similar Title {recommended_product_title}")
            similar_products.append(similar_titles_dic)

        return render_template('product_page.html',product_details = product_details,similar_titles=similar_products)

import datetime
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()}


@app.route('/')

def category():

    session_user_id = session.get('user_id')
    logging.info(f"Session {session_user_id} received")

    name = None
    recommended_product_ids = [] 

    if session_user_id is not None:
        org_session_id = session_user_id[0][0]
        user_db = User_info_DB(db)
        org_name = user_db.get_user_name(org_session_id)

        if org_name:
            name = org_name[0][0].title()

        logging.info(f"Extracted name from the session_id: {name}")
         
        try:
            user_recommendations = get_user_recommendations(org_session_id)
            logging.info(f"Recommened products {user_recommendations} received")

            recommended_product_ids = [ i['id'] for i in user_recommendations]
            logging.info(f"Extracted product_ids: {recommended_product_ids}")

        except Exception as e:
            logging.info(f"Error Getting User recommendations: {e}")

        product_db = ProductsDB(db)
        # category_products = product_db.get_featured_products()
        featured_products = []
        for i in recommended_product_ids:

            id = i
            recommended_product_details = product_db.get_product_details(id)
            recommended_product_title =  recommended_product_details[0][2]
            recommended_product_category = recommended_product_details[0][1]
            recommended_product_price = recommended_product_details[0][3]
            recommended_product_iamge = image_high_res(recommended_product_details)

            dic = {'id':id,'name':recommended_product_title,'price':recommended_product_price,
                   'category':recommended_product_category,'image_url':recommended_product_iamge}
            featured_products.append(dic)
            logging.info(f"{featured_products}")

        # for i in range(len(category_products)):
        #     ids = category_products[i][0]
        #     category_name= category_products[i][1]
        #     titles = category_products[i][2]
        #     prices = category_products[i][3]
        #     image_url = image_thumbnail(category_products)
            
            # dic = {'id':ids,'name':titles,'price':prices,'category':category_name,'image_url':image_url}
            # featured_products.append(dic)

        # return render_template('category_page.html',featured_products = featured_products,name = name)
    
    else:
        featured_products = get_generic_products()


    return render_template('category_page.html',featured_products = featured_products,name = name)
         




# @app.route("/search", methods=['GET', 'POST'])
# def search():    

#     if request.method == 'POST':
#         data = request.get_json()
#         # search_query = request.args.get('query', '')
#         search_query = data.get('search_query', '')
#         similar_ids = custom_search(search_query)
#         logging.info("similar products found")

#         searched_products = []

#         for product_id in similar_ids:
#                     product_db= ProductsDB(db)
#         details = product_db.get_product_details(product_id)
        
#         if not details:
#             logging.error(f"Product not found: {product_id}")
#             return "Product not found", 404
        
#         id = details[0][0]
#         title =  details[0][2]
#         category = details[0][11]


#         logging.info(f"Details retrieved: {details}")
#         product_details = {"id": id,
#                         "name": title,
#                         "price": 129.99,
#                         "category": category,
#                             "image": "path/to/default/image.jpg",  # Add this
#                             "description": "No description available"  # Add this
#         }

#         searched_products.append(product_details)

#     return render_template('search.html',relevant_products = searched_products)







@app.route("/search", methods=['GET'])
def search():    
    searched_products = []  # Initialize outside the if block
    
    if request.method == 'GET':
        # data = request.get_json()
        # search_query = data.get('search_query', '')
        search_query = request.args.get('query')
        logging.info(f"Search Query:{search_query}")
        
        if not search_query.strip():  # Validate search query
            return render_template('search.html', relevant_products=searched_products, error="Please enter a search term")
        
        try:
            from functions import custom_search
            similar_ids = custom_search(search_query)
            logging.info(f"Similar products found {similar_ids}")

            product_db = ProductsDB(db)  # Move outside the loop

            for product_id in similar_ids:
                details = product_db.get_product_details(product_id)
                logging.info(f"Similar IDs:{details}")
                
                if not details:
                    logging.error(f"Product not found: {product_id}")
                    continue  # Skip this product instead of returning 404
                
                # Extract details safely
                id = details[0][0]
                logging.info(f"Id Extracte {id}")
                title = details[0][2]
                logging.info(f"Title Extracted {title}")
                category = details[0][1]
                logging.info(f"Category Extracted {category}")
                image = image_thumbnail(details)
                logging.info(f"Image URL:{image}")
                price =  details[0][3]

                logging.info(f"Details retrieved for product {id}: {details}")
                
                product_details = {
                    "id": id,
                    "name": title,
                    "price": price,  # Consider getting actual price from database
                    "category": category,
                    "image": image,
                    "description": "No description available"
                }
                
                searched_products.append(product_details)
                
        except Exception as e:
            logging.error(f"Error during search: {e}")
            return render_template('search.html', relevant_products=[], error="Search failed. Please try again.")
    
    # Handle GET requests or return results
    return render_template('search.html', results=searched_products)




# @app.route('/track-interaction', methods=['POST'])
# def track_interaction():

#     if request.method == 'POST':
#         try:
#             data = request.get_json()
#             logging.info(f"User Interaction Data Received {data}")
            
#             user_id = session.get('user_id') 
#             logging.info(f"User ID received from session: {user_id}")

#             product_id = data['product_id']
#             product_name = data['product_name']
#             event_type = data['action']
#             logging.info(f"Data Extracted from user interaction json: {[product_id,product_name,event_type]}")


#             db = DBManager()
#             user_int_db = User_Interaction_DB(db)
#             user_int_db.add_intercation(user_id=user_id, product_id=product_id, product_name=product_name,event_type=event_type)
#             logging.info(f"Event added:{event_type}")

#             return jsonify({"success": True}), 200

#         except Exception as e:
#             logging.info(f"Error receiving user interaction data from frontend:{e}")
#             return jsonify({"Error":str(e)}),500  # No content


## Testing ##

@app.route('/track-interaction', methods=['POST'])
def track_interaction():

    if request.method == 'POST':
        try:
            data = request.get_json()
            logging.info(f"User Interaction Data Received {data}")
            
            add_data(data)
            logging.info("Data shared to Kafka")

            # user_id = session.get('user_id') 
            # logging.info(f"User ID received from session: {user_id}")

            # product_id = data['product_id']
            # product_name = data['product_name']
            # event_type = data['action']
            # logging.info(f"Data Extracted from user interaction json: {[product_id,product_name,event_type]}")


            # db = DBManager()
            # user_int_db = User_Interaction_DB(db)
            # user_int_db.add_intercation(user_id=user_id, product_id=product_id, product_name=product_name,event_type=event_type)
            # logging.info(f"Event added:{event_type}")

            return jsonify({"success": True}), 200

        except Exception as e:
            logging.info(f"Error receiving user interaction data from frontend:{e}")
            return jsonify({"Error":str(e)}),500  


@app.route('/logout')
def logout():
    session.clear()  # Clears all session data, including user_id
    return redirect(url_for('login'))  # Or redirect to home page


if __name__ == '__main__':
    app.run(debug=True)














