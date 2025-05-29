import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

# Instanciar extensiones fuera de la fábrica
db = SQLAlchemy()
# Podrías añadir otras aquí (Migrate, LoginManager, etc.) más adelante

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones con la app
    db.init_app(app)

    # Registrar Blueprints
    from app.admin.routes import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.parish_priest.routes import bp as parish_priest_bp
    app.register_blueprint(parish_priest_bp, url_prefix='/parish_priest')

    from app.catechist.routes import bp as catechist_bp
    app.register_blueprint(catechist_bp, url_prefix='/catechist')

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp) # Sin prefijo para rutas como '/'

    # Asegurar que los modelos sean conocidos por SQLAlchemy dentro del contexto de la app
    # Necesario si no usas algo como Flask-Migrate que los importa
    with app.app_context():
        from .main.data.dal.sql_server import sql_models # Importa tus modelos adaptados

    print(f"Aplicación creada. Debug: {app.debug}")

    return app

def get_dal():
    """
    Devuelve la instancia de DAL (Data Access Layer) para interactuar con la base de datos.
    """
    from app.main.data.dal.sql_server.sql_dal import SQLAlchemyDAL
    return SQLAlchemyDAL(db.session) if os.environ.get('DB_TYPE') == 'mssql' else None

dal = get_dal()