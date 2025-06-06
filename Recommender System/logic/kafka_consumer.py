from kafka import KafkaConsumer
import json
from posgres import User_Interaction_DB,db
import logging
logging.basicConfig(level= logging.INFO,
                    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

consumer = KafkaConsumer("my_topic",
                         bootstrap_servers = 'localhost:9092',
                            #  bootstrap_servers=['127.0.0.1:9092']

                         auto_offset_reset='earliest',enable_auto_commit=True,
                         group_id='recsys_group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                         )


user_int_db = User_Interaction_DB(db)

for data in consumer:

    message = data.value
    logging.info(f"received {message}")
    try:
        product_id = message['product_id']
        logging.info(f"received {product_id}")

        product_name = message['product_name']
        logging.info(f"received {product_name}")

        event_type = message['action']
        logging.info(f"received {event_type}")

        user_id = message['user_id']
        logging.info(f"received {user_id}")
        
        # print(product_id,product_name,user_id,event_type)
        user_int_db.add_intercation(user_id=user_id, product_id=product_id, product_name=product_name,event_type=event_type)
        logging.info(f"Event added:{event_type}")
    except Exception as e:
        print(f"{e}")








