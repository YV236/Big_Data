# Імпорт основних компонентів для зручного доступу
from .app import create_app
from .routes import api_bp

# Визначення версії API
__version__ = '1.0.0'

# Експорт тільки певних компонентів при використанні "from api import *"
__all__ = ['create_app', 'api_bp']
