from flask import Blueprint, request, jsonify
from database import db
import re

# ব্লুপ্রিন্ট তৈরি করা হলো (নাম দিলাম products_bp)
products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/api/products/search', methods=['GET'])
def search_products():
    try:
        category = request.args.get('category', 'All')
        search_query = request.args.get('search', '')
        
        query = {}
        
        # ১. ক্যাটাগরি ফিল্টার
        if category and category != 'All':
            query['category'] = category
            
        # ২. ট্যাগস এবং নামের উপর সার্চ ফিল্টার
        if search_query:
            regex_pattern = re.compile(search_query, re.IGNORECASE)
            query['$or'] = [
                {'tags': {'$regex': regex_pattern}},
                {'name': {'$regex': regex_pattern}}
            ]
            
        products_collection = db['products']
        cursor = products_collection.find(query).sort("createdAt", -1)
        
        products = []
        for doc in cursor:
            products.append({
                "id": str(doc['_id']),
                "name": doc.get('name', ''),
                "price": doc.get('price', 0),
                "image": doc.get('image', ''),
                "category": doc.get('category', ''),
                "tags": doc.get('tags', [])
            })
            
        return jsonify({"status": "success", "products": products}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
