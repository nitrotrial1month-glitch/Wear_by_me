from flask import Blueprint, request, jsonify
from database import db, generate_unique_id # generate_unique_id ইমপোর্ট করা হলো
import re
import datetime # আপলোডের সময় সেভ করার জন্য

# ব্লুপ্রিন্ট তৈরি করা হলো
products_bp = Blueprint('products_bp', __name__)

# ==========================================
# 🔍 ১. প্রোডাক্ট সার্চ API (বায়ার অ্যাপের জন্য)
# ==========================================
@products_bp.route('/api/products/search', methods=['GET'])
def search_products():
    try:
        category = request.args.get('category', 'All')
        search_query = request.args.get('search', '')
        
        query = {}
        
        # ক্যাটাগরি ফিল্টার
        if category and category != 'All':
            query['category'] = category
            
        # ট্যাগস এবং নামের উপর সার্চ ফিল্টার
        if search_query:
            regex_pattern = re.compile(search_query, re.IGNORECASE)
            query['$or'] = [
                {'tags': {'$regex': regex_pattern}},
                {'name': {'$regex': regex_pattern}}
            ]
            
        products_collection = db['products']
        # 'createdAt' এর বদলে আমরা 'upload_date' দিয়ে সর্ট করতে পারি (যেহেতু নিচে upload_date সেভ হচ্ছে)
        cursor = products_collection.find(query).sort("upload_date", -1)
        
        products = []
        for doc in cursor:
            products.append({
                "id": str(doc.get('product_id', doc['_id'])), # WBM_P_ID থাকলে সেটা নেবে
                "name": doc.get('name', ''),
                "price": doc.get('price', 0),
                "image": doc.get('image', ''), # অথবা colors_and_media থেকে প্রথম ছবি
                "category": doc.get('category', ''),
                "tags": doc.get('tags', [])
            })
            
        return jsonify({"status": "success", "products": products}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 🛍️ ২. প্রোডাক্ট লাইভ আপলোড API (সেলার অ্যাপের জন্য)
# ==========================================
@products_bp.route('/api/seller/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        seller_id = data.get('seller_id')
        
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID missing!"}), 400

        # 🔴 প্রোডাক্টের জন্য আপনার স্পেশাল ইউনিক আইডি জেনারেট
        product_id = generate_unique_id('P')

        # ডাটাবেসের জন্য প্রোডাক্ট ডকুমেন্ট তৈরি
        new_product = {
            "product_id": product_id,
            "seller_id": seller_id,
            "name": data.get('name'),
            "price": data.get('price'),
            "stock": data.get('stock'),
            "description": data.get('description'),
            "specifications": data.get('specifications'),
            "sizes": data.get('sizes', []),
            "colors_and_media": data.get('variants', []), # ক্লাউডিনারির URL-গুলো
            "refund_policy": data.get('refund_policy', True),
            # সার্চ API এর জন্য ক্যাটাগরি ও ট্যাগস ডিফল্টভাবে যুক্ত করা হলো
            "category": "Uncategorized", 
            "tags": data.get('name', '').split(), 
            "status": "Active",
            "upload_date": datetime.datetime.utcnow()
        }

        # MongoDB-তে 'products' কালেকশনে ডেটা সেভ করা
        db['products'].insert_one(new_product)

        return jsonify({
            "status": "success",
            "message": "Product Uploaded Successfully!",
            "product_id": product_id
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# 📦 ৩. সেলারের নিজস্ব প্রোডাক্ট দেখার API (হোমপেজের জন্য)
# ==========================================
@products_bp.route('/api/seller/my_products', methods=['GET'])
def get_my_products():
    try:
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID required!"}), 400
            
        products_collection = db['products']
        # শুধু এই সেলারের প্রোডাক্টগুলো লেটেস্ট আপলোড অনুযায়ী আনা হচ্ছে
        cursor = products_collection.find({"seller_id": seller_id}).sort("upload_date", -1)
        
        my_products = []
        for doc in cursor:
            # ক্লাউডিনারি থেকে প্রথম ছবিটা বের করা
            image_url = ""
            variants = doc.get("colors_and_media", [])
            if variants and len(variants) > 0:
                images = variants[0].get("images", [])
                if images and len(images) > 0:
                    image_url = images[0]

            my_products.append({
                "product_id": doc.get('product_id', ''),
                "name": doc.get('name', ''),
                "price": doc.get('price', 0),
                "stock": doc.get('stock', 0),
                "status": doc.get('status', 'Active'),
                "image": image_url
            })
            
        return jsonify({"status": "success", "products": my_products}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
        
