import os
from flask import Blueprint, request, jsonify
from database import db, generate_unique_id

# 🚀 Blueprint তৈরি করা (আপনার app.py এর অটো লোডার এটিকেই খুঁজবে)
google_bp = Blueprint('google_auth', __name__)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

@google_bp.route('/api/login/google', methods=['POST'])
def google_login():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        profile_pic = data.get('profile_pic', '') # ফ্লাটার থেকে আসা প্রোফাইল পিকচার ইউআরএল (যদি থাকে)
        
        if not email:
            return jsonify({"status": "error", "message": "Email required for Google Login"}), 400

        users_collection = db['users']
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            # ইউজার আগে থেকেই থাকলে তার ডাটাবেজের আসল আইডি নেওয়া হবে
            user_id = existing_user.get("user_id")
            message = "Google Login successful"
            
            # প্রয়োজন হলে ডাটাবেজে নাম বা ছবি আপডেট করে নেওয়া (ঐচ্ছিক)
            users_collection.update_one(
                {"email": email},
                {"$set": {"name": name}}
            )
        else:
            # 🔴 ইউজার নতুন হলে আপনার নতুন ফরম্যাট অনুযায়ী U_ID জেনারেট হবে (যেমন: 48291WBMU592)
            user_id = generate_unique_id('U')
            
            users_collection.insert_one({
                "user_id": user_id, 
                "name": name, 
                "email": email, 
                "provider": "Google", 
                "role": "customer",
                "profile_pic": profile_pic
            })
            message = "Google Account created successfully"

        # ফ্লাটার অ্যাপ যাতে লোকাল মেমোরিতে ডেটা সেভ করতে পারে, তাই রেসপন্সে আইডি ও নাম পাঠানো হচ্ছে
        return jsonify({
            "status": "success", 
            "message": message, 
            "user_id": user_id,
            "name": name,
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
