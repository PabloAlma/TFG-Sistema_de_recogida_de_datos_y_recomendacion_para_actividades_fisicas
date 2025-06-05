from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def configure_keycloak(app):
    oauth.init_app(app)
    oauth.register(
        name='keycloak',
        client_id='tu-client-id',
        client_secret='tu-client-secret',
        server_metadata_url='https://<DOMINIO>/realms/<REALM>/protocol/openid-connect/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email',
        }
    )
