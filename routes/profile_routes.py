import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from database import db

profile_bp = Blueprint('profile_bp', __name__)

cloudinary.config(
    cloud_name="dsr2twtwd",
    api_key="783482566841957",
    api_secret="pb_LkF6p4FQBD2fwv4Yp8j-qIUI"
)

# 🔴 ইউনিভার্সাল আপলোড ফাংশন (ছবি এবং ভিডিও দুটোর জন্যই)
@profile_bp.route('/api/upload_media', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    media_type = request.form.get('type')  # 'profile', 'product_image', বা 'product_video'
    
    # ফাইলের ধরন অনুযায়ী ফোল্ডার সেট করা
    folder_name = "wear_by_me_media"
    resource_type = "image"
    
    if media_type == 'product_video':
        resource_type = "video"
        folder_name = "wear_by_me_videos"

    try:
        # Cloudinary-তে আপলোড (ছবি বা ভিডিও অটো ডিটেক্ট করবে)
        upload_result = cloudinary.uploader.upload(
            file, 
            resource_type=resource_type, 
            folder=folder_name
        )
        
        media_url = upload_result.get("secure_url")
        
        return jsonify({"status": "success", "url": media_url}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
      
