import time
import board
import busio
import math
import json
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ADS

i2c = busio.I2C(board.SCL, board.SDA)
adc = ADS1115(i2c)
adc.gain = 1  # ±4.096V
canal = AnalogIn(adc, 0)

def get_ruido():
    DURACION = 0.7  # segundos para medir
    VOLT_REF = 1e-6  # voltaje de referencia para dB
    OFFSET_DB = 35   # offset de calibración
    
    muestras = []
    inicio = time.time()
    while (time.time() - inicio) < DURACION:
        valor = canal.value
        muestras.append(valor)
        
    if not muestras:
        return 0

    promedio = sum(muestras) / len(muestras)
    sin_offset = [x - promedio for x in muestras]
    cuadrado = [x ** 2 for x in sin_offset]
    rms_raw = math.sqrt(sum(cuadrado) / len(cuadrado))
    volt_rms = canal.voltage * (rms_raw / promedio) if promedio != 0 else 0
    
    if volt_rms <= 0:
        dB = 0
    else:
        dB = 20 * math.log10(volt_rms / VOLT_REF) - OFFSET_DB
        factor = math.log10(rms_raw + 1)
        dB += 15 * factor
        
    dB = max(0, dB)
    
    return int(round(dB))
if __name__ == "__main__":
    try:
        while True:
            ruido = get_ruido()
            print(json.dumps({"ruido_dB": ruido}, indent=2))
    except KeyboardInterrupt:
        print("\nLectura interrumpida.")
    except Exception as e:
        print("Error al leer ruido:", str(e))
