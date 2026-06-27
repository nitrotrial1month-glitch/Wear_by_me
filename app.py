import os
import importlib
from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from database import db

app = Flask(__name__)
CORS(app)

# =========================================================
# 🚀 AUTO ROUTE LOADER (ম্যাজিক ফোল্ডার স্ক্যানার)
# =========================================================
def load_all_routes(app):
    # 'routes' ফোল্ডারের লোকেশন বের করা
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    
    # ফোল্ডার না থাকলে তৈরি করে নেবে
    if not os.path.exists(routes_dir):
        os.makedirs(routes_dir)
        print("📁 'routes' folder created.")

    # ফোল্ডারের ভেতরের সব .py ফাইল স্ক্যান করা
    for filename in os.listdir(routes_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f"routes.{filename[:-3]}"
            
            # ফাইলটিকে ইমপোর্ট করা
            module = importlib.import_module(module_name)
            
            # ফাইলের ভেতরে কোনো ফ্লাস্ক Blueprint আছে কি না চেক করা
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, Blueprint):
                    app.register_blueprint(item)
                    print(f"✅ Auto-Loaded Route: {module_name} -> {item.name}")

# অটো লোডার চালু করা হলো
load_all_routes(app)

# =========================================================
# 🏠 হোমপেজ API (এটি এখানেই রাখলাম সুবিধার জন্য)
# =========================================================
@app.route('/api/home', methods=['GET'])
def get_home_data():
    try:
        banners_collection = db['banners']
        active_banner = banners_collection.find_one({"is_active": True})
        banner_data = {"title": active_banner.get("title", ""), "subtitle": active_banner.get("subtitle", ""), "image_url": active_banner.get("image_url", "")} if active_banner else None

        products_collection = db['products']
        product_list = [{"id": str(prod['_id']), "name": prod.get('name', ''), "price": prod.get('price', 0), "image": prod.get('image', ''), "category": prod.get('category', 'All')} for prod in products_collection.find({})]

        return jsonify({"status": "success", "banner": banner_data, "products": product_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
