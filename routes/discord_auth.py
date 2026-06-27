import os
from flask import Blueprint, request, jsonify
from database import db, generate_unique_id

discord_bp = Blueprint('discord_auth', __name__)

DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')

@discord_bp.route('/api/login/discord', methods=['POST'])
def discord_login():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        
        if not email:
            return jsonify({"status": "error", "message": "Email required for Discord"}), 400

        users_collection = db['users']
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            user_id = existing_user.get("user_id")
            message = "Discord Login successful"
        else:
            user_id = generate_unique_id()
            users_collection.insert_one({"user_id": user_id, "name": name, "email": email, "provider": "Discord", "role": "customer"})
            message = "Discord Account created successfully"

        return jsonify({"status": "success", "message": message, "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
