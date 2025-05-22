import time
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bme680"))
import bme680
import json

sensor = bme680.BME680(0x77)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

def get_ambiental():
    temp_readings = []
    humidity_readings = []
    pressure_readings = []
    start_time = time.time()

    while time.time() - start_time < 0.7:
        if sensor.get_sensor_data():
            temp_readings.append(sensor.data.temperature)
            humidity_readings.append(sensor.data.humidity)
            pressure_readings.append(sensor.data.pressure)
        time.sleep(0.1)

    return {
        "temperatura": round(sum(temp_readings) / len(temp_readings), 1) if temp_readings else 0,
        "humedad": int(round(sum(humidity_readings) / len(humidity_readings))) if humidity_readings else 0,
        "presion": int(round(sum(pressure_readings) / len(pressure_readings))) if pressure_readings else 0
    }

if __name__ == "__main__":
    try:
        while True:
            datos = get_ambiental()
            print(json.dumps(datos, indent=2))
    except KeyboardInterrupt:
        print("\nLectura interrumpida.")
    except Exception as e:
        print("Error al leer datos ambientales:", str(e))