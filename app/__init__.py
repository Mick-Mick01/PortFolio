from flask import Flask, session

def create_app():
    app = Flask(__name__)
    
    app.secret_key = "DevCrish_Debmalya"
    
    from .portFolio import portFolio_bp
    from .Gigamart import Gigamart_bp
    from .Host_Your_HTML import hosting_bp
    
    app.register_blueprint(portFolio_bp, url_prefix="/")
    app.register_blueprint(Gigamart_bp, url_prefix="/Gigamart")
    app.register_blueprint(hosting_bp, url_prefix="/DevCrishKha")
    
    return app