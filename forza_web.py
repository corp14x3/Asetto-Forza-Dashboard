import socket
import struct
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forza_telemetry_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

UDP_IP = "0.0.0.0"
UDP_PORT = 5566

telemetry_data = {
    'speed_kmh': 0,
    'gear': 0,
    'rpm': 0,
    'engine_max_rpm': 9000,
    'power_kw': 0,
    'torque': 0,
    'accel': 0,
    'brake': 0,
    'connected': False
}

def forza_telemetry_listener():
    global telemetry_data
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(1.0)
    
    print(f"📡 UDP Listener started: {UDP_IP}:{UDP_PORT}")
    
    last_data_time = time.time()
    first_packet = True
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            data_len = len(data)
            
            if data_len >= 232:
                if first_packet:
                    print(f"\n📦 First packet received! Size: {data_len} bytes")
                    first_packet = False
                
                is_race_on = struct.unpack('=i', data[0:4])[0]
                
                engine_max_rpm = struct.unpack('=f', data[8:12])[0]
                engine_idle_rpm = struct.unpack('=f', data[12:16])[0]
                current_rpm = struct.unpack('=f', data[16:20])[0]
                
                speed_ms = struct.unpack('=f', data[256:260])[0] if data_len > 260 else 0
                speed_kmh = speed_ms * 3.6
                
                power = struct.unpack('=f', data[260:264])[0] if data_len > 264 else 0
                torque = struct.unpack('=f', data[264:268])[0] if data_len > 268 else 0
                
                accel = struct.unpack('=B', data[315:316])[0] if data_len > 316 else 0
                brake = struct.unpack('=B', data[316:317])[0] if data_len > 317 else 0
                clutch = struct.unpack('=B', data[317:318])[0] if data_len > 318 else 0
                handbrake = struct.unpack('=B', data[318:319])[0] if data_len > 319 else 0
                gear = struct.unpack('=B', data[319:320])[0] if data_len > 320 else 0
                
                telemetry_data = {
                    'speed_kmh': round(speed_kmh, 1),
                    'gear': gear,
                    'rpm': int(current_rpm),
                    'engine_max_rpm': int(engine_max_rpm) if engine_max_rpm > 0 else telemetry_data.get('engine_max_rpm', 9000),
                    'power_kw': round(power / 1000, 1),
                    'torque': round(torque, 1),
                    'accel': accel,
                    'brake': brake,
                    'connected': True
                }
                
                socketio.emit('telemetry_update', telemetry_data)
                
                last_data_time = time.time()
            
        except socket.timeout:
            if time.time() - last_data_time > 3:
                telemetry_data['connected'] = False
                socketio.emit('telemetry_update', telemetry_data)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"✅ New connection!")
    socketio.emit('telemetry_update', telemetry_data)

if __name__ == "__main__":
    udp_thread = threading.Thread(target=forza_telemetry_listener, daemon=True)
    udp_thread.start()
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n🎮 DRIVE DASH - Forza Telemetry")
    print(f"=" * 50)
    print(f"📱 Access this address from your phone:")
    print(f"   http://{local_ip}:5000")
    print(f"\n⚙️  Forza In-Game Data Out Settings:")
    print(f"   IP: {local_ip}")
    print(f"   Port: {UDP_PORT}")
    print(f"=" * 50)
    print(f"\n🌐 Server starting...\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
