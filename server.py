import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

# Set up logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
valid_formats = ['mp4', 'webm']
valid_qualities = ['144', '240', '360', '480', '720', '1080', 'best']

# Ensure download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    logger.info(f"Created download folder: {DOWNLOAD_FOLDER}")

@app.route('/')
def home():
    logger.debug("Loading home page")
    return render_template('index.html')

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

        ydl_opts = {
            'format': f'bestvideo[height<={quality}][ext={format}]+bestaudio/best[ext=m4a]' if quality != 'best' else 'best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'merge_output_format': format,
            'restrictfilenames': True,
            'noplaylist': True,
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

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")