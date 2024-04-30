const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
let mainWindow;

function createWindow() {
    // Path to the Flask executable
    const flaskAppPath = path.join(__dirname, 'dist', 'app');

    // Start the Flask server
    const server = spawn(flaskAppPath);

    server.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
        if (!mainWindow && data.toString().includes('Running on')) {
            mainWindow = new BrowserWindow({
                width: 800,
                height: 600,
                webPreferences: {
                    nodeIntegration: true,
                    contextIsolation: false // consider security implications
                }
            });

            mainWindow.loadURL('http://127.0.0.1:5000');
            mainWindow.on('closed', () => {
                mainWindow = null;
                server.kill(); // Kill Flask server when closing Electron
            });
        }
    });

    server.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });
}

app.on('ready', createWindow);
