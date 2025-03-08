from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Ejemplo simple de validación (reemplazar con lógica real)
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect(url_for('upload.dashboard'))
        else:
            flash('Credenciales incorrectas')
    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))
