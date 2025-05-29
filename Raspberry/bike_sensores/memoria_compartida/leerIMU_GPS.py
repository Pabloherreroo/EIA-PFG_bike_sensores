#!/usr/bin/env python3

import time
import struct
import posix_ipc
import mmap
import numpy as np

SHM_NAME = "/eBici_shared_memory"
SHM_SIZE = 52  # (49 bytes reales)

print(f"Esperando a que el writer cree la memoria compartida '{SHM_NAME}'...")
while True:
    try:
        shm = posix_ipc.SharedMemory(SHM_NAME)
        break
    except posix_ipc.ExistentialError:
        time.sleep(0.01)

map_file = mmap.mmap(shm.fd, SHM_SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
shm.close_fd()
print(f"Memoria compartida '{SHM_NAME}' abierta y mapeada ({SHM_SIZE} bytes)")

def read_shared_memory():
    map_file.seek(0)
    return map_file.read(SHM_SIZE)

def parse_data(buffer):
    try:
        # GPS: primeros 2 floats
        lat, lon = struct.unpack_from('ff', buffer, 0)
        # IMU: ultimos 3 floats
        offset = 20 + 5 + 3 + 12  # 5floats + 5bytes + padding + 3floats
        ax, ay, az = struct.unpack_from('fff', buffer, offset)
        return (lat, lon), (ax, ay, az)
    except Exception as e:
        print(f"Error parseando datos: {e}")
        return (0.0,0.0), (0.0,0.0,0.0)

def get_gps():
    time.sleep(0.8)
    buffer = read_shared_memory()
    gps_data, _ = parse_data(buffer)
    print(f"GPS: {gps_data}")
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
    print(f"Desv tipica: {std_dev}")

    if std_dev < 0.5:
        return 1
    elif std_dev < 1.5:
        return 2
    elif std_dev < 3.0:
        return 3
    else:
        return 4

if __name__ == "__main__":
    try:
        print("GPS:", get_gps())
        print("Calidad carretera:", get_imu())
    finally:
        map_file.close()
