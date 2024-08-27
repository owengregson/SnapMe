const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

let flaskProcess;

function createWindow() {
	const win = new BrowserWindow({
		width: 400,
		height: 600,
		icon: path.join(__dirname, "..", "resources", "images", "icon.png"),
		webPreferences: {
			nodeIntegration: true,
			contextIsolation: false,
		},
		autoHideMenuBar: true,
	});

	win.setMenu(null);

	win.loadURL("http://127.0.0.1:5000");
}

function startFlaskServer() {
	return new Promise((resolve, reject) => {
		flaskProcess = spawn("python", ["flask_server.py"], {
			cwd: path.join(__dirname, ".."),
			detached: true,
			stdio: "ignore",
		});

		flaskProcess.unref();

		// Poll the server until it’s up and running
		const checkServer = () => {
			http.get("http://127.0.0.1:5000", (res) => {
				if (res.statusCode === 200) {
					resolve();
				} else {
					setTimeout(checkServer, 100);
				}
			}).on("error", () => {
				setTimeout(checkServer, 100);
			});
		};
		checkServer();
	});
}

app.whenReady().then(() => {
	startFlaskServer()
		.then(() => {
			createWindow();
		})
		.catch((err) => {
			console.error("Failed to start Flask server:", err);
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
