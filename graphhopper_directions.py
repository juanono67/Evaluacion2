
import os
import requests

API_URL = "https://graphhopper.com/api/1/route"


def obtener_coordenadas(mensaje):
    while True:
        entrada = input(mensaje).strip()

        if entrada.lower() in ("s", "salir"):
            return None

        try:
            latitud, longitud = entrada.split(",")
            latitud = float(latitud.strip())
            longitud = float(longitud.strip())

            if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
                raise ValueError

            return latitud, longitud

        except ValueError:
            print("Coordenadas no válidas. Usa el formato: latitud,longitud")
            print("Ejemplo: -33.4489,-70.6693")
            print("Escribe 's' o 'salir' para terminar.")


def consultar_ruta(origen, destino, api_key):
    parametros = {
        "point": [
            "{},{}".format(origen[0], origen[1]),
            "{},{}".format(destino[0], destino[1])
        ],
        "vehicle": "car",
        "locale": "es",
        "instructions": "true",
        "points_encoded": "false",
        "key": api_key
    }

    respuesta = requests.get(API_URL, params=parametros, timeout=30)

    if respuesta.status_code != 200:
        print("No se pudo calcular la ruta (HTTP {}).".format(
            respuesta.status_code
        ))
        try:
            print("Detalle: {}".format(
                respuesta.json().get("message", "Error desconocido")
            ))
        except ValueError:
            print("No se recibió un detalle del error.")
        return

    datos = respuesta.json()
    rutas = datos.get("paths", [])

    if not rutas:
        print("No se encontró una ruta entre esos puntos.")
        return

    ruta = rutas[0]
    distancia_km = ruta["distance"] / 1000
    tiempo_minutos = ruta["time"] / 60000

    print("\n--- RESULTADO DEL VIAJE ---")
    print("Distancia: {:.2f} km".format(distancia_km))
    print("Tiempo estimado: {:.2f} minutos".format(tiempo_minutos))
    print("\nNarrativa del viaje:")

    instrucciones = ruta.get("instructions", [])

    if not instrucciones:
        print("La API no entregó instrucciones para este recorrido.")
        return

    for numero, instruccion in enumerate(instrucciones, start=1):
        texto = instruccion.get("text", "Continúa por la ruta.")
        distancia = instruccion.get("distance", 0) / 1000
        print("{}. {} ({:.2f} km)".format(numero, texto, distancia))


def main():
    api_key = os.environ.get("GRAPHHOPPER_API_KEY")

    if not api_key:
        print("No se encontró la API Key de GraphHopper.")
        print("Configúrala en la terminal antes de ejecutar el programa.")
        return

    print("======================================")
    print("   SISTEMA DE RUTAS GRAPHHOPPER")
    print("======================================")
    print("Ingresa las coordenadas en formato latitud,longitud.")
    print("Ejemplo: -33.4489,-70.6693")
    print("Escribe 's' o 'salir' para terminar.\n")

    while True:
        origen = obtener_coordenadas(
            "Ingresa las coordenadas del origen: "
        )

        if origen is None:
            print("Programa finalizado. ¡Hasta pronto!")
            break

        destino = obtener_coordenadas(
            "Ingresa las coordenadas del destino: "
        )

        if destino is None:
            print("Programa finalizado. ¡Hasta pronto!")
            break

        try:
            consultar_ruta(origen, destino, api_key)
        except requests.exceptions.Timeout:
            print("La solicitud tardó demasiado. Inténtalo nuevamente.")
        except requests.exceptions.RequestException as error:
            print("Error de conexión: {}".format(error))
        except (KeyError, TypeError, ValueError) as error:
            print("No se pudo interpretar la respuesta de la API: {}".format(
                error
            ))

        print()


if __name__ == "__main__":
    main()
