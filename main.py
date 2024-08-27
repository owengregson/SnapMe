# flask_server.py
import os
import platform
import time
import ctypes
import pyautogui
import keyboard
import logging
from flask import Flask, render_template, request, jsonify
from threading import Thread, Event
from dataclasses import dataclass, field

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("snapchat_bot.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class PositionSelector:
    positions: dict = field(default_factory=dict)
    current_message: str = ""
    stop_event: Event = field(default_factory=Event)

    def set_position(self, name: str):
        self.current_message = f"Move your mouse to the {name} button, then press 'R'"
        logging.info(self.current_message)
        while not self.stop_event.is_set():
            keyboard.wait('r')
            pos = pyautogui.position()
            self.positions[name] = pos
            logging.info(f"Position for '{name}' set to: {pos}")
            time.sleep(0.5)
            break

    def get_position(self, name: str):
        return self.positions.get(name)

    def reset_positions(self):
        self.positions = {}
        self.current_message = ""
        logging.info("All positions have been reset.")

    def stop_positioning(self):
        self.stop_event.set()

    def start_positioning(self):
        self.stop_event.clear()

@dataclass
class SnapchatBot:
    sent_snaps: int = 0
    delay: float = 1.3
    selector: PositionSelector = field(default_factory=PositionSelector)
    start_time: float = 0
    is_running: bool = False

    def _is_linux(self):
        return platform.system() == "Linux"

    def update_console_title(self, shortcut_users):
        now = time.time()
        elapsed = int(now - self.start_time)
        sent_snaps = self.sent_snaps * shortcut_users
        title = (f"SnapMe - Sent: {sent_snaps} - Elapsed: {elapsed}s | Made with <3 by @owengregson on GitHub")
        if not self._is_linux():
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        logging.info(title)

    def start_sending_snaps(self, shortcut_users):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self._send_snap_loop(shortcut_users)

    def _send_snap_loop(self, shortcut_users):
        actions = [
            "camera",
            "take_picture",
            "edit_send",
            "send_to",
            "shortcut",
            "select_all",
            "send_snap"
        ]
        while self.is_running:
            for action in actions:
                pos = self.selector.get_position(action)
                if pos:
                    pyautogui.moveTo(pos)
                    pyautogui.click()
                    logging.debug(f"Clicked on {action} at {pos}")
                    time.sleep(self.delay)
                else:
                    logging.error(f"Position for '{action}' not set. Skipping action.")
            self.sent_snaps += 7
            self.update_console_title(shortcut_users)
            time.sleep(4)  # Wait before sending another set of snaps

    def stop_sending_snaps(self):
        self.is_running = False
        logging.info("Stopping the snap sending process.")

    def reset_positions(self):
        self.selector.reset_positions()
        logging.info("Resetting positions. Reconfiguration needed.")

# Global bot instance
bot = SnapchatBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    shortcut_users = int(request.form['shortcut_users'])
    logging.info(f"Starting snap sending for {shortcut_users} users.")
    Thread(target=bot.start_sending_snaps, args=(shortcut_users,)).start()
    return jsonify(success=True)

@app.route('/stop', methods=['POST'])
def stop():
    bot.stop_sending_snaps()
    return jsonify(success=True)

@app.route('/reset_positions', methods=['POST'])
def reset_positions():
    bot.reset_positions()
    return jsonify(success=True)

@app.route('/start_positioning', methods=['POST'])
def start_positioning():
    bot.selector.start_positioning()
    Thread(target=_positioning_guide).start()
    return jsonify(success=True)

@app.route('/stop_positioning', methods=['POST'])
def stop_positioning():
    bot.selector.stop_positioning()
    return jsonify(success=True)

@app.route('/current_message', methods=['GET'])
def current_message():
    return jsonify(message=bot.selector.current_message)

@app.route('/close', methods=['POST'])
def close():
    os._exit(0)

def _positioning_guide():
    positions = [
        "camera", "take_picture", "edit_send", "send_to",
        "shortcut", "select_all", "send_snap"
    ]
    for position in positions:
        if bot.selector.stop_event.is_set():
            break
        bot.selector.set_position(position)
    logging.info("Positioning finished.")

def run_flask():
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    run_flask()
