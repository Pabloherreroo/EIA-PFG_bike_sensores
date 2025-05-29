import requests
import threading
import datetime
import time
from luz.leerluz import get_luz
from ambiental.leerambiental import get_ambiental
from ruido.leerruido import get_ruido
from memoria_compartida.leerIMU_GPS import get_imu, get_gps

FIREBASE_URL = "https://bicicletas-sensorizadas-default-rtdb.europe-west1.firebasedatabase.app/bike_data.json"

def send_data():
    while True:
        start_time = time.perf_counter()
        try:
            resultados = {
                "luz": None,
                "ruido": None,
                "ambiental": {},
                "gps": (0.0, 0.0),
                "puntuacion_road": None 
            }

            def leer_luz():
                resultados["luz"] = get_luz()
                
            def leer_ruido():
                resultados["ruido"] = get_ruido()

            def leer_ambiental():
                resultados["ambiental"] = get_ambiental()
                
            def leer_gps():
                resultados["gps"] = get_gps()

            def leer_imu():
                resultados["puntuacion_road"] = get_imu()

            hilo_luz = threading.Thread(target=leer_luz)
            hilo_ambiental = threading.Thread(target=leer_ambiental)
            hilo_ruido = threading.Thread(target=leer_ruido)
            hilo_gps = threading.Thread(target=leer_gps)
            hilo_imu = threading.Thread(target=leer_imu)

            hilo_luz.start()
            hilo_ambiental.start()
            hilo_ruido.start()
            hilo_gps.start()
            hilo_imu.start()

            hilo_luz.join()
            hilo_ambiental.join()
            hilo_ruido.join()
            hilo_gps.join()
            hilo_imu.join()

            lat, lon = resultados["gps"]
            
            if lat != 0.0 or lon != 0.0:
                data = {
                    "bike_id": "B1",
                    "latitud": lat,
                    "longitud": lon,
                    "puntuacion_road": resultados["puntuacion_road"],
                    "ruido": resultados["ruido"],
                    "temperatura": resultados["ambiental"].get("temperatura", 0),
                    "humedad": resultados["ambiental"].get("humedad", 0),
                    "presion": resultados["ambiental"].get("presion", 0),
                    "luz": resultados["luz"],
                    "fecha": datetime.datetime.now().isoformat()
                }

                response = requests.post(FIREBASE_URL, json=data)
                if response.status_code == 200:
                    print("Datos enviados correctamente:", data)
                else:
                    print("Error al enviar datos:", response.text)
            else:
                print("Coordenadas GPS no válidas (0,0), no se envían datos.")

        except Exception as e:
            print("Error general:", str(e))

        time_consumed = time.perf_counter() - start_time
        time_to_wait = 1.0 - time_consumed

        if time_to_wait > 0:
            time.sleep(time_to_wait)

if __name__ == "__main__":
    try:
        send_data()
    except KeyboardInterrupt:
        print("\nDeteniendo")
    finally:
        from memoria_compartida.leerIMU_GPS import map_file
        print("Cerrando mapeo de memoria compartida")
        map_file.close()

