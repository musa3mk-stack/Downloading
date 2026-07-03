import os
from flask import Flask, render_template, request, jsonify

project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'ms_video_v4_render_api_2026'

@app.route('/')
def index():
    return render_template('index.html')

# 1. GYARA AKAN DOWNLOADER: Flask zai riqa dawo da Direct Download Link ne kawai
@app.route('/download', methods=['POST'])
def get_download_link():
    url = request.form.get('url')
    if not url: 
        return jsonify({'error': 'Please paste a valid video URL!'}), 400
    try:
        import yt_dlp
        
        # Saita yt_dlp don ya karbo asalin link ba tare da ya yi download a Server ba
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'quiet': True,
            'no_warnings': True,
            'skip_download': True  # Wannan zai hana shi yin download a Render server
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False) # download=False don guje wa ajiya a server
            video_url = info.get('url') # Wannan shi ne asalin direct link na bidiyon
            video_title = info.get('title', 'Downloaded_Video')
            
        return jsonify({
            'success': True, 
            'download_url': video_url, 
            'title': video_title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # An bar shi a port 8080 don gwaji a Pydroid3, idan zaka tura Render zai dauki port dinta
    app.run(debug=True, host='0.0.0.0', port=8080)
