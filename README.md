# Video Editor

This project is a video editing application that cuts a video file according to silences below a threshold for a specified duration. It includes a Python script to process the video and a Flask web application to provide a user interface for uploading and processing videos.

## Features

- Extracts audio from a video and identifies silences.
- Cuts the video into sub-clips based on speaking intervals.
- Optionally concatenates the sub-clips into a single video.
- Provides a web interface for uploading and processing videos.

## Requirements

- Python 3.6+
- Flask
- FlaskWebGUI
- MoviePy
- NumPy

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/video-editor.git
    cd video-editor
    ```

2. Create and activate a virtual environment (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Command Line

To run the video editor from the command line, use the following command:
```sh
python video_editor.py -f <path_to_video_file> -c <True_or_False>
