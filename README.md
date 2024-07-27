# VideoEditor

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Settings](#settings)
- [Packaging the Application](#packaging-the-application)
- [Contributing](#contributing)
- [License](#license)

## Overview
VideoEditor is a web-based application that allows users to edit videos by automatically detecting and removing silent segments. The application is built using Flask for the backend and a frontend interface that provides an easy way to upload videos, adjust settings, and process videos.

## Features
- Upload video files for processing.
- Automatically detect and remove silent segments from videos.
- Customize processing settings including volume threshold, silence jacket, and dynamic volume threshold.
- Specify output directory for edited videos.
- View real-time processing logs.

## Requirements
- Python 3.12
- Flask
- FlaskWebGUI
- MoviePy
- Other dependencies as listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/video-editor.git
   cd video-editor
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv myvenv
   source myenv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup the application (to run through the terminal):
   ```bash
   python3 app.py
   ```

## Usage
1. Run the application
   ```bash
   python app.py
   ```
2. Open you web browser and navigate to `http://localhost:5000`
3. Adjust settings as needed and save them
4. Upload a video file using the upload button
5. The application will process the video and save the edited clips to the specified output directory.

## Settings
The application allows you to adjust a number of settings:
- Minimum Volume Threshold: The volume level below which segments are considered silent.
- Silence Jacket: The amount of non-silent audio to keep around silent segments.
- Dynamic Volume Threshold: Toggle to dynamically calculate the minimum volume threshold based on the initial segments of the video
- Output Directory: Specify the directory where edited videos will be saved

## Packaging the application
To pacakge the application into a standalone MacOS app, follow these steps:
1. Install `py2app`:
   ```bash
   pip install py2app
   ```
2. Create `setup.py` for `py2app`:
   ```python
   from setuptools import setup

   APP = ['app.py']
   DATA_FILES = []
   OPTIONS = {
       'argv_emulation': True,
       'includes': ['moviepy', 'flask', 'flaskwebgui', 'psutil', 'tqdm'],
       'packages': ['os', 'sys', 'logging', 'queue', 'argparse', 'math', 'numpy', 'moviepy', 'flask', 'flaskwebgui'],
       'iconfile': 'path/to/your/icon.icns',
       'plist': {
           'CFBundleName': 'VideoEditor',
           'CFBundleDisplayName': 'VideoEditor',
           'CFBundleIdentifier': 'com.yourname.videoeditor',
           'CFBundleVersion': '0.1.0',
           'CFBundleShortVersionString': '0.1.0',
           'NSHighResolutionCapable': True
       }
   }

   setup(
       app=APP,
       data_files=DATA_FILES,
       options={'py2app': OPTIONS},
       setup_requires=['py2app'],
   )
   ```
3. Build the application:
   ```bash
   python setup.py py2app -A
   ```

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is under the MIT license. See the `LICENSE` file for more details
