from flask import Flask, session

def create_app():
    app = Flask(__name__)
    
    app.secret_key = "DevCrish_Debmalya"
    
    from .portFolio import portFolio_bp
    
    app.register_blueprint(portFolio_bp, url_prefix="/")
    
    return app