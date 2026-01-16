# DRIVE DASH 🏎️💨

**DRIVE DASH** is a telemetry system developed for Assetto Corsa and Forza Horizon 5 (and Motorsport). It provides both a web-based dashboard and sends real-time data to a physical LCD screen via Arduino.

---

### Features
- **Dual Game Support:** Fully compatible with Assetto Corsa and Forza Horizon 5.
- **Web Dashboard:** Modern, fluid (60 FPS) speed and RPM gauges.
- **Arduino Support:** Real-time speed tracking via a 16x2 LCD display.
- **Real-time Data:** Low-latency communication via UDP and Shared Memory.

### Installation

1. **Python Requirements:**
   ```bash
   pip install flask flask-socketio eventlet pyserial
   ```

2. **Arduino Setup:**
   - Open `telemetry/telemetry.ino` in Arduino IDE.
   - Ensure `LiquidCrystal` library is installed.
   - Connect your Arduino and upload the code.

### Usage

#### 🏁 For Assetto Corsa:
1. Start the game.
2. Run `asetto_web.py`.
3. Open `http://localhost:5000` in your browser.
4. (Optional) Run `telemetry/sim_arduino.py` for Arduino support. (Ensure `PORT_NAME` is correct for your device).

#### 🏎️ For Forza Horizon 5:
1. Go to **Settings > HUD and Gameplay**.
2. Set **Data Out** to `ON`.
3. Set **Data Out IP Address** to your computer's local IP.
4. Set **Data Out IP Port** to `5566`.
5. Run `forza_web.py`.
6. Open `http://localhost:5000` in your browser.

---

## 🛠️ Project Structure
- `asetto_web.py`: Web server for Assetto Corsa.
- `forza_web.py`: Web server for Forza.
- `sim_info.py`: Shared memory structures for AC.
- `templates/index.html`: The UI for the dashboard.
- `telemetry/sim_arduino.py`: Python-to-Arduino bridge.

- `telemetry/telemetry.ino`: Arduino firmware.
