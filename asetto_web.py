import socket
import struct
import threading
import ctypes
import mmap
import time
from ctypes import c_int32, c_float, c_wchar
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'asetto-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=30)

class SPageFilePhysics(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('packetId', c_int32),
        ('gas', c_float),
        ('brake', c_float),
        ('fuel', c_float),
        ('gear', c_int32),
        ('rpms', c_int32),
        ('steerAngle', c_float),
        ('speedKmh', c_float),
        ('velocity', c_float * 3),
        ('accG', c_float * 3),
        ('wheelSlip', c_float * 4),
        ('wheelLoad', c_float * 4),
        ('wheelsPressure', c_float * 4),
        ('wheelAngularSpeed', c_float * 4),
        ('tyreWear', c_float * 4),
        ('tyreDirtyLevel', c_float * 4),
        ('tyreCoreTemperature', c_float * 4),
        ('camberRAD', c_float * 4),
        ('suspensionTravel', c_float * 4),
        ('drs', c_float),
        ('tc', c_float),
        ('heading', c_float),
        ('pitch', c_float),
        ('roll', c_float),
        ('cgHeight', c_float),
        ('carDamage', c_float * 5),
        ('numberOfTyresOut', c_int32),
        ('pitLimiterOn', c_int32),
        ('abs', c_float),
        ('kersCharge', c_float),
        ('kersInput', c_float),
        ('autoShifterOn', c_int32),
        ('rideHeight', c_float * 2),
        ('turboBoost', c_float),
        ('ballast', c_float),
        ('airDensity', c_float),
        ('airTemp', c_float),
        ('roadTemp', c_float),
        ('localAngularVel', c_float * 3),
        ('finalFF', c_float),
        ('performanceMeter', c_float),
        ('engineBrake', c_int32),
        ('ersRecoveryLevel', c_int32),
        ('ersPowerLevel', c_int32),
        ('ersHeatCharging', c_int32),
        ('ersIsCharging', c_int32),
        ('kersCurrentKJ', c_float),
        ('drsAvailable', c_int32),
        ('drsEnabled', c_int32),
        ('brakeTemp', c_float * 4),
        ('clutch', c_float),
        ('tyreTempI', c_float * 4),
        ('tyreTempM', c_float * 4),
        ('tyreTempO', c_float * 4),
        ('isAIControlled', c_int32),
        ('tyreContactPoint', c_float * 4 * 3),
        ('tyreContactNormal', c_float * 4 * 3),
        ('tyreContactHeading', c_float * 4 * 3),
        ('brakeBias', c_float),
        ('localVelocity', c_float * 3),
    ]

class SPageFileStatic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('_smVersion', c_wchar * 15),
        ('_acVersion', c_wchar * 15),
        ('numberOfSessions', c_int32),
        ('numCars', c_int32),
        ('carModel', c_wchar * 33),
        ('track', c_wchar * 33),
        ('playerName', c_wchar * 33),
        ('playerSurname', c_wchar * 33),
        ('playerNick', c_wchar * 33),
        ('sectorCount', c_int32),
        ('maxTorque', c_float),
        ('maxPower', c_float),
        ('maxRpm', c_int32),
        ('maxFuel', c_float),
        ('suspensionMaxTravel', c_float * 4),
        ('tyreRadius', c_float * 4),
        ('maxTurboBoost', c_float),
        ('airTemp', c_float),
        ('roadTemp', c_float),
        ('penaltiesEnabled', c_int32),
        ('aidFuelRate', c_float),
        ('aidTireRate', c_float),
        ('aidMechanicalDamage', c_float),
        ('aidAllowTyreBlankets', c_int32),
        ('aidStability', c_float),
        ('aidAutoClutch', c_int32),
        ('aidAutoBlip', c_int32),
        ('hasDRS', c_int32),
        ('hasERS', c_int32),
        ('hasKERS', c_int32),
        ('kersMaxJ', c_float),
        ('engineBrakeSettingsCount', c_int32),
        ('ersPowerControllerCount', c_int32),
        ('trackSPlineLength', c_float),
        ('trackConfiguration', c_wchar * 33),
        ('ersMaxJ', c_float),
        ('isTimedRace', c_int32),
        ('hasExtraLap', c_int32),
        ('carSkin', c_wchar * 33),
        ('reversedGridPositions', c_int32),
        ('pitWindowStart', c_int32),
        ('pitWindowEnd', c_int32),
    ]

telemetry_data = {
    'speed_kmh': 0,
    'rpm': 0,
    'gear': 0,
    'power_kw': 0,
    'accel': 0,
    'brake': 0,
    'connected': False,
    'engine_max_rpm': 9000
}

AC_PHYSICS_FILE = 'Local\\acpmf_physics'
AC_STATIC_FILE = 'Local\\acpmf_static'

def assetto_telemetry_listener():
    print("[AC] Listening for Assetto Corsa via Shared Memory...")
    
    while True:
        try:
            with mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), AC_PHYSICS_FILE) as physics_mmap:
                with mmap.mmap(0, ctypes.sizeof(SPageFileStatic), AC_STATIC_FILE) as static_mmap:
                    print("[AC] Connected to Assetto Corsa Shared Memory")
                    
                    while True:
                        try:
                            physics_mmap.seek(0)
                            physics_buffer = physics_mmap.read(ctypes.sizeof(SPageFilePhysics))
                            physics = SPageFilePhysics.from_buffer_copy(physics_buffer)
                            
                            static_mmap.seek(0)
                            static_buffer = static_mmap.read(ctypes.sizeof(SPageFileStatic))
                            static = SPageFileStatic.from_buffer_copy(static_buffer)
                            
                            telemetry_data['speed_kmh'] = physics.speedKmh
                            telemetry_data['rpm'] = physics.rpms
                            telemetry_data['gear'] = physics.gear
                            telemetry_data['accel'] = int(physics.gas * 100)
                            telemetry_data['brake'] = int(physics.brake * 100)
                            telemetry_data['power_kw'] = int((physics.gas * static.maxPower) / 1000)
                            telemetry_data['connected'] = True
                            telemetry_data['engine_max_rpm'] = static.maxRpm if static.maxRpm > 1000 else 9000
                            
                            socketio.emit('telemetry_update', telemetry_data, skip_sid=None)
                            
                            time.sleep(0.016)
                            
                        except Exception as e:
                            print(f"[AC] Update error: {e}")
                            time.sleep(0.1)
                            
        except FileNotFoundError:
            print("[AC] Assetto Corsa not running or Shared Memory disabled")
            telemetry_data['connected'] = False
            socketio.emit('telemetry_update', telemetry_data, skip_sid=None)
            time.sleep(1)
        except Exception as e:
            print(f"[AC] Connection error: {e}")
            telemetry_data['connected'] = False
            socketio.emit('telemetry_update', telemetry_data, skip_sid=None)
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    listener_thread = threading.Thread(target=assetto_telemetry_listener, daemon=True)
    listener_thread.start()
    
    print("[SimTeleNio] Starting Assetto Corsa Telemetry Dashboard on http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
