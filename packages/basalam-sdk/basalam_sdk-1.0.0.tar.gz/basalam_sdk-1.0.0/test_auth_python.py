#!/usr/bin/env python3
"""
Test script for Basalam OAuth Authorization Code flow using the SDK.

This script demonstrates how to:
1. Create an AuthorizationCode instance
2. Get the authorization URL
3. Exchange an authorization code for a token
4. Display the token information

Usage:
1. Run this script
2. Open the generated authorization URL in your browser
3. Complete the authorization process
4. Copy the 'code' parameter from the redirect URL
5. Paste it when prompted

Requirements:
- Install the basalam-sdk package or ensure src/basalam_sdk is in your Python path
"""

import os
import sys
from urllib.parse import urlparse, parse_qs

# Add the src directory to the Python path to import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from basalam_sdk.auth import AuthorizationCode

# Configuration
CLIENT_ID = os.getenv("BASALAM_CLIENT_ID", "1048")
CLIENT_SECRET = os.getenv("BASALAM_CLIENT_SECRET", "aStxfKmpsdD1WaCgIQPa0Nt3owDhGQ7ZXZ9KjNtl")
REDIRECT_URI = os.getenv("BASALAM_REDIRECT_URI", "http://localhost:8000/auth/callback")
SCOPE = "vendor.product.read customer.profile.read"


def main():
    """Main function to test the OAuth flow."""
    print("=" * 60)
    print("Basalam OAuth Authorization Code Flow Test")
    print("=" * 60)
    
    # Step 1: Create AuthorizationCode instance
    print("\n1. Creating AuthorizationCode instance...")
    auth = AuthorizationCode(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,        scopes=SCOPE.split()
    )
    print("✓ AuthorizationCode instance created successfully")
    
    # Step 2: Get authorization URL
    print("\n2. Generating authorization URL...")
    state = "test_state_123"  # Optional state parameter for security
    auth_url = auth.get_authorization_url(state=state)
    
    print(f"✓ Authorization URL generated:")
    print(f"   {auth_url}")
    print(f"\n📋 Please:")
    print(f"   1. Open the URL above in your browser")
    print(f"   2. Complete the authorization process")
    print(f"   3. Copy the 'code' parameter from the redirect URL")
    print(f"   4. Come back here and paste it below")
    
    # Step 3: Get authorization code from user
    print("\n3. Waiting for authorization code...")
    while True:
        try:
            user_input = input("\nPaste the redirect URL or just the code: ").strip()
            
            if not user_input:
                print("❌ Please provide the authorization code or redirect URL")
                continue
            
            # Try to extract code from URL if full URL is provided
            if user_input.startswith('http'):
                parsed_url = urlparse(user_input)
                query_params = parse_qs(parsed_url.query)
                if 'code' in query_params:
                    auth_code = query_params['code'][0]
                else:
                    print("❌ No 'code' parameter found in the URL")
                    continue
            else:
                # Assume the input is just the code
                auth_code = user_input
            
            break
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            return
        except Exception as e:
            print(f"❌ Error processing input: {e}")
            continue
    
    # Step 4: Exchange code for token
    print(f"\n4. Exchanging authorization code for token...")
    print(f"   Code: {auth_code[:10]}...")
    
    try:
        # Use the synchronous method as requested
        token_info = auth.get_token_sync(code=auth_code)
        
        print("✓ Token retrieved successfully!")
        print("\n5. Token Information:")
        print("-" * 40)
        print(f"Access Token: {token_info.access_token[:20]}...")
        print(f"Token Type: {token_info.token_type}")
        print(f"Expires In: {token_info.expires_in} seconds")
        print(f"Scope: {token_info.scope}")
        print(f"Created At: {token_info.created_at}")
        print(f"Expires At: {token_info.expires_at}")
        print(f"Is Expired: {token_info.is_expired}")
        
        if token_info.refresh_token:
            print(f"Refresh Token: {token_info.refresh_token[:20]}...")
        
        print(f"\n📝 Full Token (JSON format):")
        print("-" * 40)
        import json
        token_dict = {
            "access_token": token_info.access_token,
            "token_type": token_info.token_type,
            "expires_in": token_info.expires_in,
            "scope": token_info.scope,
            "created_at": token_info.created_at,
            "expires_at": token_info.expires_at,
        }
        if token_info.refresh_token:
            token_dict["refresh_token"] = token_info.refresh_token
            
        print(json.dumps(token_dict, indent=2))
        
        print(f"\n🎉 OAuth flow completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to exchange code for token: {e}")
        print(f"   Make sure the code is valid and hasn't expired")
        return


if __name__ == "__main__":
    main() 