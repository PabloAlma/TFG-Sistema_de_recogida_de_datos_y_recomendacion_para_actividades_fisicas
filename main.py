from flask import Flask
from auth import auth_blueprint
from upload import upload_blueprint

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto en producción

# Registrar blueprints para manejar rutas de autenticación y carga
app.register_blueprint(auth_blueprint)
app.register_blueprint(upload_blueprint)

if __name__ == '__main__':
    app.run(debug=True)