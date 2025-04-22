from flask import Flask
from api.routes import api_bp

def create_app():
    """
    Створення та налаштування Flask додатку.
    
    Returns:
        Flask: Об'єкт Flask додатку
    """
    app = Flask(__name__)
    
    # Реєстрація Blueprint
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
