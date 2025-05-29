from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(required_role=None):
    """
    Asegura que el usuario haya iniciado sesión antes de acceder a la vista.
    Si se especifica `required_role`, también verifica que el usuario tenga ese rol.

    Uso:
    @login_required()  # Solo requiere login
    @login_required(required_role="Admin") # Requiere login y rol "Admin"
    @login_required(required_role=["Admin", "ParishPriest"]) # Requiere login y uno de los roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session:
                flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login', next=request.url_rule.endpoint if request.url_rule else url_for('dashboard')))

            current_role = session["role"]

            allowed = False
            if isinstance(required_role, list):
                if current_role in required_role:
                    allowed = True
            elif isinstance(required_role, str):
                if current_role == required_role:
                    allowed = True
            
            if not allowed:
                flash(f'No tienes los permisos necesarios ({required_role}) para acceder a esta página. Tu rol es: {current_role}.', 'danger')
                return redirect(url_for('auth.login', next=request.url_rule.endpoint if request.url_rule else url_for('dashboard')))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator