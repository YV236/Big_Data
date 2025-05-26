# Import main components for convenient access
from .app import create_app
from .routes import api_bp

# API version definition
__version__ = '1.0.0'

# Export only specific components when using "from api import *"
__all__ = ['create_app', 'api_bp']
