from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

# এনভায়রনমেন্ট থেকে ডাটা লোড করা
GOOGLE_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

DISCORD_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT = os.environ.get('DISCORD_REDIRECT_URI')

# এরপর লগইন রাউটে আপনি এগুলো এভাবেই ব্যবহার করতে পারবেন:
# requests.post(discord_token_url, data={'client_id': DISCORD_ID, ...})

app = Flask(__name__)
CORS(app)  # ফ্লাটার অ্যাপ যাতে কোনো ঝামেলা ছাড়া সার্ভারে রিকোয়েস্ট পাঠাতে পারে

# 🔌 আপনার দেওয়া MongoDB কানেকশন স্ট্রিং (সুরক্ষিতভাবে ব্যাকএন্ডে রাখা হলো)
MONGO_URI = "mongodb+srv://servernitrado59_db_user:FU2qt15RfoyNDW1m@cluster0.delarjm.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['wear_by_me_db']  # আপনার ডাটাবেসের নাম

# -----------------------------------------------------------
# 🏠 হোমপেজের জন্য এপিআই (Products & Banners)
# -----------------------------------------------------------
@app.route('/api/home', methods=['GET'])
def get_home_data():
    try:
        # ১. ডাটাবেস থেকে অ্যাক্টিভ ইভেন্ট ব্যানার নিয়ে আসা (যা স্টাফ অ্যাপ থেকে কন্ট্রোল হবে)
        banners_collection = db['banners']
        active_banner = banners_collection.find_one({"is_active": True})
        
        banner_data = None
        if active_banner:
            banner_data = {
                "title": active_banner.get("title", "Special Event"),
                "subtitle": active_banner.get("subtitle", ""),
                "image_url": active_banner.get("image_url", "")
            }

        # ২. ডাটাবেস থেকে সব প্রোডাক্টের লিস্ট নিয়ে আসা
        products_collection = db['products']
        products_cursor = products_collection.find({})
        
        product_list = []
        for prod in products_cursor:
            product_list.append({
                "id": str(prod['_id']), # ObjectId কে ফ্লাটারের জন্য স্ট্রিং করা হলো
                "name": prod.get('name', 'Unknown Item'),
                "price": prod.get('price', 0),
                "image": prod.get('image', ''),
                "category": prod.get('category', 'All')
            })

        # ৩. অ্যাপের কাছে একসাথে সব ডাটা পাঠানো
        return jsonify({
            "status": "success",
            "banner": banner_data,
            "products": product_list
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # আপনার লোকাল নেটওয়ার্কে টেস্ট করার জন্য host='0.0.0.0' দেওয়া হয়েছে
    app.run(host='0.0.0.0', port=5000, debug=True)
  
