import os
import random
from pymongo import MongoClient

# MongoDB কানেকশন (আপনার আসল কানেকশন স্ট্রিং ব্যবহার করা হয়েছে)
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://servernitrado59_db_user:FU2qt15RfoyNDW1m@cluster0.delarjm.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['wear_by_me_db']

# 🚀 কাস্টম ইউনিক আইডি জেনারেটর (আপনার ইউনিক রুলস অনুযায়ী)
def generate_unique_id(role):
    """
    role = 'U' (User), 'S' (Seller), 'P' (Product), 'O' (Order), 'A' (Admin), 'SF' (Staff)
    """
    is_unique = False
    new_id = ""
    
    # ডুপ্লিকেট আইডি এড়ানোর জন্য লুপ
    while not is_unique:
        if role == 'U':
            # Format: 9999WBM999U
            new_id = f"{random.randint(1000, 9999)}WBM{random.randint(100, 999)}U"
            collection = db['users']
            id_key = "user_id"
            
        elif role == 'S':
            # Format: 99999WBM999S
            new_id = f"{random.randint(10000, 99999)}WBM{random.randint(100, 999)}S"
            collection = db['sellers']
            id_key = "seller_id"
            
        elif role == 'P':
            # Format: 99999999WBM9999P
            new_id = f"{random.randint(10000000, 99999999)}WBM{random.randint(1000, 9999)}P"
            collection = db['products']
            id_key = "product_id"
            
        elif role == 'O':
            # Format: 99999999WBM999O
            new_id = f"{random.randint(10000000, 99999999)}WBM{random.randint(100, 999)}O"
            collection = db['orders']
            id_key = "order_id"
            
        elif role == 'A':
            # Format: 9999WBM99A
            new_id = f"{random.randint(1000, 9999)}WBM{random.randint(10, 99)}A"
            collection = db['admins']
            id_key = "admin_id"
            
        elif role == 'SF':
            # Format: 99999WBM9999SF
            new_id = f"{random.randint(10000, 99999)}WBM{random.randint(1000, 9999)}SF"
            collection = db['staff']
            id_key = "staff_id"
            
        else:
            return f"{random.randint(1000, 9999)}WBM{random.randint(100, 999)}"

        # চেক করা হচ্ছে এই আইডিটা আগে থেকেই ডাটাবেসে এক্সিস্ট করে কি না
        existing = collection.find_one({id_key: new_id})
        if not existing:
            is_unique = True # একদম ফ্রেশ আইডি পাওয়া গেছে!

    return new_id
    
