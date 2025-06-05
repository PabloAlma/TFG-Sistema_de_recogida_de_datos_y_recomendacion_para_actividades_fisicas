import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar un backend no interactivo
import matplotlib.pyplot as plt
import os
import numpy as np

# Nombres de las columnas
TIEMPO = "TIEMPO"
BPM = "BPM"
RR = "RR"
# Carpeta donde se guardan las gráficas
STATIC_FOLDER = '/static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

def process_excel_file(filepath, user_id):

    # Creamos la carpeta de usuario si no existe
    user_folder = os.path.join(STATIC_FOLDER, user_id)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Creamos la carpeta donde almacenaremos las imagenes del fichero actual
    fic_folder = os.path.join(user_folder, os.path.basename(filepath).split(".")[0])
    if not os.path.exists(fic_folder):
        os.makedirs(fic_folder)

    # Comprobar si las grafícas ya existen para no volver a generarlas
    grafRR = os.path.join(fic_folder, "RRVSTIME.png")
    histRR = os.path.join(fic_folder, "histograma_RR.png")
    grafRRvsBPM = os.path.join(fic_folder, "RR_vs_BPM.png")

    #Leer el archivo Excel
    try:
        df = pd.read_excel(filepath)
        df = df.dropna()  # Eliminar filas con valores NaN
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None
    # Procesar el archivo Excel y generar gráficas
    graph_urls = {}
    t = df.iloc[:,0] # Primer columna la cual es el tirmpo
    b = df.iloc[:,1] # Segunda columna la cual es el BPM
    r = df.iloc[:,2] # Tercera columna la cual es el RR
    # Crear un nuevo DataFrame con las columnas necesarias
    df = pd.DataFrame()
    df[BPM] = b.values
    df[RR] = r.values
    df[TIEMPO] = t.values
    
    df[["time", "value"]] = df[TIEMPO].str.split(expand=True)
    # Combinar tiempo y milisegundos en un formato datetime
    df["time"] = pd.to_datetime(df["time"] + "." + df["value"].astype(int).astype(str), format="%H:%M:%S.%f").dt.time
    df["time"] = pd.to_timedelta(df["time"].astype(str))
    df["time"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()

    # Creemos las gráficas

    # Grafica R-R vs TIME
    if not os.path.exists(grafRR):
        plt.figure(figsize=(10, 5))
        plt.plot(df["time"], df[RR], marker="o", linestyle="-", color="b")
        plt.xlabel("Tiempo")
        plt.ylabel("Intervalo RR (ms)")
        plt.title("Variabilidad del Ritmo Cardíaco (RR vs TIME)")
        plt.grid(True)
        graph_path = grafRR
        plt.savefig(graph_path)
        plt.close()
    else:
        graph_path = grafRR
    graph_urls["RR"] = graph_path

    # Histograma de R-R
    if not os.path.exists(histRR):
        plt.figure(figsize=(10, 5))
        q75, q25 = np.percentile(df[RR], [75, 25])
        iqr = q75 - q25
        bin_width = 2 * iqr / (len(df[RR]) ** (1/3))
        bins_fd = round((df[RR].max() - df[RR].min()) / bin_width)  
        plt.hist(df[RR], bins=bins_fd, color="b", alpha=0.7)
        plt.title("Histograma de Intervalos RR (ms)")
        plt.xlabel("Intervalo RR (milisegundos)")
        plt.ylabel("Frecuencia")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        graph_path = histRR    
        plt.savefig(graph_path)
        plt.close()
    else:
        graph_path = histRR
    graph_urls["histograma_RR"] = graph_path

    # Grafica BPM vs R-R
    if not os.path.exists(grafRRvsBPM):
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Eje Y izquierdo (RR)
        color_rr = "tab:blue"
        ax1.set_xlabel("Tiempo (s)")
        ax1.set_ylabel("Intervalo RR (ms)", color=color_rr)
        ax1.plot(df["time"], df[RR], color=color_rr, marker="o", label="RR")
        ax1.tick_params(axis="y", labelcolor=color_rr)

        # Eje Y derecho (BPM)
        ax2 = ax1.twinx()  # Comparte el mismo eje X
        color_bpm = "tab:red"
        ax2.set_ylabel("BPM", color=color_bpm)
        ax2.plot(df["time"], df[BPM], color=color_bpm, linestyle="--", marker="s", label="BPM")
        ax2.tick_params(axis="y", labelcolor=color_bpm)

        # Título y leyenda
        plt.title("Variabilidad de RR y BPM vs Tiempo")
        fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))

        # Ajustar diseño
        plt.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        graph_path = grafRRvsBPM
        plt.savefig(graph_path)
        plt.close()
    else:
        graph_path = grafRRvsBPM
    graph_urls["RR_vs_BPM"] = graph_path

    return graph_urls
