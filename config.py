import os
import urllib.parse
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG') == '1'

    # Configuración DB
    DB_TYPE = os.environ.get('DB_TYPE', 'mongodb')

    if DB_TYPE == "mssql":
        SQL_SERVER_DB_SERVER = os.environ.get('SQL_SERVER_DB_SERVER')
        SQL_SERVER_DB_DATABASE = os.environ.get('SQL_SERVER_DB_DATABASE', 'ParishDatabase')
        SQL_SERVER_DB_USERNAME = os.environ.get('SQL_SERVER_DB_USERNAME')
        SQL_SERVER_DB_PASSWORD = os.environ.get('SQL_SERVER_DB_PASSWORD', '')
        SQL_SERVER_DB_DRIVER = os.environ.get('SQL_SERVER_DB_DRIVER', 'ODBC Driver 17 for SQL Server')

        # Codificar la contraseña por si tiene caracteres especiales para la URI
        safe_password = urllib.parse.quote_plus(SQL_SERVER_DB_PASSWORD)
        # Reemplazar espacios en el driver con '+' para la URI
        safe_driver = SQL_SERVER_DB_DRIVER.replace(' ', '+')

        SQLALCHEMY_DATABASE_URI = (
            f'mssql+pyodbc://{SQL_SERVER_DB_USERNAME}:{safe_password}@{SQL_SERVER_DB_SERVER}/{SQL_SERVER_DB_DATABASE}?'
            f'driver={safe_driver}'
            # Añadir ;Encrypt=yes;TrustServerCertificate=yes; si es necesario por la config de SQL Server/Azure
        )

        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SQLALCHEMY_ECHO = FLASK_DEBUG # Imprime consultas SQL en modo debug (útil para depurar)
    
    else:
        MongoDB_SERVER=os.environ.get('MongoDB_SERVER')
        MongoDB_DATABASE=os.environ.get('MongoDB_DATABASE', 'ParishDatabase')
        MongoDB_USERNAME=os.environ.get('MongoDB_USERNAME')
        MongoDB_PASSWORD=os.environ.get('MongoDB_PASSWORD')

        MONGODB_SETTINGS = {
            "db": MongoDB_DATABASE,
            "host": MongoDB_SERVER,
            "username": MongoDB_USERNAME,
            "password": MongoDB_PASSWORD
        }

    UPLOAD_FOLDER = os.path.join(basedir, "app", 'static', 'uploads')