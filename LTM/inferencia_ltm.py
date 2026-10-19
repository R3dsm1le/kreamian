import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tabfm import TabFMRegressor
from tabfm import tabfm_v1_0_0_pytorch as tabfm_v1_0_0  # Usando el backend de PyTorch

def ejecutar_inferencia():
    print("[3/3] Iniciando inferencia con TabFM...")
    
    # 1. Cargar el output del Spatial ETL (GeoJSON procesado por Go)
    try:
        with open("spatial_etl_output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'spatial_etl_output.json'. Ejecuta el paso de Go primero.")
        return

    if not data:
        print("El archivo de datos está vacío.")
        return

    # 2. Aplanamiento de datos para estructurarlos en un DataFrame de Pandas
    rows = []
    for item in data:
        rows.append({
            "id": item["id"],
            "city": item["city"] if item["city"] else "Desconocida",
            "primary_connector": item["standardized_connectors"][0] if item["standardized_connectors"] else "Unknown",
            "num_connectors": len(item["standardized_connectors"]),
            "longitude": item["geometry"]["coordinates"][0],
            "latitude": item["geometry"]["coordinates"][1],
            "max_power_kw": item["max_power_kw"]
        })

    df = pd.DataFrame(rows)

    # Nota: Si la API devolvió muy pocos registros de prueba, duplicamos sintácticamente 
    # para permitir que el modelo in-context tenga suficientes filas de contexto mínimo.
    if len(df) < 5:
        df = pd.concat([df] * 10, ignore_index=True)

    # 3. Definir características (X) y etiqueta objetivo (y)
    X = df[["city", "primary_connector", "num_connectors", "longitude", "latitude"]]
    y = df["max_power_kw"].values

    # Separar en contexto de entrenamiento in-context y datos de prueba para inferencia
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 4. Cargar modelo TabFM preentrenado (Regresión)
    print("Cargando pesos de TabFM desde Hugging Face...")
    model = tabfm_v1_0_0.load(model_type="regression")
    regressor = TabFMRegressor(model=model)

    # 5. Ajuste in-context y predicción zero-shot
    print("Ejecutando inferencia in-context con TabFM...")
    regressor.fit(X_train, y_train)
    predictions = regressor.predict(X_test)

    # 6. Mostrar resultados de la inferencia
    results_df = X_test.copy()
    results_df["Real_Power_KW"] = y_test
    results_df["Predicted_Power_KW"] = predictions

    print("\n--- Resultados de la Inferencia TabFM ---")
    print(results_df[["city", "primary_connector", "Real_Power_KW", "Predicted_Power_KW"]].to_string(index=False))

if __name__ == "__main__":
    ejecutar_inferencia()