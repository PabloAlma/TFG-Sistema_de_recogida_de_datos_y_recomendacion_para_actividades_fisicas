import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from analysis import process_excel_file

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))  # ¡Usa 'index', no 'oidc_auth.login'!
    user = session['user']['username']
    # En caso de que no haya subido nada, creamos una carpeta asociada a su cuenta donde tendra sus archivos
    user_folder = os.path.join(UPLOAD_FOLDER, user)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    archivos = os.listdir(user_folder)  # Obtener lista de archivos subidos
    graph_urls = {}

    if request.method == 'POST':
        if 'upload_button' in request.form:
            if 'excel_file' in request.files:
                file = request.files['excel_file']
                print("Archivo recibido:", file)  # Debug
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(user_folder, filename)
                    file.save(filepath)
                    flash("Archivo subido correctamente.")
                    return redirect(request.url)
        elif 'generate_button' in request.form:  # Botón de generar
            file_name = request.form.get('file_name')  # Obtener el archivo seleccionado
            if not file_name or file_name not in archivos:
                flash("Selecciona un archivo válido.")
                return redirect(request.url)

            filepath = os.path.join(user_folder, file_name)
            
            graph_urls = process_excel_file(filepath, user)  # Procesar el archivo

    return render_template('dashboard.html', archivos=archivos, graph_urls=graph_urls)

# Ruta para descargar archivos
@upload_blueprint.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
