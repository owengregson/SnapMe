const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let flaskProcess;

function createWindow() {
	const win = new BrowserWindow({
		width: 400,
		height: 600,
		webPreferences: {
			nodeIntegration: true,
			contextIsolation: false,
		},
	});

	win.loadURL("http://127.0.0.1:5000");
}

app.whenReady().then(() => {
	// Start the Flask server as a child process
	flaskProcess = spawn("python", ["flask_server.py"], {
		cwd: path.join(__dirname, ".."),
		detached: true,
		stdio: "ignore",
	});

	flaskProcess.unref();

	createWindow();

	app.on("activate", () => {
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow();
		}
	});
});

app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
		flaskProcess.kill(); // Stop the Flask server when Electron quits
	}
});

app.on("will-quit", () => {
	if (flaskProcess) {
		flaskProcess.kill(); // Ensure Flask server is terminated
	}
});
