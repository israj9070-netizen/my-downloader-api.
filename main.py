import instaloader
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Instagram Loader Setup
L = instaloader.Instaloader()

# --- PURANA DOWNLOADER LOGIC ---
@app.route('/get-video-info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "download_url": info.get('url'),
                "source": info.get('extractor')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- NAYA STORY VIEWER LOGIC ---
@app.route('/fetch-stories', methods=['POST'])
def fetch_stories():
    data = request.json
    username = data.get('username', '').replace('@', '').strip()
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        if profile.is_private:
            return jsonify({"error": "Account is Private. Can't fetch stories anonymously."}), 403
            
        stories_data = []
        # Public stories fetch kar raha hai
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                stories_data.append({
                    "url": item.video_url if item.is_video else item.display_url,
                    "is_video": item.is_video,
                    "thumbnail": item.display_url
                })
        
        if not stories_data:
            return jsonify({"message": "No active stories found for this user."}), 200
            
        return jsonify({"stories": stories_data})

    except Exception as e:
        return jsonify({"error": "Instagram block or error: " + str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
