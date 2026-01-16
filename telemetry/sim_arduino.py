import ctypes
import mmap
import time
import serial
from ctypes import c_int32, c_float

AC_PHYSICS_FILE = 'Local\\acpmf_physics'
BUFFER_SIZE_PHYSICS = 160

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
    ]

PORT_NAME = 'COM5' 
BAUD_RATE = 9600

def send_data():
    ser = None
    ser = serial.Serial(PORT_NAME, BAUD_RATE, timeout=0.1)
    print(f"Serial Port Connection Successful: {PORT_NAME}")

    with mmap.mmap(0, BUFFER_SIZE_PHYSICS, AC_PHYSICS_FILE) as physics_mmap:
        print("Assetto Corsa Shared Memory Connection Successful.")

        while True:
            physics_mmap.seek(0)
            buffer = physics_mmap.read(ctypes.sizeof(SPageFilePhysics))
            physics = SPageFilePhysics.from_buffer_copy(buffer)

            speed = int(physics.speedKmh)
            
            data = f"{speed}\n".encode('utf-8')
            
            ser.write(data)
            
            print(f"Sent Speed: {speed} km/h", end='\r')
            
            time.sleep(0.1)

if __name__ == "__main__":
    send_data()