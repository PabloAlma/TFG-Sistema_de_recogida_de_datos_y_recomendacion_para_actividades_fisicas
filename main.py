from flask import Flask, redirect, url_for, render_template, session, Blueprint
from upload import upload_blueprint, usuarios, usuarios2, usuario1
from flask_oidc import OpenIDConnect
import jwt  # Asegúrate de tener PyJWT instalado: pip install PyJWT

app = Flask(__name__)

app.config.update({
    "SECRET_KEY": "clave-secreta-segura",
    "OIDC_CLIENT_SECRETS": "client_secrets.json",
    "OIDC_SCOPES": ["openid", "email", "profile", "roles"],
    "OIDC_INTROSPECTION_AUTH_METHOD": "client_secret_post",
    "OIDC_CALLBACK_ROUTE": "/oidc_callback",  
    "OVERWRITE_REDIRECT_URI": "http://localhost:5000/oidc_callback"  
})
oidc = OpenIDConnect(app)
app.register_blueprint(upload_blueprint, url_prefix='/upload') 

@app.route("/oidc_callback")
def oidc_callback():
    return oidc.callback()  # Manejo propio de Flask-OIDC

@app.route("/") 
def inicio():
    return render_template("index.html")  

@app.route("/registro")
def registro():
    registration_url = (
        f"{oidc.client_secrets['issuer']}/protocol/openid-connect/registrations?"
        f"client_id={oidc.client_secrets['client_id']}&"
        f"redirect_uri={url_for('inicio', _external=True)}&"
        f"response_type=code&scope=openid email profile"
    )
    return redirect(registration_url)

@app.route("/iniciar_sesion")
@oidc.require_login
def iniciar_sesion():
    try:
        user = session.get('oidc_auth_profile', {})
        if not user:
            raise ValueError("No se recibieron datos del usuario desde Keycloak")

        id_token = session.get('oidc_auth_token', {}).get('id_token')

        try:            
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
            roles = decoded_token.get('resource_access', {}).get('Usuario1', []).get('roles', [])[0]
            
        except Exception as e:
            print("Error al obtener roles:", str(e))
            roles = []

        session['roles'] = roles  # Guarda los roles en la sesión

        if not id_token:
            raise ValueError("No se pudo obtener el token ID")
        
        session['user'] = {
            'id': user.get('sub',''),
            'username': user.get('name', 'Usuario'),
            'email': user.get('email', '')
        }
        session['id_token'] = id_token # Guarda el ID Token en la sesión
        session.modified = True  # Fuerza la persistencia
    except Exception as e:
        print("Error al obtener datos de usuario:", str(e))
        return str(e), 500
    return redirect(url_for('upload.dashboard'))


@app.route("/cerrar_sesion")
def cerrar_sesion():
    if 'id_token' not in session:# Si no hay ID Token, no hay sesión que cerrar
        session.clear()
        return redirect(url_for('inicio'))
    
    logout_url = (
        f"{oidc.client_secrets['issuer']}/protocol/openid-connect/logout?"
        f"post_logout_redirect_uri={url_for('inicio', _external=True)}&"
        f"client_id={oidc.client_secrets['client_id']}&"
        f"id_token_hint={session['id_token']}"
    )
    session.clear()  # Limpia la sesión de Flask
    usuarios.clear()  # Limpia la lista de usuarios
    usuarios2.clear()  # Limpia la lista de usuarios secundarios
    usuario1 = ""

    return redirect(logout_url)  # Redirige a Keycloak para logout global


if __name__ == "__main__":
    app.run(debug=True)
