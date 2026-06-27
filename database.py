import os
import random
from pymongo import MongoClient

# MongoDB কানেকশন
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://servernitrado59_db_user:FU2qt15RfoyNDW1m@cluster0.delarjm.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['wear_by_me_db']

# ইউনিক আইডি জেনারেটর
def generate_unique_id():
    part1 = random.randint(1000, 9999) 
    part2 = random.randint(100, 999)   
    return f"WBD_U_ID - {part1}WBM{part2}"
  
