import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Allow all origins

# Configuration
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
COOKIES_PATH = os.getenv('COOKIES_PATH', 'cookies/cookies.txt')  # مسار ملف الكوكيز
valid_formats = os.getenv('FORMATS', 'mp4,webm').split(',')
valid_qualities = ['144', '240', '360', '480', '720', '1080', 'best']

# Ensure folders exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
if not os.path.exists(os.path.dirname(COOKIES_PATH)):
    os.makedirs(os.path.dirname(COOKIES_PATH))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality', 'best')

    # Validate input
    if not video_url or not format:
        return jsonify({"error": "الرجاء إدخال رابط الفيديو والتنسيق المطلوب!"}), 400

    if format not in valid_formats:
        return jsonify({"error": f"تنسيق الفيديو غير صالح! يرجى اختيار {', '.join(valid_formats)}"}), 400

    if quality not in valid_qualities:
        return jsonify({"error": f"جودة الفيديو غير صالحة! يرجى اختيار {', '.join(valid_qualities)}"}), 400

    # Configure yt-dlp options
    ydl_opts = {
        'format': f'bestvideo[height<={quality}][ext={format}]+bestaudio/best' if format == 'mp4' else 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'cookies': COOKIES_PATH,  # إضافة الكوكيز هنا
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        if not os.path.exists(file_path):
            return jsonify({"error": "الملف غير موجود!"}), 404

        # Send the file to the client
        response = send_from_directory(DOWNLOAD_FOLDER, os.path.basename(file_path), as_attachment=True)
        response.headers['Access-Control-Allow-Origin'] = '*'

        # Clean up the file after sending
        def remove_file():
            try:
                os.remove(file_path)
                logger.info(f"تم حذف الملف: {file_path}")
            except Exception as e:
                logger.error(f"حدث خطأ أثناء حذف الملف: {str(e)}")

        response.call_on_close(remove_file)
        return response

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"حدث خطأ أثناء التحميل: {str(e)}")
        return jsonify({"error": f"حدث خطأ أثناء التحميل: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"حدث خطأ غير متوقع: {str(e)}")
        return jsonify({"error": f"حدث خطأ غير متوقع: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)