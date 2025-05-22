import time
import threading
import numpy as np
import struct
from multiprocessing import shared_memory

SHM_NAME = "shared_data"  # YA LO CAMBIARÉ
SHM_SIZE = 52  # (49 bytes reales)

imu_data_buffer = []

def read_shared_memory():
    try:
        existing_shm = shared_memory.SharedMemory(name=SHM_NAME)
        buffer = existing_shm.buf[:SHM_SIZE]
        return buffer
    except FileNotFoundError:
        print("No se encontró la memoria compartida")
        return None
    except Exception as e:
        print("Error leyendo memoria compartida:", e)
        return None

def parse_data(buffer):
    if buffer is None:
        return (0.0, 0.0), (0.0, 0.0, 0.0)
    
    try:
        # Memoria compartida: 5 floats (Latitud, Longitud...) + 5 bytes + 6 floats (Yaw, Pitch, Roll, Accel_X, Accel_Y, Accel_Z)
        lat = struct.unpack('f', buffer[0:4])[0]
        lon = struct.unpack('f', buffer[4:8])[0]
        gps_data = (lat, lon)
        
        offset = 20 + 5 + 12  # 5f + 5b + 3f (No cojo Yaw, Pitch, Roll)
        accel_x = struct.unpack('f', buffer[offset:offset+4])[0]
        accel_y = struct.unpack('f', buffer[offset+4:offset+8])[0]
        accel_z = struct.unpack('f', buffer[offset+8:offset+12])[0]    
        imu_data = (accel_x, accel_y, accel_z)
        
        return gps_data, imu_data
    except Exception as e:
        print(f"Error al extraer datos de la memoria compartida: {e}")
        return (0.0, 0.0), (0.0, 0.0, 0.0)

def get_gps():
    time.sleep(0.8)
    buffer = read_shared_memory()
    gps_data, _ = parse_data(buffer)
    return gps_data

def get_imu():
    imu_data_buffer = []  
    start_time = time.monotonic()

    while True:
        now = time.monotonic()
        if now - start_time >= 0.8:
            break
        buffer = read_shared_memory()
        _, imu = parse_data(buffer)
        imu_data_buffer.append(imu)
        time.sleep(0.02)

    if not imu_data_buffer or len(imu_data_buffer) < 2:
        return 1  # Sin datos suficientes, asumo 1

    # Con numpy, calculo magnitud de aceleraciones para cada muestra y desv estándar
    accel_data = np.array(imu_data_buffer)
    magnitudes = np.sqrt(np.sum(accel_data**2, axis=1))     # sqrt(x² + y² + z²)
    std_dev = np.std(magnitudes) # A mayor sea habrá más vibraciones

    if std_dev < 0.5:
        return 1
    elif std_dev < 1.5:
        return 2
    elif std_dev < 3.0:
        return 3
    else:
        return 4

if __name__ == "__main__":
    print("GPS:", get_gps())
    print("Calidad carretera:", get_imu())
