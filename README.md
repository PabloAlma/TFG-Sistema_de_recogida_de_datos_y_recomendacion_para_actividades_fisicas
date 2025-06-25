# Sistema de análisis de HRV (Heart Rate Variability)

Este proyecto consiste en una aplicación web desarrollada en Python con Flask que permite a los usuarios subir ficheros Excel con registros de frecuencia cardíaca (BPM, intervalos RR) y obtener un análisis de variabilidad de la frecuencia cardíaca (HRV). La app genera métricas y visualizaciones útiles para evaluar aspectos como recuperación, estrés o fatiga.

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener:

- Python 3.8 o superior instalado.
- Keycloak 26.2.2 descomprimido para la autenticación de usuarios.

## Instalación

1. **Clona o descarga el repositorio.**
    Puedes clonarlo con el siguiente comando:

    git clone git@github.com:PabloAlma/TFG-Sistema_de_recogida_de_datos_y_recomendacion_para_actividades_fisicas.git <Nombre-de-la-carpeta>

2. **Instalar dependecioas**
    Ejecuta el siguiente comando para poder instalar las dependencias

    pip install -r requirements.txt

3. **Configurar keycloak**
    Decomprime el archivo y accede a la carpeta /bin dentro de este. Una vez aqui podras ejecutar "kc.bat star-dev" para poder ejecutar en local y modo developer keycloak para poder usar el prototipo de la app en local.

4. **Ejecuta la aplicación**
    Ejecuta el siguiente comando para poder poner la aplicación en marcha:
    python main.py

