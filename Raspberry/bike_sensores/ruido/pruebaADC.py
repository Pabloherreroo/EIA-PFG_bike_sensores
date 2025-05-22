import smbus
import time
import math

ADS1115_ADDR = 0x48

POINTER_CONVERT = 0x00
POINTER_CONFIG = 0x01

CONFIG_OS_SINGLE    = 0x8000
CONFIG_MUX_AIN0     = 0x4000
CONFIG_GAIN = 0x0200
CONFIG_MODE_SINGLE  = 0x0100
CONFIG_DR_128SPS    = 0x0080
CONFIG_COMP_DISABLE = 0x0003

CONFIG = (CONFIG_OS_SINGLE | CONFIG_MUX_AIN0 | CONFIG_GAIN |
          CONFIG_MODE_SINGLE | CONFIG_DR_128SPS | CONFIG_COMP_DISABLE)

bus = smbus.SMBus(1) 

BIT_TO_VOLT = 0.125 / 1000.0
OFFSET_DB = 30

def leer_raw_adc():
    msb = (CONFIG >> 8) & 0xFF
    lsb = CONFIG & 0xFF
    bus.write_i2c_block_data(ADS1115_ADDR, POINTER_CONFIG, [msb, lsb])
    time.sleep(0.008) 

    data = bus.read_i2c_block_data(ADS1115_ADDR, POINTER_CONVERT, 2)
    valor = (data[0] << 8) | data[1]
    if valor > 0x7FFF:
        valor -= 0x10000
    return valor

def medir_rms(duracion=0.7):
    muestras = []
    inicio = time.time()

    while (time.time() - inicio) < duracion:
        val = leer_raw_adc()
        muestras.append(val)

    if not muestras:
        return 0.0, 0.0, 0.0

    promedio = sum(muestras) / len(muestras)
    sin_offset = [x - promedio for x in muestras]
    cuadrado = [x ** 2 for x in sin_offset]
    rms_raw = math.sqrt(sum(cuadrado) / len(cuadrado))

    volt_rms = rms_raw * BIT_TO_VOLT
    volt_inst = muestras[0] * BIT_TO_VOLT
    return volt_rms, volt_inst, rms_raw

def voltaje_to_db(volt_rms, volt_ref=1e-6):  
    if volt_rms <= 0:
        return 0
    db = 20 * math.log10(volt_rms / volt_ref) - 35
    if rms_crudo:
        factor = math.log10(rms_crudo + 1)
        db += 15 * factor 
    return max(0, db)


if __name__ == "__main__":
    try:
        while True:
            v_rms, v_inst, rms_crudo = medir_rms(duracion=0.7)
            db = voltaje_to_db(v_rms)
            print(f"VRMS: {v_rms:.6f} V | RMS crudo: {rms_crudo:.1f} | Inst: {v_inst:.6f} V | dB estimado: {db:.1f} dB")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCalibración detenida.")
    except Exception as e:
        print("Error al medir:", str(e))

        
