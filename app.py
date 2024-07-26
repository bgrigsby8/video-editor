#!/usr/bin/env python
"""
Flask server for video-editor
"""
from flask import (
	Flask, 
	jsonify, 
	render_template, 
	request,
	send_from_directory,
)
from flaskwebgui import FlaskUI
import os
from pathlib import Path
import sys
from video_editor import VideoEditor
from werkzeug.utils import secure_filename

def get_browser_path():
    if sys.platform.startswith('win'):
        # Path for Chrome on Windows
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif sys.platform.startswith('darwin'):
        # Path for Chrome on macOS
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif sys.platform.startswith('linux'):
        # Path for Chrome on Linux
        return "/usr/bin/google-chrome-stable"
    else:
        raise EnvironmentError("Unsupported operating system")

def ensure_upload_folder_exists():
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Upload folder '{app.config['UPLOAD_FOLDER']}' is ready.")
    except Exception as e:
        print(f"Error creating upload directory: {e}")

# Create the Flask instance
app = Flask(__name__)

current_directory = Path(__file__).parent
upload_folder = current_directory / 'tmp'
upload_folder.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(upload_folder)

ensure_upload_folder_exists()

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/receive_filename', methods=['POST'])
def receive_filename():
    try:
        # Check if the post request has the file part
        if 'video_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['video_file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the video
            video_editor = VideoEditor(file_path)
            video_editor.process_video()
            print("Completed video editing")

            # Optionally, you can also serve the processed video to download or preview
            return jsonify({'message': f"Received and processed video: {filename}."})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    browser_path = get_browser_path()
    FlaskUI(
        app=app,
        server="flask",
        width=900,
        height=600,
        browser_path=browser_path
    ).run()
