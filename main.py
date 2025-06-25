# Importaciones necesarias de Flask y otros módulos
from flask import Flask, redirect, url_for, render_template, session, Blueprint
# Importación de elementos desde el módulo upload
from upload import upload_blueprint, usuarios, usuarios2, usuario1, graph_urls, graph_urls2
# OpenIDConnect para la autenticación mediante OIDC ( Keycloak)
from flask_oidc import OpenIDConnect
# Librería JWT para decodificar tokens (sin verificar firma en este caso)
import jwt  

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación para integración con OIDC (por ejemplo, con Keycloak)
app.config.update({
    "SECRET_KEY": "clave-secreta-segura",  # Clave para firmar cookies y sesiones
    "OIDC_CLIENT_SECRETS": "client_secrets.json",  # Archivo con configuración del cliente OIDC
    "OIDC_SCOPES": ["openid", "email", "profile", "roles"],  # Permisos solicitados al proveedor OIDC
    "OIDC_INTROSPECTION_AUTH_METHOD": "client_secret_post",  # Método de autenticación para introspección
    "OIDC_CALLBACK_ROUTE": "/oidc_callback",  # Ruta de redirección después del login
    "OVERWRITE_REDIRECT_URI": "http://localhost:5000/oidc_callback"  # URI usada en desarrollo
})

# Inicializa la extensión Flask-OIDC con la configuración anterior
oidc = OpenIDConnect(app)

# Registro del blueprint relacionado con la funcionalidad de subida de archivos
app.register_blueprint(upload_blueprint, url_prefix='/upload') 

# Ruta que maneja el callback desde el proveedor OIDC ( con Keycloak)
@app.route("/oidc_callback")
def oidc_callback():
    return oidc.callback()  # Manejo automático del callback por Flask-OIDC

# Ruta de inicio (página principal)
@app.route("/") 
def inicio():
    return render_template("index.html")  # Renderiza la plantilla HTML principal

# Ruta para redirigir al usuario a la página de registro de Keycloak
@app.route("/registro")
def registro():
    registration_url = (
        f"{oidc.client_secrets['issuer']}/protocol/openid-connect/registrations?"
        f"client_id={oidc.client_secrets['client_id']}&"
        f"redirect_uri={url_for('inicio', _external=True)}&"
        f"response_type=code&scope=openid email profile"
    )
    return redirect(registration_url)  # Redirige al usuario a la página de registro

# Ruta protegida que requiere inicio de sesión
@app.route("/iniciar_sesion")
@oidc.require_login  # Middleware que fuerza autenticación OIDC
def iniciar_sesion():
    try:
        # Obtiene el perfil del usuario autenticado desde la sesión
        user = session.get('oidc_auth_profile', {})
        if not user:
            raise ValueError("No se recibieron datos del usuario desde Keycloak")

        # Obtiene el token de ID desde la sesión
        id_token = session.get('oidc_auth_token', {}).get('id_token')

        try:            
            # Decodifica el token ID sin verificar la firma para extraer los roles
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
            roles = decoded_token.get('resource_access', {}).get('Usuario1', []).get('roles', [])[0]
            
        except Exception as e:
            print("Error al obtener roles:", str(e))
            roles = []

        # Guarda los roles en la sesión
        session['roles'] = roles

        if not id_token:
            raise ValueError("No se pudo obtener el token ID")
        
        # Guarda información del usuario en la sesión
        session['user'] = {
            'id': user.get('sub',''),
            'username': user.get('name', 'Usuario'),
            'email': user.get('email', '')
        }
        session['id_token'] = id_token  # Guarda el ID Token en la sesión
        session.modified = True  # Marca la sesión como modificada para forzar persistencia
    except Exception as e:
        print("Error al obtener datos de usuario:", str(e))
        return str(e), 500
    return redirect(url_for('upload.dashboard'))  # Redirige al dashboard después de iniciar sesión

# Ruta para cerrar sesión (logout)
@app.route("/cerrar_sesion")
def cerrar_sesion():
    if 'id_token' not in session:  # Si no hay ID Token, no hay sesión que cerrar
        session.clear()
        return redirect(url_for('inicio'))
    
    # Construye la URL de logout de Keycloak
    logout_url = (
        f"{oidc.client_secrets['issuer']}/protocol/openid-connect/logout?"
        f"post_logout_redirect_uri={url_for('inicio', _external=True)}&"
        f"client_id={oidc.client_secrets['client_id']}&"
        f"id_token_hint={session['id_token']}"
    )
    # Limpieza de sesión local y estructuras de datos auxiliares
    session.clear()  # Limpia la sesión de Flask
    usuarios.clear()  # Limpia la lista de usuarios
    usuarios2.clear()  # Limpia la lista de usuarios secundarios
    usuario1 = ""
    graph_urls.clear()  # Limpia las URLs de gráficas
    graph_urls2.clear()  # Limpia las URLs de gráficas secundarias

    return redirect(logout_url)  # Redirige a Keycloak para logout global

# Punto de entrada de la aplicación Flask en modo desarrollo
if __name__ == "__main__":
    app.run(debug=True)
