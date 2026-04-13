from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/fetch', methods=['GET'])
def fetch_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is missing"}), 400
    
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": info.get('url'),
                "duration": info.get('duration')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
