import os
import urllib.parse
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG') == '1'

    # Configuración DB para Flask-SQLAlchemy
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_DATABASE = os.environ.get('DB_DATABASE')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

    # Codificar la contraseña por si tiene caracteres especiales para la URI
    safe_password = urllib.parse.quote_plus(DB_PASSWORD)
    # Reemplazar espacios en el driver con '+' para la URI
    safe_driver = DB_DRIVER.replace(' ', '+')

    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://{DB_USERNAME}:{safe_password}@{DB_SERVER}/{DB_DATABASE}?'
        f'driver={safe_driver}'
        # Añadir ;Encrypt=yes;TrustServerCertificate=yes; si es necesario por la config de SQL Server/Azure
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = FLASK_DEBUG # Imprime consultas SQL en modo debug (útil para depurar)

    UPLOAD_FOLDER = os.path.join(basedir, "app", 'static', 'uploads')