import time
import board
import busio
import adafruit_tsl2591
import json

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

def get_luz():
    lux_readings = []
    start_time = time.time()
    
    while time.time() - start_time < 0.7:
        lux = sensor.lux
        lux_readings.append(lux)
        time.sleep(0.1)

    avg_lux = int(round(sum(lux_readings) / len(lux_readings), 2)) if lux_readings else 0
    return avg_lux

if __name__ == "__main__":
    try:
        while True:
            lux = get_luz()
            print(json.dumps({"luz": lux}, indent=2))
    except KeyboardInterrupt:
        print("\nLectura interrumpida.")
    except Exception as e:
        print("Error al leer luz:", str(e))