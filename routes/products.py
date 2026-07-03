from flask import Blueprint, request, jsonify
from database import db, generate_unique_id
import re
import datetime

products_bp = Blueprint('products_bp', __name__)

# 🔍 ১. প্রোডাক্ট সার্চ API
@products_bp.route('/api/products/search', methods=['GET'])
def search_products():
    try:
        category = request.args.get('category', 'All')
        search_query = request.args.get('search', '')
        query = {}
        
        if category and category != 'All':
            query['category'] = category
            
        if search_query:
            regex_pattern = re.compile(search_query, re.IGNORECASE)
            query['$or'] = [
                {'tags': {'$regex': regex_pattern}},
                {'name': {'$regex': regex_pattern}}
            ]
            
        products_collection = db['products']
        cursor = products_collection.find(query).sort("upload_date", -1)
        
        products = []
        for doc in cursor:
            products.append({
                "id": str(doc.get('product_id', doc['_id'])),
                "name": doc.get('name', ''),
                "price": doc.get('price', 0),
                "image": doc.get('image', ''),
                "category": doc.get('category', ''),
                "tags": doc.get('tags', [])
            })
        return jsonify({"status": "success", "products": products}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🛍️ ২. প্রোডাক্ট লাইভ আপলোড API
@products_bp.route('/api/seller/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        seller_id = data.get('seller_id')
        
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID missing!"}), 400

        product_id = generate_unique_id('P')

        new_product = {
            "product_id": product_id,
            "seller_id": seller_id,
            "name": data.get('name'),
            "price": data.get('price'),
            "stock": data.get('stock'),
            "description": data.get('description'),
            "specifications": data.get('specifications'),
            "sizes": data.get('sizes', []),
            "colors_and_media": data.get('variants', []),
            "return_policy": data.get('return_policy', False),        # আলাদা রিটার্ন পলিসি
            "replacement_policy": data.get('replacement_policy', False), # আলাদা রিপ্লেস পলিসি
            "category": "Uncategorized", 
            "tags": data.get('tags', []), # সেলারের পাঠানো কাস্টম সার্চ ট্যাগস
            "status": "Active",
            "upload_date": datetime.datetime.utcnow()
        }

        db['products'].insert_one(new_product)
        return jsonify({"status": "success", "message": "Product Uploaded!", "product_id": product_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📦 ৩. সেলারের নিজস্ব প্রোডাক্ট দেখার API
@products_bp.route('/api/seller/my_products', methods=['GET'])
def get_my_products():
    try:
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID required!"}), 400
            
        products_collection = db['products']
        cursor = products_collection.find({"seller_id": seller_id}).sort("upload_date", -1)
        
        my_products = []
        for doc in cursor:
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
        
