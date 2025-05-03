from app import create_app

# Crea la instancia de la aplicación usando la fábrica
app = create_app()

if __name__ == '__main__':
    # Obtener host y port de la configuración si los defines allí, o usar defaults
    host = app.config.get('HOST', '127.0.0.1')
    port = int(app.config.get('PORT', 5000))
    # El modo debug se controla principalmente por FLASK_DEBUG en .env/Config
    app.run(host=host, port=port, debug=app.debug)