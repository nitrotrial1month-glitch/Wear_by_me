import os
import random
from pymongo import MongoClient

# MongoDB কানেকশন
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://servernitrado59_db_user:FU2qt15RfoyNDW1m@cluster0.delarjm.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['wear_by_me_db']

# 🚀 কাস্টম ইউনিক আইডি জেনারেটর (আপনার নতুন ফরম্যাট অনুযায়ী)
def generate_unique_id(role):
    if role == 'U':
        # 11111WBMU111 (5 digits + WBMU + 3 digits)
        return f"{random.randint(10000, 99999)}WBMU{random.randint(100, 999)}"
        
    elif role == 'SF':
        # 1111WBMSF11 (4 digits + WBMSF + 2 digits)
        return f"{random.randint(1000, 9999)}WBMSF{random.randint(10, 99)}"
        
    elif role == 'O':
        # 11111WBMO111 (5 digits + WBMO + 3 digits)
        return f"{random.randint(10000, 99999)}WBMO{random.randint(100, 999)}"
        
    elif role == 'P':
        # 111111WBMP1111 (6 digits + WBMP + 4 digits)
        return f"{random.randint(100000, 999999)}WBMP{random.randint(1000, 9999)}"
        
    elif role == 'A':
        # 1111WBMA111 (4 digits + WBMA + 3 digits)
        return f"{random.randint(1000, 9999)}WBMA{random.randint(100, 999)}"
        
    else:
        # Default Fallback
        return f"{random.randint(1000, 9999)}WBM{random.randint(100, 999)}"
        
