import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from analysis import process_excel_file

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
usuarios = []  # Lista de usuarios para el selector
usuarios2 = []  # Lista de usuarios para el selector (para admin)
usuario1 = ""  # Usuario seleccionado por el admin
archivos = []  # Lista de archivos subidos por el usuario
usuario2 = ""  # Usuario seleccionado por el admin para comparar
archivos2 = []  # Lista de archivos subidos por el usuario2



if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global usuarios, usuarios2, usuario1, archivos, archivos2, usuario2
    if 'user' not in session:
        return redirect(url_for('index'))  # ¡Usa 'index', no 'oidc_auth.login'!
    user = session['user']['username']
    # En caso de que no haya subido nada, creamos una carpeta asociada a su cuenta donde tendra sus archivos
    user_folder = os.path.join(UPLOAD_FOLDER, user)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    if session['roles'] != 'Administrador':
        archivos = os.listdir(user_folder)  # Obtener lista de archivos subidos
    graph_urls = {}
    graph_urls2 = {}


    # Esto lo hacen los usarios normales
    if request.method == 'POST':
        if 'upload_button' in request.form:
            if 'excel_file' in request.files:
                file = request.files['excel_file']
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
        elif 'seleccion_usuario' in request.form:
            usuario1 = None
            usuarios.clear()  # Limpiamos la lista de usuarios
            # Entramos en la capeta de uploads que es donde estan los archivos de todos los usuarios
            for u in os.listdir(UPLOAD_FOLDER):
                if os.path.isdir(os.path.join(UPLOAD_FOLDER, u)) and u != user:
                    if not usuario1:
                        usuario1 = u
                    usuarios.append(u)
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))
        elif 'seleccion_usuario2' in request.form:
            usuarios2.clear()
            usuario1 = request.form.get('user_principal')
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))
            usuario2 = None
            # Entramos en la carpeta de uploads que es donde estan los archivos de todos los usuarios
            for u in os.listdir(UPLOAD_FOLDER):
                if os.path.isdir(os.path.join(UPLOAD_FOLDER, u)) and u != user and u != usuario1:
                    if not usuario2:
                        usuario2 = u
                    usuarios2.append(u)
            archivos2 = os.listdir(os.path.join(UPLOAD_FOLDER, usuario2))
        elif 'comparar_consigoMismo' in request.form:
            usuario1 = request.form.get('user_principal')
            usuario2 = usuario1  # Para comparar consigo mismo
            usuarios2.clear()
            usuarios2.append(usuario1)  # Agregamos el usuario principal a la lista de usuarios2
            archivos = os.listdir(os.path.join(UPLOAD_FOLDER, usuario1))
            archivos2 = archivos  # Los mismos archivos
        elif 'cambio' in request.form:
            usuario2 = request.form.get('user2')
            archivos2 = os.listdir(os.path.join(UPLOAD_FOLDER, usuario2))
        elif 'comparar_usuario' in request.form:
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

            if usuario1 == usuario2:
                usuario1 = usuario1 + ": " + request.form.get('archivo_Compa_1')
                usuario2 = usuario2 + ": " + request.form.get('archivo_Compa_2')

            


    return render_template('dashboard.html', archivos=archivos, graph_urls=graph_urls, usuarios=usuarios, usuarios2=usuarios2, usuario1=usuario1, archivos2=archivos2, usuario2=usuario2, graph_urls2=graph_urls2, zip=zip)


# Ruta para descargar archivos
@upload_blueprint.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
