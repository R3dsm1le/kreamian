from tinydb import TinyDB
from os import getenv
import requests as re  # Asumiendo que 're' es la librería requests
import json as j

def configurar_llamado():
    """Esta clase se utiliza para configurar los llamados a la API
        Inputs : variables de entorno 
        Outputs : constantes y parametros 
    """
    URL = getenv("URL") 
    ACCESS_TOKEN = getenv("ACCESS_TOKEN")  # Reemplaza con tu clave de API real

    PARAMS = {
        "key": ACCESS_TOKEN,
        "countrycode": "PA",
        "maxresults": 2  # Opcional: limita o amplia el número máximo de resultados
    }
    return URL, PARAMS

def extraer_datos(): 
    url, params = configurar_llamado()
    try:
        # Realizamos la petición GET a la API
        response = re.get(url=str(url), params=params)
        
        # Verificamos si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            datos_json = response.json()  # Obtenemos los datos en formato nativo de Python (dict o list)
            
            # (Opcional) Imprimimos para visualizar el resultado formateado
            result = j.dumps(datos_json, indent=4, ensure_ascii=False)
            print(result)
            
            # TRASPASO DE DATOS: Llamamos a la función de guardado pasándole los datos
            guardar_en_tiny_db(datos_json)
        else:
            print(f"Error en la API: {response.status_code}\n{response.text}")
            
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def guardar_en_tiny_db(datos):
    """Recibe los datos extraídos y los guarda utilizando TinyDB"""
    # Inicializamos la base de datos (creará un archivo llamado 'db.json')
    db = TinyDB('db.json')
    
    # Como Open Charge Map suele devolver una lista de estaciones, 
    # usamos insert_multiple si es una lista, o insert si es un diccionario único.
    if isinstance(datos, list):
        db.insert_multiple(datos)
    else:
        db.insert(datos)
        
    print("¡Datos guardados exitosamente en TinyDB!")