import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar un backend no interactivo
import matplotlib.pyplot as plt
import os
# Carpeta donde se guardan las gráficas
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

def process_excel_file(filepath):
    # Leer el archivo Excel
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None

    # Mostrar nombres reales de las columnas para depuración
    print("Columnas encontradas en el archivo:", df.columns)

    # Verificar si las columnas existen en el DataFrame
    required_columns = ["TIME ", "WIMU_04 HRM HeartRate(bpm) ", "WIMU_04 HRM R-R(mSec) "]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: No se encontró la columna '{col}' en el archivo.")
            return None
        
    # Eliminar valores vacíos
    df = df.dropna(subset=required_columns)

    # Renombrar columnas para facilitar el acceso
    df = df.rename(columns={
        'TIME ': 'TIME',
        'WIMU_04 HRM HeartRate(bpm) ': 'HEART_RATE',
        'WIMU_04 HRM R-R(mSec) ': 'RR_INTERVAL'
    })

    # Comprobar que las columnas necesarias existen
    if not all(col in df.columns for col in ['TIME', 'HEART_RATE', 'RR_INTERVAL']):
        print("Faltan columnas necesarias en el archivo.")
        return None

    # Convertir TIME a formato numérico si es necesario
    try:
        df['TIME'] = pd.to_numeric(df['TIME'], errors='coerce')
    except:
        print("No se pudo convertir la columna TIME a numérico.")

    # Generar gráficas
    graph_urls = {}

    # Gráfico 1: Ritmo Cardiaco en el tiempo
    plt.figure()
    plt.plot(df['TIME'], df['HEART_RATE'], label="Ritmo Cardíaco", color='blue')
    plt.xlabel("Tiempo")
    plt.ylabel("Frecuencia Cardíaca (bpm)")
    plt.title("Ritmo Cardíaco en el Tiempo")
    plt.legend()
    graph_path1 = os.path.join(STATIC_FOLDER, 'heart_rate.png')
    plt.savefig(graph_path1)
    plt.close()
    graph_urls['heart_rate'] = '/static/heart_rate.png'

    # Gráfico 2: Variabilidad del Ritmo Cardiaco (R-R Interval)
    plt.figure()
    plt.plot(df['TIME'], df['RR_INTERVAL'], label="Intervalo R-R", color='red')
    plt.xlabel("Tiempo")
    plt.ylabel("Intervalo R-R (ms)")
    plt.title("Variabilidad del Ritmo Cardiaco (R-R Interval)")
    plt.legend()
    graph_path2 = os.path.join(STATIC_FOLDER, 'rr_interval.png')
    plt.savefig(graph_path2)
    plt.close()
    graph_urls['rr_interval'] = '/static/rr_interval.png'

    return graph_urls
