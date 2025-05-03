import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv() # Carga desde .env

DB_SERVER = os.environ.get('DB_SERVER')
DB_DATABASE = os.environ.get('DB_DATABASE')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = urllib.parse.quote_plus(os.environ.get('DB_PASSWORD', ''))
DB_DRIVER = os.environ.get('DB_DRIVER', '{ODBC Driver 17 for SQL Server}').replace(' ', '+')

db_url = (
    f'mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}?'
    f'driver={DB_DRIVER}'
)

# --- ¡Define aquí los esquemas que quieres inspeccionar! ---
schemas_to_inspect = ['catechesis', 'book', 'certificate', 'classinformation', 'locationinformation', 'person', 'personalinformation', 'schoolinformation', 'user'] # Ajusta esta lista

# Construye la parte de los esquemas para el comando
schema_options = ','.join([f'{s}' for s in schemas_to_inspect])

output_file = 'app/models_generated.py'

print("Ejecuta en la terminal:")
# Asegúrate de que la URL esté entre comillas por si tiene caracteres especiales
print(f'sqlacodegen "{db_url}" --generator declarative --options nobidi --noviews --schemas {schema_options} --outfile {output_file}')