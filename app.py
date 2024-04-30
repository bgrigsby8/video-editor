#!/usr/bin/env python
"""
Flask server for video-editor
"""
from flask import (
	Flask, 
	jsonify, 
	render_template, 
	request,
)
import moviepy.editor as mpy
import os
from video_editor import VideoEditor
from werkzeug.utils import secure_filename

# Create the Flask instance
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/receive_filename', methods=['POST'])
def receive_filename():
	data = request.get_json()
	filename = data.get('filename')
	video_editor = VideoEditor("C:/Users/Brad's PC/projects/video-editor/test_video.mp4")
	video_editor.process_video()

	return jsonify({'message': f"Received filename: {filename} and edited video."})

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
	app.run(host='127.0.0.1', port=5000, debug=False)