"""
Gunicorn startup file for Azure App Service
"""
from app import app

if __name__ == "__main__":
    app.run()