@echo off
REM Check for Python installation
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

REM Check if pip is installed
pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo pip is not installed. Please install pip and try again.
    exit /b
)

REM Check and install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check for Node.js installation
node --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Node.js is not installed. Please install Node.js and try again.
    exit /b
)

REM Navigate to the electron directory
cd electron

REM Check and install Node.js dependencies
if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
) else (
    echo Node.js dependencies are already installed.
)

REM Start the Flask server and Electron app
echo Starting Flask server and Electron app...
start /B python ..\main.py
npm start

REM Return to the root directory
cd ..
PAUSE