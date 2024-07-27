from setuptools import setup

APP = ['app.py']
DATA_FILES = ['templates', 'static']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['flask', 'flaskwebgui', 'pathlib', 'moviepy', 'numpy', 'werkzeug', 'logging', 'psutil', 'tqdm'],
    'excludes': [
        'PyQt5', 'PyInstaller', 'gi', 'Cython', 'IPython', 'OpenSSL', 'pandas', 'scipy', 'setuptools',
        'matplotlib', 'PyQt6', 'PySide6', 'tensorflow', 'Tkinter', 'pygame', 'cv2', 'cython',
        'distutils', 'setuptools', 'mypy', 'numba', 'hypothesis', 'pytest'
    ],
    'frameworks': [
        '/opt/homebrew/opt/libffi/lib/libffi.8.dylib',
        '/opt/homebrew/opt/expat/lib/libexpat.1.dylib'
    ],
    'plist': {
        'CFBundleName': 'VideoEditor',
        'CFBundleDisplayName': 'VideoEditor',
        'CFBundleIdentifier': 'com.yourcompany.videoeditor',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': 'True'
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
