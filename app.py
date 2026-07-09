import os
import json
from flask import Flask, render_template, send_from_directory, abort, jsonify

# ---------------------------------------------------------
# FZ Video Download — Backend (Flask)
# Wannan app yana bawa mutane damar duba da sauke bidiyoyin
# da ke ajiye a wannan server ɗin kai tsaye. Ba ya cire
# bidiyo daga wata website ta waje (YouTube, Facebook, da sauransu).
# ---------------------------------------------------------

project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')
videos_dir = os.path.join(static_dir, 'videos')
videos_json_path = os.path.join(project_root, 'videos.json')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'fz_video_download_v1_2026'


def load_videos():
    """Karanta jerin bidiyoyi daga videos.json (yana aiki kamar sauƙaƙƙen database)."""
    if not os.path.exists(videos_json_path):
        return []
    with open(videos_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_video(video_id):
    for v in load_videos():
        if str(v.get('id')) == str(video_id):
            return v
    return None


# ---------- SHAFIN FARKO (SPLASH) ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- JERIN BIDIYOYI ----------
@app.route('/home')
def home():
    videos = load_videos()
    return render_template('home.html', videos=videos)


# ---------- SHAFIN KALLON BIDIYO GUDA DAYA ----------
@app.route('/video/<video_id>')
def video_player(video_id):
    video = find_video(video_id)
    if not video:
        abort(404)
    return render_template('video_player.html', video=video)


# ---------- SHAFIN DOWNLOADS (JERIN DUK ABIN DA ZA A SAUKE) ----------
@app.route('/downloads')
def downloads():
    videos = load_videos()
    return render_template('downloads.html', videos=videos)


# ---------- API: DAWO DA BAYANIN BIDIYOYI A FORMAR JSON ----------
@app.route('/api/videos')
def api_videos():
    return jsonify(load_videos())


# ---------- ANNAN NE AKE SAUKE FAYIL ɗIN BIDIYO KAI TSAYE ----------
@app.route('/download/<video_id>')
def download_video(video_id):
    video = find_video(video_id)
    if not video:
        abort(404)
    filename = video.get('filename')
    if not os.path.exists(os.path.join(videos_dir, filename)):
        abort(404, description="Fayil ɗin bidiyo bai samu a server ba.")
    return send_from_directory(videos_dir, filename, as_attachment=True)


if __name__ == '__main__':
    # Na gwaji a local (Pydroid3/kwamfuta), idan an tura Render/wani host
    # zai amfani da PORT da environment ta bayar.
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
