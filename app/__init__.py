from flask import Flask, session

def create_app():
    app = Flask(__name__)
    
    app.secret_key = "DevCrish_Debmalya"
    
    from .client import client_bp
    from .dashboard import dashboard_bp
    
    app.register_blueprint(client_bp, url_prefix="/")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    
    
    return app