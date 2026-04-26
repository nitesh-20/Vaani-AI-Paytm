"""
Simple token server for development.

In production, integrate this into your backend API.
This generates LiveKit access tokens for clients to join rooms.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for development

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.route('/api/token', methods=['POST'])
def generate_token():
    """Generate a LiveKit access token for a user."""
    auth_token = os.getenv("ORION_AUTH_TOKEN", "change-me-123")
    received_token = request.headers.get("X-Authorization")
    if received_token != auth_token:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.json
        room_name = data.get('roomName')
        user_name = data.get('userName')
        
        if not room_name or not user_name:
            return jsonify({'error': 'Missing roomName or userName'}), 400
        
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(user_name)
        token.with_name(user_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        
        # Generate JWT
        jwt_token = token.to_jwt()
        
        return jsonify({
            'token': jwt_token,
            'url': os.getenv('LIVEKIT_URL')
        })
        
    except Exception as e:
        print(f"Error generating token: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        print("❌ Missing LiveKit credentials. Please check your .env file.")
        exit(1)
    
    print("🚀 Token server running on http://localhost:3001")
    print("📝 Generating tokens for LiveKit rooms")
    app.run(host='0.0.0.0', port=3001, debug=False)
 
 
 
 
 
 
 
 
 
