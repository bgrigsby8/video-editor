const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const basePath = process.resourcesPath; // Use this in production
const axios = require('axios'); // Make sure to install axios via npm
let mainWindow;

function createWindow() {
    // Start the Flask server
    const pythonExecutable = 'C:/Python39/python.exe'; // For example: 'C:/Python39/python.exe'
    const flaskAppPath = path.join(__dirname, 'app.py');
    const server = spawn('python', [path.join(basePath, './app.py')]);

    // Function to check if Flask server is ready
    function checkServer() {
        axios.get('http://127.0.0.1:5000')
            .then(response => {
                // When Flask responds successfully, create the browser window
                if (!mainWindow) {
                    mainWindow = new BrowserWindow({
                        width: 800,
                        height: 600,
                        webPreferences: {
                            nodeIntegration: true,
                            contextIsolation: false
                        }
                    });

                    mainWindow.loadURL('http://127.0.0.1:5000');

                    mainWindow.on('closed', function () {
                        mainWindow = null;
                        server.kill(); // Kill Flask server when closing Electron
                    });
                }
            })
            .catch(error => {
                // Retry after a short delay if Flask is not ready
                console.log("Flask server is not ready yet. Retrying...");
                setTimeout(checkServer, 2000); // Adjust delay as needed
            });
    }

    // Start checking if the Flask server is ready
    checkServer();
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

