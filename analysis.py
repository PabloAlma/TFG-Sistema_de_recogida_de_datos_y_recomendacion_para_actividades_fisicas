import pandas as pd
import matplotlib.pyplot as plt
import os

def process_excel_file(filepath):
    # Leer el archivo Excel
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None
    
    # Comprobar que la columna 'ritmo' existe
    if 'ritmo' not in df.columns:
        print("La columna 'ritmo' no se encontró")
        return None
    
    # Generar una gráfica simple del ritmo cardiaco
    plt.figure()
    df['ritmo'].plot(title="Ritmo Cardiaco")
    plt.xlabel("Índice")
    plt.ylabel("Ritmo")
    
    # Guardar la gráfica en la carpeta 'static'
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    graph_path = os.path.join(static_folder, 'graph.png')
    plt.savefig(graph_path)
    plt.close()
    
    # Retornar la ruta relativa de la gráfica para que se muestre en el HTML
    return '/static/graph.png'
