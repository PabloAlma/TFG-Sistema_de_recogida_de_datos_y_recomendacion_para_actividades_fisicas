import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar un backend no interactivo
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import welch, periodogram
from scipy.stats import linregress
import nolds  
from sklearn.metrics import pairwise_distances  # Para gráfica de recurrencia
from flask import flash

# Nombres de las columnas
TIEMPO = "TIEMPO"
BPM = "BPM"
RR = "RR"
# Carpeta donde se guardan las gráficas
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)


def rr_vs_time_plot(df, grafRR):
    """
    Genera una gráfica de R-R vs Tiempo y la guarda en el filepath especificado.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df[RR], marker="o", linestyle="-", color="b")
    plt.xlabel("Tiempo")
    plt.ylabel("Intervalo RR (ms)")
    plt.title("Variabilidad del Ritmo Cardíaco (RR vs TIME)")
    plt.grid(True)
    graph_path = grafRR
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def histograma_rr(df, histRR):
    """
    Genera un histograma de los intervalos R-R y lo guarda en el filepath especificado.
    """
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
    return graph_path

def rr_vs_bpm_plot(df, grafRRvsBPM):
    """
    Genera una gráfica de R-R vs BPM y la guarda en el filepath especificado.
    """
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
    return graph_path

def fft_spectrum(df, fftPlot):
    """
    Genera el espectro de potencia utilizando FFT y lo guarda en el filepath especificado.
    """
    fs = 1.0 / np.mean(np.diff(df["time"]))  # Frecuencia de muestreo
    f, Pxx = welch(df[RR], fs=fs, nperseg=min(256, len(df[RR])))
    plt.figure(figsize=(10, 5))
    plt.semilogy(f, Pxx, color='purple')
    plt.xlabel('Frecuencia (Hz)'); plt.ylabel('Densidad espectral (ms²/Hz)')
    plt.title('Espectro de Potencia (FFT)')
    plt.grid(True)
    # Resaltar bandas VLF, LF, HF
    plt.axvspan(0.003, 0.04, color='gray', alpha=0.2, label='VLF')
    plt.axvspan(0.04, 0.15, color='blue', alpha=0.2, label='LF')
    plt.axvspan(0.15, 0.4, color='red', alpha=0.2, label='HF')
    plt.legend()
    graph_path = fftPlot
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def dfa_analysis(df, dfaplot):
    """
    Realiza el análisis DFA y genera la gráfica correspondiente.
    """
    try:
        rr_intervals = df[RR].values
        y = np.cumsum(rr_intervals - np.mean(rr_intervals))  # Serie acumulativa de RR
        min_scale = 4 # Escala mínima para DFA
        max_scale = len(rr_intervals) // 4  # Escala máxima (1/4 de la longitud de la serie)
        scales = np.unique(np.logspace(np.log10(min_scale), np.log10(max_scale), num=20, dtype=int))
        fluctuations = []

        for scale in scales:
            block = len(y) // scale
            if block < 2:
                continue # Evitar bloques demasiado pequeños
            y_block = np.reshape(y[:block * scale], (block, scale))

            rms = []
            for b in y_block:
                x = np.arange(scale)
                c = np.polyfit(x, b, 1)
                t = np.polyval(c, x)

                rms.append(np.sqrt(np.mean((b - t) ** 2)))
            
            fluctuations.append(np.mean(rms))


        alpha = nolds.dfa(rr_intervals)


        log_scales = np.log10(scales[:len(fluctuations)])  # Escalas logarítmicas
        log_fluctuations = np.log10(fluctuations)

        slope, intercept, _, _, _ = linregress(log_scales, log_fluctuations)
        
        # Crear la gráfica
        plt.figure(figsize=(10, 6))
        plt.scatter(log_scales, log_fluctuations, color='blue', label='Datos')
        plt.plot(log_scales, intercept + slope * log_scales, 'r--', 
                label=f'DFA α = {alpha:.2f} (Ajuste lineal)')
        plt.xlabel('log(Escala)')
        plt.ylabel('log(Fluctuación RMS)')
        plt.title(f'Análisis DFA de HRV - Exponente α: {alpha:.2f}')
        plt.legend()
        plt.grid(True)
        graph_path = dfaplot
        plt.savefig(graph_path)
        plt.close()
    except Exception as e:
        flash(f"Error en DFA: {e}")
    
    return graph_path

def poincare_plot(df, poincarePlot):
    """
    Genera la gráfica de Poincaré y la guarda en el filepath especificado.
    """
    rr_n = df[RR].iloc[:-1].values
    rr_n1 = df[RR].iloc[1:].values
    plt.figure(figsize=(8, 8))
    plt.scatter(rr_n, rr_n1, color='green', alpha=0.5)
    plt.xlabel('RRₙ (ms)'); plt.ylabel('RRₙ₊₁ (ms)')
    plt.title('Gráfica de Poincaré')
    
    # Calcular SD1 y SD2
    sd1 = np.std(rr_n1 - rr_n) / np.sqrt(2)
    sd2 = np.std(rr_n1 + rr_n) / np.sqrt(2)
    plt.gca().annotate(f'SD1: {sd1:.2f} ms\nSD2: {sd2:.2f} ms', 
                        xy=(0.7, 0.1), xycoords='axes fraction')
    plt.grid(True)
    graph_path = poincarePlot
    plt.savefig(graph_path)
    plt.close()
    
    return graph_path

def read_excel(filepath):
    """
    Lee un archivo Excel y devuelve un DataFrame de pandas.

    Parámetros:
        filepath (str): Ruta al archivo Excel.
        **kwargs: Argumentos adicionales para pd.read_excel.

    Retorna:
        pd.DataFrame: DataFrame con los datos del archivo Excel o None si hay un error.
    """   
    try:
        df = pd.read_excel(filepath)
        df = df.dropna()  # Eliminar filas con valores NaN
        return df
    except Exception as e:
        flash("Error al leer el archivo:", e)
        return None


# Función para procesar el archivo Excel y generar gráficas

def process_excel_file(filepath, user_id):
    """
    Procesa un archivo Excel con datos de variabilidad del ritmo cardíaco (HRV), generando múltiples
    gráficas relacionadas y almacenándolas en carpetas específicas por usuario.

    Parámetros:
        filepath (str): Ruta al archivo Excel que contiene las columnas de tiempo, BPM y RR.
        user_id (str): Identificador del usuario, utilizado para organizar los resultados en subcarpetas.

    Retorna:
        dict: Diccionario con las claves que identifican cada tipo de gráfica y los valores correspondientes
              a las rutas de los archivos de imagen generados.

              Claves posibles:
                - "RR": Gráfica de intervalos RR vs tiempo.
                - "histograma_RR": Histograma de los intervalos RR.
                - "RR_vs_BPM": Gráfica combinada de RR y BPM vs tiempo.
                - "fft_spectrum": Espectro de potencia (FFT).
                - "dfa_plot": Gráfica del análisis DFA (si hay suficientes datos).
                - "poincare_plot": Gráfica de Poincaré.

    Proceso:
        1. Crea carpetas en static/<user_id>/<nombre_archivo>/ para almacenar resultados.
        2. Lee y procesa el archivo Excel, convirtiendo el tiempo a segundos desde el inicio.
        3. Genera las gráficas si no existen previamente en disco.
        4. Devuelve las rutas de los gráficos generados en un diccionario.
    """

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
    fftPlot = os.path.join(fic_folder, "fft_spectrum.png")
    dfaplot = os.path.join(fic_folder, "dfa_plot.png")
    poincarePlot = os.path.join(fic_folder, "poincare_plot.png")

    #Leer el archivo Excel
    df = read_excel(filepath, header=None, names=[TIEMPO, BPM, RR])
    # Procesar el archivo Excel y generar gráficas
    graph_urls = {}
    # Verificar si el DataFrame tiene las columnas necesarias
    if df is None or len(df.columns) < 3:
        flash("El archivo no contiene las columnas necesarias o está vacío.")
        return graph_urls
    
    t = df.iloc[:,0] # Primer columna la cual es el tirmpo
    b = df.iloc[:,1] # Segunda columna la cual es el BPM
    r = df.iloc[:,2] # Tercera columna la cual es el RR

    # Verificar que las columnas tengan el formato correcto
    if not pd.api.types.is_string_dtype(t) or not pd.api.types.is_numeric_dtype(b) or not pd.api.types.is_numeric_dtype(r):
        flash("Las columnas no tienen el formato correcto. Asegúrate de que 'TIEMPO' sea una cadena, 'BPM' y 'RR' sean numéricos.")
        return graph_urls
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
        graph_path = rr_vs_time_plot(df, grafRR)
    else:
        graph_path = grafRR
    graph_urls["RR"] = graph_path

    # Histograma de R-R
    if not os.path.exists(histRR):
        graph_path = histograma_rr(df, histRR)
    else:
        graph_path = histRR
    graph_urls["histograma_RR"] = graph_path

    # Grafica BPM vs R-R
    if not os.path.exists(grafRRvsBPM):
        graph_path = rr_vs_bpm_plot(df, grafRRvsBPM)
    else:
        graph_path = grafRRvsBPM
    graph_urls["RR_vs_BPM"] = graph_path

    # Espectro de Potencia (FFT)
    if not os.path.exists(fftPlot):
        graph_path = fft_spectrum(df, fftPlot)
    else:
        graph_path = fftPlot
    graph_urls["fft_spectrum"] = graph_path

    # Análisis DFA
    if not os.path.exists(dfaplot) and len(df[RR]) > 100:  # Requiere suficiente datos
        graph_path = dfa_analysis(df, dfaplot)
    elif os.path.exists(dfaplot):
        graph_path = dfaplot
    else:
        dfaplot = None
        flash("No se generó la gráfica DFA porque no hay suficientes datos (se requieren más de 100 intervalos RR).")
    if dfaplot:
        graph_urls["dfa_plot"] = graph_path

    # Gráfica de Poincaré
    if not os.path.exists(poincarePlot):
        graph_path = poincare_plot(df, poincarePlot)
    else:
        graph_path = poincarePlot
    graph_urls["poincare_plot"] = graph_path

    return graph_urls
