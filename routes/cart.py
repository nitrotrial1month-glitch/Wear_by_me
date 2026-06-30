from flask import Blueprint, request, jsonify
from database import db

cart_bp = Blueprint('cart_bp', __name__)

# 🔴 ১. কার্টে প্রোডাক্ট যোগ করা বা কোয়ান্টিটি বাড়ানো
@cart_bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        name = data.get('name')
        price = data.get('price')
        image = data.get('image')
        quantity = data.get('quantity', 1)

        if not user_id or not product_id:
            return jsonify({"status": "error", "message": "User ID and Product ID are required!"}), 400

        cart_collection = db['cart']
        
        # ইউজার এই প্রোডাক্টটি আগে থেকেই কার্টে যোগ করেছে কি না চেক করা
        existing_item = cart_collection.find_one({"user_id": user_id, "product_id": product_id})
        
        if existing_item:
            # কার্টে থাকলে কোয়ান্টিটি বাড়িয়ে দেওয়া
            cart_collection.update_one(
                {"_id": existing_item["_id"]},
                {"$inc": {"quantity": quantity}}
            )
        else:
            # না থাকলে নতুন আইটেম হিসেবে কার্টে ইনসার্ট করা
            cart_collection.insert_one({
                "user_id": user_id,
                "product_id": product_id,
                "name": name,
                "price": price,
                "image": image,
                "quantity": quantity
            })

        return jsonify({"status": "success", "message": "Item added to cart successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 🔴 ২. নির্দিষ্ট ইউজারের কার্টের সব প্রোডাক্ট দেখা
@cart_bp.route('/api/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    try:
        cart_collection = db['cart']
        cursor = cart_collection.find({"user_id": user_id})
        
        cart_items = []
        total_amount = 0
        
        for doc in cursor:
            item_total = doc.get('price', 0) * doc.get('quantity', 1)
            total_amount += item_total
            cart_items.append({
                "id": str(doc['_id']),
                "product_id": doc.get('product_id'),
                "name": doc.get('name', ''),
                "price": doc.get('price', 0),
                "image": doc.get('image', ''),
                "quantity": doc.get('quantity', 1)
            })
            
        return jsonify({
            "status": "success", 
            "cart": cart_items,
            "total_amount": total_amount
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 🔴 ৩. কার্ট থেকে কোনো প্রোডাক্ট রিমুভ (ডিলিট) করা
@cart_bp.route('/api/cart/<user_id>/<product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    try:
        cart_collection = db['cart']
        cart_collection.delete_one({"user_id": user_id, "product_id": product_id})
        return jsonify({"status": "success", "message": "Item removed from cart!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
