from flask import Blueprint, request, jsonify

# একটি ব্লুপ্রিন্ট তৈরি করা হলো (যাতে app.py এর অটো-লোডার একে খুঁজে পায়)
seller_auth_bp = Blueprint('seller_auth', __name__)

@seller_auth_bp.route('/api/seller/login', methods=['POST'])
def seller_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # টেস্টিংয়ের জন্য ডামি ভেরিফিকেশন (পরে এখানে আপনার MongoDB ডাটাবেস চেক করার কোড বসবে)
        if email == "test@seller.com" and password == "123456":
            return jsonify({
                "message": "Login Success", 
                "token": "abcd123_seller_token_for_wearbyme"
            }), 200
        else:
            return jsonify({
                "message": "Invalid Email or Password"
            }), 401

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
      
