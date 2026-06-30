from flask import Blueprint, request, jsonify
from database import db
import datetime

qa_bp = Blueprint('qa_bp', __name__)

# প্রশ্ন করার API
@qa_bp.route('/api/qa', methods=['POST'])
def ask_question():
    try:
        data = request.json
        product_id = data.get('product_id')
        user_name = data.get('user_name', 'User')
        question = data.get('question', '')

        if not product_id or not question:
            return jsonify({"status": "error", "message": "Product ID and Question are required!"}), 400

        qa_doc = {
            "product_id": product_id,
            "user_name": user_name,
            "question": question,
            "answer": "", # সেলার বা অ্যাডমিন পরে এর উত্তর দেবে
            "is_answered": False,
            "createdAt": datetime.datetime.utcnow()
        }
        
        db['qa'].insert_one(qa_doc)
        return jsonify({"status": "success", "message": "Question submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# নির্দিষ্ট প্রোডাক্টের প্রশ্নোত্তর দেখার API
@qa_bp.route('/api/qa/<product_id>', methods=['GET'])
def get_qa(product_id):
    try:
        cursor = db['qa'].find({"product_id": product_id}).sort("createdAt", -1)
        qa_list = []
        for doc in cursor:
            qa_list.append({
                "id": str(doc['_id']),
                "user_name": doc.get('user_name', ''),
                "question": doc.get('question', ''),
                "answer": doc.get('answer', ''),
                "is_answered": doc.get('is_answered', False),
                "date": doc.get('createdAt').strftime("%Y-%m-%d") if doc.get('createdAt') else ""
            })
        return jsonify({"status": "success", "qa_list": qa_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      
# ইউজারের নিজের করা সব প্রশ্ন দেখার API
@qa_bp.route('/api/qa/user/<user_name>', methods=['GET'])
def get_user_qa(user_name):
    try:
        cursor = db['qa'].find({"user_name": user_name}).sort("createdAt", -1)
        qa_list = []
        for doc in cursor:
            qa_list.append({
                "id": str(doc['_id']),
                "product_id": doc.get('product_id', ''),
                "question": doc.get('question', ''),
                "answer": doc.get('answer', ''),
                "is_answered": doc.get('is_answered', False),
                "date": doc.get('createdAt').strftime("%Y-%m-%d") if doc.get('createdAt') else ""
            })
        return jsonify({"status": "success", "qa_list": qa_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
