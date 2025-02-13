import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

# إعداد نظام التسجيل (Logging)
logging.basicConfig(
    level=logging.INFO,  # ضبط مستوى السجلات إلى INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة تطبيق Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")
CORS(app)

# **تحديد المسارات والمجلدات**
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')
COOKIES_PATH = os.path.join(BASE_DIR, 'Kick', 'cookies.txt')  # 🔹 مسار ملف الكوكيز

valid_formats = ['mp4', 'webm']
valid_qualities = ['144', '240', '360', '480', '720', '1080', 'best']

# إنشاء مجلد التنزيلات إذا لم يكن موجودًا
try:
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
        logger.info(f"Created download folder: {DOWNLOAD_FOLDER}")
    os.chmod(DOWNLOAD_FOLDER, 0o755)
    logger.info("Download directory setup completed successfully")
except Exception as e:
    logger.error(f"Failed to setup download directory: {str(e)}")
    raise

@app.route('/')
def home():
    logger.debug("Loading home page")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return "Error loading page", 500

@app.route('/download', methods=['GET'])
def download():
    try:
        video_url = request.args.get('url')
        format = request.args.get('format', 'mp4')
        quality = request.args.get('quality', 'best')

        logger.info(f"Download request: URL={video_url}, Format={format}, Quality={quality}")

        if not video_url:
            return jsonify({"error": "الرجاء إدخال رابط الفيديو"}), 400

        if format not in valid_formats:
            return jsonify({"error": f"تنسيق غير صالح. التنسيقات المتاحة: {', '.join(valid_formats)}"}), 400

        if quality not in valid_qualities:
            return jsonify({"error": f"جودة غير صالحة. الجودات المتاحة: {', '.join(valid_qualities)}"}), 400

        # **إعداد yt-dlp مع ملف الكوكيز**
        ydl_opts = {
            'format': f'bestvideo[height<={quality}][ext={format}]+bestaudio/best[ext=m4a]' if quality != 'best' else 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'merge_output_format': format if format == 'mp4' else None,
            'restrictfilenames': True,
            'noplaylist': True,
            'cookiefile': COOKIES_PATH,  # 🔹 استخدام ملف الكوكيز
        }

        logger.debug(f"yt-dlp options: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info_dict)

                if not os.path.exists(file_path):
                    logger.error(f"Downloaded file not found: {file_path}")
                    return jsonify({"error": "فشل في تحميل الملف"}), 404

                logger.info(f"File downloaded successfully: {file_path}")

                response = send_from_directory(
                    DOWNLOAD_FOLDER,
                    os.path.basename(file_path),
                    as_attachment=True
                )

                def cleanup():
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logger.info(f"Cleaned up file: {file_path}")
                    except Exception as e:
                        logger.error(f"Cleanup error: {str(e)}")

                response.call_on_close(cleanup)
                return response

            except Exception as ydl_error:
                logger.error(f"yt-dlp error: {str(ydl_error)}")
                return jsonify({"error": f"فشل في تحميل الفيديو: {str(ydl_error)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    logger.debug(f"Serving static file: {filename}")
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
