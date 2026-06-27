import os
from flask import Blueprint, request, jsonify
from database import db, generate_unique_id

# Blueprint তৈরি করা (অটো লোডার এটিকেই খুঁজবে)
google_bp = Blueprint('google_auth', __name__)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

@google_bp.route('/api/login/google', methods=['POST'])
def google_login():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        
        if not email:
            return jsonify({"status": "error", "message": "Email required"}), 400

        users_collection = db['users']
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            user_id = existing_user.get("user_id")
            message = "Google Login successful"
        else:
            user_id = generate_unique_id()
            users_collection.insert_one({"user_id": user_id, "name": name, "email": email, "provider": "Google", "role": "customer"})
            message = "Google Account created successfully"

        return jsonify({"status": "success", "message": message, "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
