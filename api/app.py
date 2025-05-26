from flask import Flask
from api.routes import api_bp

def create_app():
    """
    Creating and configuring Flask application.
    
    Returns:
        Flask: Flask application object
    """
    app = Flask(__name__)
    
    # Blueprint registration
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
