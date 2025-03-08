import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from analysis import process_excel_file

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

""" @upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    graph_url = None  # Inicializamos la variable para evitar errores

    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('No se encontró el archivo')
            return redirect(request.url)
        file = request.files['excel_file']
        if file.filename == '':
            flash('No se seleccionó archivo')
            return redirect(request.url)
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Procesar el archivo Excel y generar la gráfica
        graph_url = process_excel_file(filepath)

    # Obtener la lista de archivos subidos
    archivos = os.listdir(UPLOAD_FOLDER)

    return render_template('dashboard.html', graph_url=graph_url, archivos=archivos) """

def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    archivos = os.listdir(UPLOAD_FOLDER)  # Obtener lista de archivos subidos
    graph_urls = {}

    if request.method == 'POST':
        if 'excel_file' in request.files:
            file = request.files['excel_file']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                flash("Archivo subido correctamente.")
                return redirect(request.url)

        file_name = request.form.get('file_name')  # Obtener el archivo seleccionado
        if file_name and file_name in archivos:
            filepath = os.path.join(UPLOAD_FOLDER, file_name)
            graph_urls = process_excel_file(filepath)  # Procesar el archivo

    return render_template('dashboard.html', archivos=archivos, graph_urls=graph_urls)

@upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    archivos = os.listdir(UPLOAD_FOLDER)  # Obtener lista de archivos subidos
    graph_urls = {}

    if request.method == 'POST':
        file_name = request.form.get('file_name')  # Obtener el archivo seleccionado
        if not file_name or file_name not in archivos:
            flash("Selecciona un archivo válido.")
            return redirect(request.url)

        filepath = os.path.join(UPLOAD_FOLDER, file_name)
        graph_urls = process_excel_file(filepath)  # Procesar el archivo

    return render_template('dashboard.html', archivos=archivos, graph_urls=graph_urls)

# Ruta para descargar archivos
@upload_blueprint.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
