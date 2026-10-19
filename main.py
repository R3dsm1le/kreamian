import os
import subprocess
import sys

# Agregamos la carpeta INGESTA al path de Python para importar directamente
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "INGESTA"))
)

try:
  from ingesta_datos import extraer_datos
except ImportError as e:
  print(f"Error al importar 'extraer_datos' desde la carpeta INGESTA: {e}")
  sys.exit(1)


def paso_1_ingesta():
  print("[1/3] Ejecutando Extracción y Guardado en TinyDB (INGESTA)...")
  try:
    extraer_datos()
    print("-> Datos extraídos y almacenados exitosamente en 'db.json'.")
  except Exception as e:
    print(f"Error en la ingesta de datos: {e}")
    sys.exit(1)


def paso_2_transformacion():
  print("[2/3] Ejecutando Spatial ETL y Normalización (TRANSFORMACION)...")

  # Ruta al archivo de Go dentro de la carpeta TRANSFORMACION
  archivo_go = os.path.join("TRANSFORMACION", "transformacion.go")

  if not os.path.exists(archivo_go):
    print(
        f"Error: No se encuentra el archivo de transformación en '{archivo_go}'."
    )
    sys.exit(1)

  try:
    # Si estás dentro de Docker, puedes invocar directamente el binario compilado:
    # binario = "/app/bin/transformacion-go"
    # subprocess.run([binario], check=True)

    # Si estás ejecutando localmente con 'go run':
    subprocess.run(["go", "run", archivo_go], check=True)
    print("-> ETL Espacial completado. Archivo de salida generado.")
  except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar el script de Go: {e}")
    sys.exit(1)


def paso_3_ltm_inferencia():
  print("[3/3] Ejecutando Inferencia (Carpeta LTM)...")

  # Apuntamos directamente a tu archivo 'inferencia_ltm.py' visto en la estructura
  script_ltm = os.path.join("LTM", "inferencia_ltm.py")

  if not os.path.exists(script_ltm):
    print(f"Error: No se encuentra el script de inferencia en '{script_ltm}'.")
    sys.exit(1)

  try:
    subprocess.run([sys.executable, script_ltm], check=True)
    print("-> Inferencia en LTM completada con éxito.")
  except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar el script de LTM: {e}")
    sys.exit(1)


if __name__ == "__main__":
  print("=== INICIO DEL PIPELINE INTEGRADO ===")
  paso_1_ingesta()
  print("-" * 50)
  paso_2_transformacion()
  print("-" * 50)
  paso_3_ltm_inferencia()
  print("=== PIPELINE EJECUTADO EXITOSAMENTE ===")