from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import instaloader
import os

app = Flask(__name__)
CORS(app)

# Instagram Loader Setup
L = instaloader.Instaloader(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# --- 1. PURANA DOWNLOADER (FB, IG Reels, etc.) ---
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title', 'Video'),
                "download_url": info.get('url'),
                "thumbnail": info.get('thumbnail'),
                "platform": info.get('extractor_key')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- 2. NAYA YOUTUBE/COOKING DOWNLOADER ---
# Ye upar wale code se hi handle ho jayega, bas Lovable ko URL bhejna hai

# --- 3. INSTAGRAM STORY VIEWER (With Cookie Support) ---
@app.route('/fetch-stories', methods=['POST'])
def fetch_stories():
    data = request.json
    username = data.get('username', '').replace('@', '').strip()
    session_id = data.get('session_id') # Agar aap Lovable se cookie bhejte ho

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Agar aapne session_id di hai toh login karega (Block se bachne ke liye)
        if session_id:
            L.context.set_cookie("sessionid", session_id)
        
        profile = instaloader.Profile.from_username(L.context, username)
        
        if profile.is_private:
            return jsonify({"error": "Account is Private!"}), 403
            
        stories_data = []
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                stories_data.append({
                    "url": item.video_url if item.is_video else item.display_url,
                    "is_video": item.is_video,
                    "thumbnail": item.display_url
                })
        
        if not stories_data:
            return jsonify({"message": "No active stories found."}), 200
            
        return jsonify({"stories": stories_data})

    except Exception as e:
        # Agar block ho gaya toh ye message aayega
        if "401" in str(e) or "login" in str(e).lower():
            return jsonify({"error": "Instagram Blocked! Please update Session ID/Cookie."}), 401
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
