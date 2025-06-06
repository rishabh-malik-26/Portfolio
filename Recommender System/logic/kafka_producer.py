import json
from kafka import KafkaProducer,KafkaConsumer
# from posgres import User_Interaction_DB,DBManager
import logging
logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
def add_data(event_data):

    producer= KafkaProducer(bootstrap_servers = 'localhost:9092',
                            value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logging.info("Producer Initiated")

    data = event_data

    producer.send("my_topic",value=data)
    logging.info("Data Sent")


    producer.flush()
    logging.info("Data Flushed")


# event = {'product_id': '20', 
# 'product_name': '3-pack OnePurify Water Filter Replacement Cartridge for LG','action':
# 'add_to_cart'}

# print(type(event))
# add_data(event)



# db = DBManager()
# user_int_db = User_Interaction_DB(db)
# user_int_db.add_intercation(user_id=user_id, product_id=product_id, product_name=product_name,event_type=event_type)
# logging.info(f"Event added:{event_type}")
# # print("Waiting for messages...")






