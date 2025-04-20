from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

auth_blueprint = Blueprint('auth', __name__)

# Configuramos la base de datos SQLite
DATABASE = 'users.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DATABASE):
        with get_db() as db:
            db.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()

# Inicializar la base de datos al importar
init_db()

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #email = request.form.get('email', '') # Lo voy a dejar como un opcional para mas adelante

        try:
            with get_db() as db:
                # Verificamos si el usuario ya existe
                if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
                    # El usuario ya existe
                    flash('Nombre de usuario ya existente', 'YaExiste')
                else:
                    # Generamos el hash de la contraseña
                    password_hash = generate_password_hash(password)


                    # Insertamos nuevo usuario en la DB
                    db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
                    db.commit()
                    
                    # Flash y redirigir a login
                    flash('Usuario registrado exitosamente')
                    return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error en el registro: {str(e)}')
    return render_template('register.html')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Buscamos el usuario en la base de datos
        with get_db() as db:
            user = db.execute(
                'SELECT * FROM users WHERE username = ?', 
                (username,)
            ).fetchone()
        
        # Verificamos si el usuario existe y si la contraseña es correcta
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = {
                'id': user['id'],
                'username': user['username'],
                #'email': user['email'] # Lo dejamos por si en un futuro usamos correo electronico
            }
            return redirect(url_for('upload.dashboard'))
        else:
            flash('Credenciales incorrectas', 'MalosCredenciales')
    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))
