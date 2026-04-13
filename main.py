from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/info', methods=['POST'])
def get_video_info():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'noplaylist': True,
            # Naya bypass logic
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'addheader': [
                ('Referer', 'https://www.google.com/'),
                ('Accept-Language', 'en-US,en;q=0.9'),
            ],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Pehle info nikaalo
            info = ydl.extract_info(video_url, download=False)
            
            # YouTube ke liye direct URL dhoondne ka best tarika
            download_url = None
            formats = info.get('formats', [])
            
            # Sabse acchi quality wala link jo video + audio dono ho
            valid_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
            if valid_formats:
                download_url = valid_formats[-1].get('url')
            else:
                download_url = info.get('url')

            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "direct_url": download_url,
                "duration": info.get('duration')
            })
    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm" in error_msg:
            return jsonify({"error": "YouTube is blocking the request. Try a Facebook link to verify it works!"}), 403
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


