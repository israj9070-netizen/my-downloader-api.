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
            # Bot detection se bachne ke liye naye headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Direct link nikalne ka solid tarika
            download_url = None
            if 'url' in info:
                download_url = info['url']
            elif 'formats' in info:
                for f in reversed(info['formats']):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        download_url = f.get('url')
                        break
            
            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "direct_url": download_url,
                "duration": info.get('duration')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

