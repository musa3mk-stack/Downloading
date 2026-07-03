import os
import threading
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify

project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'ms_video_v4_premium_english_final'

APP_DOWNLOAD_DIR = os.path.join(project_root, 'downloads')
os.makedirs(APP_DOWNLOAD_DIR, exist_ok=True)

PHONE_STORAGE = '/storage/emulated/0'

# Global variable to store active download percentage mapping
download_progress = {"status": "none", "percentage": 0, "file": ""}

# Real-time bytes processing hook for yt_dlp monitoring
def ytdl_progress_hook(d):
    global download_progress
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            percent = int((downloaded_bytes / total_bytes) * 100)
            download_progress["status"] = "active"
            download_progress["percentage"] = percent
    elif d['status'] == 'finished':
        download_progress["status"] = "finished"
        download_progress["percentage"] = 100
        download_progress["file"] = os.path.basename(d['filename'])

def run_downloader_thread(url):
    global download_progress
    try:
        import yt_dlp
        ydl_opts = {
            'outtmpl': os.path.join(APP_DOWNLOAD_DIR, '%(title).50s.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'no_warnings': True,
            'quiet': True,
            'restrictfilenames': True,
            'progress_hooks': [ytdl_progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        download_progress["status"] = "error"
        download_progress["percentage"] = 0
        download_progress["file"] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    global download_progress
    url = request.form.get('url')
    if not url: 
        return jsonify({'error': 'Please paste a valid video URL!'}), 400
    
    download_progress = {"status": "started", "percentage": 0, "file": ""}
    
    threading.Thread(target=run_downloader_thread, args=(url,)).start()
    return jsonify({'started': True})

# Endpoint to fetch background downloading updates periodically
@app.route('/progress')
def get_progress():
    global download_progress
    return jsonify(download_progress)

@app.route('/stream/<filename>')
def stream_downloaded(filename):
    return send_from_directory(APP_DOWNLOAD_DIR, filename)

@app.route('/stream-local')
def stream_local_file():
    file_path = request.args.get('path')
    if file_path and os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return send_from_directory(directory, filename)
    return "File not found", 404

# TSARI IRIN NA MX PLAYER: Clean English configuration folder sorting
@app.route('/list-downloads')
def list_downloads():
    folder_structure = {}
    
    # 1. App Downloads Folder - Translated completely to English
    app_downloads = []
    try:
        if os.path.exists(APP_DOWNLOAD_DIR):
            for f in os.listdir(APP_DOWNLOAD_DIR):
                if f.endswith(('.mp4', '.mkv', '.3gp', '.webm')):
                    app_downloads.append({
                        'name': f,
                        'path': os.path.join(APP_DOWNLOAD_DIR, f),
                        'is_app_download': True
                    })
    except: pass
    folder_structure['📥 App Downloaded Videos'] = app_downloads

    # 2. Local Storage Folders - Structured cleanly in English layout
    target_folders = ['Download', 'Movies', 'DCIM', 'Pictures', 'WhatsApp/Media/WhatsApp Video']
    for target in target_folders:
        search_path = os.path.join(PHONE_STORAGE, target)
        if os.path.exists(search_path):
            current_folder_videos = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith(('.mp4', '.mkv', '.3gp', '.webm')):
                        current_folder_videos.append({
                            'name': file,
                            'path': os.path.join(root, file),
                            'is_app_download': False
                        })
            if current_folder_videos:
                folder_structure[f"📂 Folder: {target}"] = current_folder_videos

    return jsonify({'folders': folder_structure})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
