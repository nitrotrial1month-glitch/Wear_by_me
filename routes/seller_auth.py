from flask import Blueprint, request, jsonify
from database import db, generate_unique_id

seller_auth_bp = Blueprint('seller_auth', __name__)

# 🏪 ১. সেলার লগইন এপিআই
@seller_auth_bp.route('/api/seller/login', methods=['POST'])
def seller_login():
    try:
        data = request.get_json()
        email_or_phone = data.get('email')
        name = data.get('name', 'New Seller')

        if not email_or_phone:
            return jsonify({"status": "error", "message": "Email or Phone is required!"}), 400

        # Super Admin Bypass
        if email_or_phone == "servernitrado59@gmail.com":
            return jsonify({
                "status": "success",
                "message": "Admin Access Granted",
                "seller_id": "9999WBM99A",
                "name": "Super Admin",
                "seller_status": "Approved"
            }), 200

        sellers_collection = db['sellers']
        existing_seller = sellers_collection.find_one({
            "$or": [{"email": email_or_phone}, {"phone": email_or_phone}]
        })

        if existing_seller:
            seller_id = existing_seller.get("seller_id")
            seller_name = existing_seller.get("name", name)
            seller_status = existing_seller.get("status", "pending")
            message = "Login Success"
        else:
            seller_id = generate_unique_id('S')
            seller_status = "pending" # ডিফল্ট স্ট্যাটাস পেন্ডিং থাকবে
            
            new_seller_data = {
                "seller_id": seller_id, 
                "name": name,
                "role": "seller",
                "status": seller_status,
                "business_name": "",
                "document_number": "",
                "address": "",
                "selfie_url": "",
                "document_url": ""
            }
            
            if "@" in email_or_phone:
                new_seller_data["email"] = email_or_phone.lower()
            else:
                new_seller_data["phone"] = email_or_phone

            sellers_collection.insert_one(new_seller_data)
            message = "Seller Account Created"

        return jsonify({
            "status": "success", 
            "message": message, 
            "seller_id": seller_id,
            "name": existing_seller.get("name", name) if existing_seller else name,
            "seller_status": seller_status
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🛡️ ২. সেলার KYC সাবমিট এপিআই (নতুন ফিচার)
@seller_auth_bp.route('/api/seller/submit_kyc', methods=['POST'])
def submit_kyc():
    try:
        data = request.get_json()
        seller_id = data.get('seller_id')
        
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID missing!"}), 400
            
        db['sellers'].update_one(
            {"seller_id": seller_id},
            {"$set": {
                "business_name": data.get('business_name'),
                "document_number": data.get('document_number'),
                "address": data.get('address'),
                "selfie_url": data.get('selfie_url'),
                "document_url": data.get('document_url'),
                "status": "pending" # স্টাফদের ভেরিফিকেশনের জন্য পেন্ডিং থাকবে
            }}
        )
        return jsonify({"status": "success", "message": "KYC Submitted! Waiting for staff approval."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔍 ৩. সেলারের লাইভ স্ট্যাটাস চেক করার এপিআই (নতুন ফিচার)
@seller_auth_bp.route('/api/seller/status', methods=['GET'])
def get_seller_status():
    try:
        seller_id = request.args.get('seller_id')
        seller = db['sellers'].find_one({"seller_id": seller_id})
        if seller:
            return jsonify({"status": "success", "seller_status": seller.get("status", "pending")}), 200
        return jsonify({"status": "error", "message": "Seller not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
