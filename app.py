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
from video_editor import VideoEditor
from werkzeug.utils import secure_filename

# Create the Flask instance
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r"C:\\Users\\Brad's PC\\projects\\video-editor\\tmp"

def ensure_upload_folder_exists():
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Upload folder '{app.config['UPLOAD_FOLDER']}' is ready.")
    except Exception as e:
        print(f"Error creating upload directory: {e}")

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
	# app.run(host='127.0.0.1', port=5000, debug=True)
	FlaskUI(
		app=app,
		server="flask",
		width=900,
		height=600,
		browser_path=r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
	).run()