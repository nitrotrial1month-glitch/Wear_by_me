from flask import Blueprint, request, jsonify
from database import db, generate_unique_id

# একটি ব্লুপ্রিন্ট তৈরি করা হলো (যাতে app.py এর অটো-লোডার একে খুঁজে পায়)
seller_auth_bp = Blueprint('seller_auth', __name__)

@seller_auth_bp.route('/api/seller/login', methods=['POST'])
def seller_login():
    try:
        data = request.get_json()
        email_or_phone = data.get('email') # ফ্লাটার থেকে আসা ইমেইল বা ফোন নম্বর
        name = data.get('name', 'New Seller') # প্রোফাইল ক্রিয়েশনের সময় নাম আসবে

        if not email_or_phone:
            return jsonify({"status": "error", "message": "Email or Phone is required!"}), 400

        # 👑 ১. Super Admin Bypass (আপনার জন্য)
        if email_or_phone == "servernitrado59@gmail.com":
            return jsonify({
                "status": "success",
                "message": "Admin Access Granted",
                "seller_id": "9999WBM99A", # আপনার অ্যাডমিন আইডি
                "name": "Super Admin",
                "role": "admin"
            }), 200

        # 🏪 ২. সাধারণ সেলার প্রসেস (MongoDB ডাটাবেস কানেকশন)
        sellers_collection = db['sellers']
        
        # ডাটাবেসে অলরেডি এই সেলার আছে কি না চেক করা হচ্ছে
        existing_seller = sellers_collection.find_one({
            "$or": [{"email": email_or_phone}, {"phone": email_or_phone}]
        })

        if existing_seller:
            seller_id = existing_seller.get("seller_id")
            seller_name = existing_seller.get("name", name)
            message = "Login Success"
        else:
            # 🔴 ইউজার নতুন হলে আপনার ইউনিক ফরম্যাট অনুযায়ী WBM_S_ID জেনারেট হবে (যেমন: 58291WBM592S)
            seller_id = generate_unique_id('S')
            
            # নতুন সেলারের ডেটাবেস এন্ট্রি
            new_seller_data = {
                "seller_id": seller_id, 
                "name": name,
                "role": "seller",
                "status": "pending" # প্রথম অবস্থায় KYC স্ট্যাটাস পেন্ডিং থাকবে
            }
            
            # ইমেইল নাকি ফোন নম্বর দিয়ে লগইন করেছে সেটা চেনা
            if "@" in email_or_phone:
                new_seller_data["email"] = email_or_phone.lower()
            else:
                new_seller_data["phone"] = email_or_phone

            sellers_collection.insert_one(new_seller_data)
            message = "Seller Account Created Successfully"

        # ফ্লাটার অ্যাপ যাতে লোকাল মেমোরিতে এই ইউনিক আইডি সেভ করে রাখতে পারে
        return jsonify({
            "status": "success", 
            "message": message, 
            "seller_id": seller_id,
            "name": name if not existing_seller else existing_seller.get("name")
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
        
