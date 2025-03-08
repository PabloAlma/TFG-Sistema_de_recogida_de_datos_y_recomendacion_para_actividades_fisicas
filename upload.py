import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from analysis import process_excel_file

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@upload_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
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
        # Procesar el archivo excel y generar la gráfica
        graph_url = process_excel_file(filepath)
        return render_template('dashboard.html', graph_url=graph_url)
    
    return render_template('dashboard.html')
