from flask import Blueprint, request, jsonify
from database import db, generate_unique_id
import datetime

seller_auth_bp = Blueprint('seller_auth', __name__)

# 🏪 ১. সেলার লগইন এপিআই (With Test & Admin Bypass)
@seller_auth_bp.route('/api/seller/login', methods=['POST'])
def seller_login():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name', 'New Seller')

        if not email:
            return jsonify({"status": "error", "message": "Email is required!"}), 400

        # 🚀 Super Admin & Testing Bypass (NO KYC REQUIRED)
        if email in ["servernitrado59@gmail.com", "test@gmail.com"]:
            return jsonify({
                "status": "success",
                "message": "Admin Access Granted",
                "seller_id": "9999WBM99A",
                "name": "WBM Tester",
                "seller_status": "Approved" # ডাইরেক্ট অ্যাপ্রুভড
            }), 200

        sellers_collection = db['sellers']
        existing_seller = sellers_collection.find_one({"email": email.lower()})

        if existing_seller:
            seller_id = existing_seller.get("seller_id")
            seller_status = existing_seller.get("status", "pending")
            message = "Login Success"
        else:
            seller_id = generate_unique_id('S')
            seller_status = "pending" # নতুন সেলারদের ডিফল্ট স্ট্যাটাস
            
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

# 🛡️ ২. সেলার KYC সাবমিট এপিআই (High-Security)
@seller_auth_bp.route('/api/seller/submit_kyc', methods=['POST'])
def submit_kyc():
    try:
        data = request.get_json()
        seller_id = data.get('seller_id')
        
        if not seller_id:
            return jsonify({"status": "error", "message": "Seller ID missing!"}), 400
            
        # ডাটাবেসে সেলারের সমস্ত সিকিউরড তথ্য আপডেট করা হচ্ছে
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
                "status": "pending" # সাবমিটের পর স্টাফদের জন্য পেন্ডিং              
            }}
        )
        return jsonify({"status": "success", "message": "High-Security KYC Submitted!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔍 ৩. সেলারের লাইভ স্ট্যাটাস চেক করার এপিআই
@seller_auth_bp.route('/api/seller/status', methods=['GET'])
def get_seller_status():
    try:
        seller_id = request.args.get('seller_id')
        
        # 🚀 টেস্টিং আইডির জন্য স্পেশাল বাইপাস
        if seller_id == "9999WBM99A":
            return jsonify({"status": "success", "seller_status": "Approved"}), 200
            
        seller = db['sellers'].find_one({"seller_id": seller_id})
        if seller:
            return jsonify({"status": "success", "seller_status": seller.get("status", "pending")}), 200
        return jsonify({"status": "error", "message": "Seller not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
