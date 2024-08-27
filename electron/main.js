const { app, BrowserWindow } = require('electron');
const path = require('path');
const { exec } = require('child_process');

// Run the Flask server
const flaskProcess = exec('python flask_server.py');

flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
});

flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
});

function createWindow () {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    win.loadURL('http://127.0.0.1:5000');
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
        flaskProcess.kill(); // Stop the Flask server when Electron quits
    }
});
