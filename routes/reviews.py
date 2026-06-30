from flask import Blueprint, request, jsonify
from database import db
import datetime
from bson.objectid import ObjectId

reviews_bp = Blueprint('reviews_bp', __name__)

# রিভিউ জমা দেওয়ার API
@reviews_bp.route('/api/reviews', methods=['POST'])
def add_review():
    try:
        data = request.json
        product_id = data.get('product_id')
        user_name = data.get('user_name', 'Anonymous')
        rating = data.get('rating', 5)
        comment = data.get('comment', '')

        if not product_id:
            return jsonify({"status": "error", "message": "Product ID is required!"}), 400

        review_doc = {
            "product_id": product_id,
            "user_name": user_name,
            "rating": rating,
            "comment": comment,
            "createdAt": datetime.datetime.utcnow()
        }
        
        db['reviews'].insert_one(review_doc)
        return jsonify({"status": "success", "message": "Review added successfully!"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# নির্দিষ্ট প্রোডাক্টের রিভিউ দেখার API
@reviews_bp.route('/api/reviews/<product_id>', methods=['GET'])
def get_reviews(product_id):
    try:
        cursor = db['reviews'].find({"product_id": product_id}).sort("createdAt", -1)
        reviews = []
        for doc in cursor:
            reviews.append({
                "id": str(doc['_id']),
                "user_name": doc.get('user_name', ''),
                "rating": doc.get('rating', 0),
                "comment": doc.get('comment', ''),
                "date": doc.get('createdAt').strftime("%Y-%m-%d") if doc.get('createdAt') else ""
            })
        return jsonify({"status": "success", "reviews": reviews}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
