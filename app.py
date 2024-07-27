#!/usr/bin/env python
"""
Flask server for video-editor
"""
from flask import (
    Flask, 
    jsonify, 
    render_template, 
    request,
    Response,
    stream_with_context,
)
from flaskwebgui import FlaskUI
import os
from pathlib import Path
import sys
import logging
from video_editor import VideoEditor
from werkzeug.utils import secure_filename
import threading
import queue

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_browser_path():
    if sys.platform.startswith('win'):
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif sys.platform.startswith('darwin'):
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif sys.platform.startswith('linux'):
        return "/usr/bin/google-chrome-stable"
    else:
        raise EnvironmentError("Unsupported operating system")

def ensure_upload_folder_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Upload folder '{path}' is ready.")
    except Exception as e:
        print(f"Error creating upload directory: {e}")

# Create the Flask instance
app = Flask(__name__)

# Set upload folder to a directory in the user's home directory
home_directory = Path(os.path.expanduser('~'))
upload_folder = home_directory / 'VideoEditor' / 'tmp'
upload_folder.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(upload_folder)

ensure_upload_folder_exists(app.config['UPLOAD_FOLDER'])

# Settings variables
volume_threshold = 0.1
silence_jacket = 0.25
dynamic_silence_threshold = False
output_directory = str(upload_folder)  # Default output directory

# Queue to store log messages
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/receive_filename', methods=['POST'])
def receive_filename():
    global volume_threshold, silence_jacket, dynamic_silence_threshold, output_directory
    try:
        if 'video_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['video_file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            expanded_output_directory = os.path.expanduser(output_directory)
            video_editor = VideoEditor(file_path, dynamic_silence_threshold, silence_jacket, volume_threshold, expanded_output_directory)
            print(f"AFTER OUTPUT DIRECTORY: {expanded_output_directory}")
            video_editor.process_video()
            logging.info("Completed video editing")

            return jsonify({'message': f"Received and processed video: {filename}."})
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_settings', methods=['POST'])
def save_settings():
    global volume_threshold, silence_jacket, dynamic_silence_threshold, output_directory
    try:
        volume_threshold = float(request.form.get('volume_threshold', 0.1) or 0.1)
        silence_jacket = float(request.form.get('silence_jacket', 0.25) or 0.25)
        dynamic_silence_threshold = request.form.get('dynamic_threshold') == 'on'
        output_directory = request.form.get('output_directory', '~/VideoEditor/edited_videos') or '~/VideoEditor/edited_videos'
        output_directory = os.path.expanduser(output_directory)
        print(f"OUTPUT DIRECTORY: {output_directory}")

        return jsonify({'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/log_stream')
def log_stream():
    def generate():
        while True:
            log_entry = log_queue.get()
            yield f'data: {log_entry}\n\n'
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    queue_handler = QueueHandler()
    queue_handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(queue_handler)
    
    logging.info("Starting the Flask application")
    browser_path = get_browser_path()
    FlaskUI(
        app=app,
        server="flask",
        width=900,
        height=600,
        browser_path=browser_path
    ).run()
