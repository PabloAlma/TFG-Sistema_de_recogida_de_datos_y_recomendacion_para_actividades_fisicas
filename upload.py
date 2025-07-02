# Importación de módulos necesarios
import os
import io
import zipfile
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, send_file
from werkzeug.utils import secure_filename
from analysis import process_excel_file  # Función personalizada para procesar archivos Excel

# Creación del blueprint para agrupar las rutas relacionadas con la subida de archivos
upload_blueprint = Blueprint('upload', __name__)

# Carpeta donde se almacenan los archivos subidos
UPLOAD_FOLDER = 'uploads'

# Extensiones permitidas para los archivos que se pueden subir
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

# Variables globales usadas en el flujo de usuarios y comparación
usuarios = []       # Lista de usuarios disponibles para selección
usuarios2 = []      # Lista de usuarios para segunda comparación
usuario1 = ""       # Usuario principal seleccionado
archivos = []       # Archivos del usuario principal
usuario2 = ""       # Segundo usuario seleccionado para comparación
archivos2 = []      # Archivos del usuario secundario
graph_urls = {}     # Diccionario con URLs de gráficas del usuario principal
graph_urls2 = {}    # Diccionario con URLs de gráficas del usuario secundario

# Crea la carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def cerrar():
    """
    Limpia las variables globales y la sesión del usuario.
    Esta función se utiliza para reiniciar el estado del dashboard y limpiar las listas de usuarios,
    así como las URLs de gráficas generadas.
    Variables globales afectadas:
        usuarios, usuarios2: listas de usuarios para comparación.
        usuario1, usuario2: usuarios seleccionados.
        graph_urls, graph_urls2: diccionarios con rutas a las gráficas generadas.
    """
    global usuarios, usuarios2, usuario1, graph_urls, graph_urls2
    usuarios.clear()  # Limpia la lista de usuarios
    usuarios2.clear()  # Limpia la lista de usuarios secundarios
    usuario1 = ""
    graph_urls.clear()  # Limpia las URLs de gráficas
    graph_urls2.clear()  # Limpia las URLs de gráficas secundarias

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida (.xls o .xlsx).

    Parámetros:
        filename (str): Nombre del archivo a verificar.

    Retorna:
        bool: True si la extensión es válida, False en caso contrario.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta del dashboard principal donde ocurre toda la interacción del usuario
@upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Ruta principal del dashboard del usuario.

    Esta función maneja múltiples funcionalidades según el formulario enviado, entre ellas:
    - Subida de archivos Excel (.xls, .xlsx).
    - Generación de gráficas a partir de un archivo Excel usando `process_excel_file`.
    - Selección de usuarios y archivos para comparar resultados (modo administrador).
    - Descarga de gráficos en formato ZIP (individual o comparativo).
    
    Variables globales afectadas:
        usuarios, usuarios2: listas de usuarios para comparación.
        usuario1, usuario2: usuarios seleccionados.
        archivos, archivos2: archivos seleccionados para cada usuario.
        graph_urls, graph_urls2: diccionarios con rutas a las gráficas generadas.

    Renderiza:
        dashboard.html con todos los elementos necesarios según el contexto del usuario.
    """
    global usuarios, usuarios2, usuario1, archivos, archivos2, usuario2, graph_urls, graph_urls2

    print("upload", graph_urls)
    
    # Redirige si el usuario no está autenticado
    if 'user' not in session:
        return redirect(url_for('index'))  # ¡Usa 'index', no 'oidc_auth.login'!

    user = session['user']['username']
    
    # Crea carpeta personal del usuario si no existe
    user_folder = os.path.join(UPLOAD_FOLDER, user)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    # Carga archivos si el usuario no es administrador
    if session['roles'] != 'Administrador':
        archivos = os.listdir(user_folder)

    # Procesamiento de formularios

    if request.method == 'POST':
        # Subida de archivo Excel
        if 'upload_button' in request.form:
            if 'excel_file' in request.files:
                file = request.files['excel_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(user_folder, filename)
                    file.save(filepath)
                    flash("Archivo subido correctamente.")
                    return redirect(request.url)

        # Generar gráficas a partir de un archivo Excel
        elif 'generate_button' in request.form:
            graph_urls.clear()
            file_name = request.form.get('file_name')
            if not file_name or file_name not in archivos:
                flash("Selecciona un archivo válido.")
                return redirect(request.url)
            filepath = os.path.join(user_folder, file_name)
            graph_urls = process_excel_file(filepath, user)

        # Seleccionar primer usuario para comparación (modo admin)
        elif 'seleccion_usuario' in request.form:
            usuario1 = None
            usuarios.clear()
            for u in os.listdir(UPLOAD_FOLDER):
                if os.path.isdir(os.path.join(UPLOAD_FOLDER, u)) and u != user and os.listdir(os.path.join(UPLOAD_FOLDER, u)) != []:
                    if not usuario1:
                        usuario1 = u
                    usuarios.append(u)
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))

        # Seleccionar segundo usuario para comparación (modo admin)
        elif 'seleccion_usuario2' in request.form:
            graph_urls2.clear()
            usuarios2.clear()
            usuario1 = request.form.get('user_principal')
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))
            usuario2 = None
            for u in os.listdir(UPLOAD_FOLDER):
                if os.path.isdir(os.path.join(UPLOAD_FOLDER, u)) and u != user and u != usuario1 and os.listdir(os.path.join(UPLOAD_FOLDER, u)) != []:
                    if not usuario2:
                        usuario2 = u
                    usuarios2.append(u)
            archivos2 = os.listdir(os.path.join(UPLOAD_FOLDER, usuario2))

        # Comparar el usuario consigo mismo (modo admin)
        elif 'comparar_consigoMismo' in request.form:
            graph_urls2.clear()
            usuario1 = request.form.get('user_principal')
            usuario2 = usuario1
            usuarios2.clear()
            usuarios2.append(usuario1)
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))
            archivos2 = archivos

        # Cambio del segundo usuario seleccionado para comparación
        elif 'cambio' in request.form:
            graph_urls2.clear()
            usuario2 = request.form.get('user2')
            archivos2 = os.listdir(os.path.join(UPLOAD_FOLDER, usuario2))

        # Comparar archivos entre dos usuarios
        elif 'comparar_usuario' in request.form:
            graph_urls2.clear()
            graph_urls.clear()
            usuario1 = request.form.get('user_principal')
            usuario2 = request.form.get('user2')
            archivos2 = os.listdir(os.path.join(UPLOAD_FOLDER, usuario2))
            if not usuario2:
                flash("Selecciona un usuario para comparar.")
                return redirect(request.url)
            user_folder1 = os.path.join(UPLOAD_FOLDER, usuario1)
            user_folder2 = os.path.join(UPLOAD_FOLDER, usuario2)
            filepath1 = os.path.join(user_folder1, request.form.get('archivo_Compa_1'))
            filepath2 = os.path.join(user_folder2, request.form.get('archivo_Compa_2'))
            graph_urls = process_excel_file(filepath1, usuario1)
            graph_urls2 = process_excel_file(filepath2, usuario2)

            # Si el mismo usuario se compara con dos archivos distintos, se renombran para visualización
            if usuario1 == usuario2:
                usuario1 = usuario1 + ": " + request.form.get('archivo_Compa_1').split('.')[0]
                usuario2 = usuario2 + ": " + request.form.get('archivo_Compa_2').split('.')[0]

        # Descargar gráficas en un archivo ZIP
        elif 'download_button' in request.form:
            images = graph_urls.values()
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for image_path in images:
                    zip_file.write(image_path, os.path.basename(image_path))
            zip_buffer.seek(0)
            return send_file(zip_buffer, as_attachment=True, download_name='graficas.zip', mimetype='application/zip')

        # Descargar gráficas de comparación en un archivo ZIP
        elif 'download_button2' in request.form:
            images1 = graph_urls.values()
            images2 = graph_urls2.values()
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for image_path in images1:
                    carpeta = os.path.join(usuario1, os.path.basename(image_path))
                    zip_file.write(image_path, carpeta)
                for image_path in images2:
                    carpeta = os.path.join(usuario2, os.path.basename(image_path))
                    zip_file.write(image_path, carpeta)
            zip_buffer.seek(0)
            return send_file(zip_buffer, as_attachment=True, download_name='graficas_comparacion.zip', mimetype='application/zip')

    # Renderiza el dashboard con todas las variables necesarias
    return render_template(
        'dashboard.html',
        archivos=archivos,
        graph_urls=graph_urls,
        usuarios=usuarios,
        usuarios2=usuarios2,
        usuario1=usuario1,
        archivos2=archivos2,
        usuario2=usuario2,
        graph_urls2=graph_urls2,
        zip=zip
    )


