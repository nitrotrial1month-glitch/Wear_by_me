from flask import Blueprint, request, jsonify
from database import db, generate_unique_id
import datetime

seller_auth_bp = Blueprint('seller_auth', __name__)

# 🏪 ১. সেলার লগইন এপিআই (Dual Admin Bypass)
@seller_auth_bp.route('/api/seller/login', methods=['POST'])
def seller_login():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name', 'New Seller')

        if not email:
            return jsonify({"status": "error", "message": "Email is required!"}), 400

        # 👑 আপনার দুটো জিমেইলের জন্যই মাস্টার পারমিশন বাইপাস (NO KYC REQUIRED)
        if email.lower() in ["servernitrado59@gmail.com", "shubhamridha96@gmail.com", "test@gmail.com"]:
            return jsonify({
                "status": "success",
                "message": "Super Admin Access Granted",
                "seller_id": "9999WBM99A", 
                "name": "Super Admin",
                "seller_status": "Approved" 
            }), 200

        sellers_collection = db['sellers']
        existing_seller = sellers_collection.find_one({"email": email.lower()})

        if existing_seller:
            seller_id = existing_seller.get("seller_id")
            seller_status = existing_seller.get("status", "pending")
            message = "Login Success"
        else:
            seller_id = generate_unique_id('S')
            seller_status = "pending"
            
            new_seller_data = {
                "seller_id": seller_id, 
                "name": name,
                "email": email.lower(),
                "role": "seller",
                "status": seller_status,
                "joined_at": datetime.datetime.utcnow()
            }
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

# 🛡️ ২. সেলার KYC সাবমিট এপিআই
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
                "legal_name": data.get('legal_name'),            
                "business_name": data.get('business_name'),      
                "address": data.get('address'),                  
                "payout_upi": data.get('payout_upi'),            
                "id_type": data.get('id_type'),                  
                "document_number": data.get('id_number'),        
                "document_url": data.get('id_doc_url'),          
                "license_number": data.get('license_number'),    
                "license_url": data.get('license_doc_url'),      
                "selfie_url": data.get('selfie_url'),            
                "status": "pending"              
            }}
        )
        return jsonify({"status": "success", "message": "KYC Submitted Successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔍 ৩. সেলারের লাইভ স্ট্যাটাস চেক
@seller_auth_bp.route('/api/seller/status', methods=['GET'])
def get_seller_status():
    try:
        seller_id = request.args.get('seller_id')
        
        # আপনার স্পেশাল আইডির জন্য লাইভ বাইপাস
        if seller_id == "9999WBM99A":
            return jsonify({"status": "success", "seller_status": "Approved"}), 200
            
        seller = db['sellers'].find_one({"seller_id": seller_id})
        if seller:
            return jsonify({"status": "success", "seller_status": seller.get("status", "pending")}), 200
        return jsonify({"status": "error", "message": "Seller not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
# 👤 ৪. সেলার প্রোফাইল আপডেট
@seller_auth_bp.route('/api/seller/update_profile', methods=['POST'])
def update_profile():
    try:
        data = request.json
        db['sellers'].update_one(
            {"seller_id": data['seller_id']},
            {"$set": {
                "business_name": data.get('business_name'),
                "address": data.get('address'),
                "payout_upi": data.get('payout_upi'),
                "license_number": data.get('license_number')
            }}
        )
        return jsonify({"status": "success", "message": "Profile Updated Successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
