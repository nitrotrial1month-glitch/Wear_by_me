import os
import requests
from flask import Blueprint, request, jsonify, redirect
from database import db, generate_unique_id

# 🚀 Blueprint for Auto Route Loader
discord_bp = Blueprint('discord_auth', __name__)

# Fetching environment variables from Render configuration
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI')

@discord_bp.route('/api/login/discord', methods=['GET'])
def discord_login_redirect():
    # Step 1: Redirect the user to Discord's OAuth2 authorization page
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify+email"
    )
    return redirect(discord_auth_url)


@discord_bp.route('/api/callback/discord', methods=['GET'])
def discord_callback():
    # Step 2: Receive the authorization code from Discord callback
    code = request.args.get('code')
    if not code:
        return "Authorization code missing from Discord", 400

    # Step 3: Exchange the authorization code for an access token
    token_url = "https://discord.com/api/oauth2/token"
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        token_response = requests.post(token_url, data=data, headers=headers).json()
        access_token = token_response.get('access_token')

        if not access_token:
            return f"Failed to obtain access token: {token_response.get('error_description', 'Unknown error')}", 400

        # Step 4: Use the access token to fetch the user's profile from Discord API
        user_url = "https://discord.com/api/v10/users/@me"
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_info = requests.get(user_url, headers=user_headers).json()

        email = user_info.get('email')
        name = user_info.get('global_name') or user_info.get('username') or "Discord User"

        if not email:
            return "Email permission is required from Discord to create an account.", 400

        # Step 5: Check MongoDB and handle user registration or login
        users_collection = db['users']
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            # If user exists, fetch their existing unique WBM_U_ID
            user_id = existing_user.get("user_id")
        else:
            # If new user, generate ID format: 11111WBMU111 (5 digits + WBMU + 3 digits)
            user_id = generate_unique_id('U')
            users_collection.insert_one({
                "user_id": user_id, 
                "name": name, 
                "email": email, 
                "provider": "Discord", 
                "role": "customer"
            })

        # Step 6: Deep Link redirect back to the Flutter app with user credentials
        flutter_deep_link = f"wearbyme://authed?user_id={user_id}&name={name}&email={email}"
        return redirect(flutter_deep_link)

    except Exception as e:
        return f"Authentication failed: {str(e)}", 500
        
