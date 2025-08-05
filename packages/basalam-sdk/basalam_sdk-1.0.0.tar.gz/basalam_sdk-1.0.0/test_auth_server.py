#!/usr/bin/env python3
"""
Flask server to test Basalam OAuth Authorization Code flow.

Simple OAuth flow:
- GET /start-auth: Create auth URL and redirect user to Basalam
- GET /auth/callback: Handle callback, exchange code for token
"""

import os
import sys
import json
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

# Add the src directory to the Python path to import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from basalam_sdk.auth import AuthorizationCode

app = Flask(__name__)
CORS(app)

# Configuration
CLIENT_ID = os.getenv("BASALAM_CLIENT_ID", "1048")
CLIENT_SECRET = os.getenv("BASALAM_CLIENT_SECRET", "aStxfKmpsdD1WaCgIQPa0Nt3owDhGQ7ZXZ9KjNtl")
REDIRECT_URI = os.getenv("BASALAM_REDIRECT_URI", "http://localhost:8005/auth/callback")
SCOPE = "vendor.product.read customer.profile.read"

# Global AuthorizationCode instance
auth_instance = None


@app.route('/start-auth')
def start_auth():
    """Create auth URL and redirect user to Basalam authorization page."""
    global auth_instance
    
    try:
        # Create AuthorizationCode instance
        auth_instance = AuthorizationCode(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scopes=SCOPE.split()
        )
        
        # Create auth URL and redirect user
        auth_url = auth_instance.get_authorization_url(state="test_state")
        print(f"Redirecting to: {auth_url}")
        return redirect(auth_url)
        
    except Exception as e:
        return jsonify({'error': f'Failed to start auth: {str(e)}'}), 500


@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback and exchange code for token."""
    global auth_instance
    
    # Get code from callback URL
    code = request.args.get('code')
    print(f"Code: {code}")
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': f'OAuth error: {error}'}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    try:
        # Ensure auth instance exists
        if not auth_instance:
            auth_instance = AuthorizationCode(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scopes=SCOPE.split()
            )
            print(f"Auth instance: {auth_instance}")
            print(f"Auth instance: {auth_instance.get_authorization_url(state='test_state')}")
            print(f"Auth scope: {auth_instance.scope}")
            print(f"Auth instance: {auth_instance.client_id}")
            print(f"Auth instance: {auth_instance.client_secret}")

        print(f"Auth scope: {auth_instance.scope}")
        print(f"Auth instance: {auth_instance.client_id}")
        print(f"Auth instance: {auth_instance.client_secret}")
        print(f"Auth instance: {auth_instance.redirect_uri}")
        # Exchange code for token
        token_info = auth_instance.get_token_sync(code=code)
        print(f"Token info: {token_info}")
        
        # Return token data
        token_data = {
            'access_token': token_info.access_token,
            'token_type': token_info.token_type,
            'expires_in': token_info.expires_in,
            'scope': token_info.scope,
            'granted_scopes': list(token_info.granted_scopes)
        }
        
        if token_info.refresh_token:
            token_data['refresh_token'] = token_info.refresh_token
        
        print(f"Token obtained: {token_info.access_token[:20]}...")
        return jsonify({
            'success': True,
            'message': 'Token obtained successfully',
            'token': token_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Token exchange failed: {str(e)}'}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Get the current configuration."""
    return jsonify({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'message': 'Current configuration'
    })


if __name__ == '__main__':
    print(f"🚀 Start OAuth: http://localhost:8005/start-auth")
    app.run(debug=True, host='0.0.0.0', port=8005) 