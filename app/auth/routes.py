from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import db
from app.main.data.dal.sql_server.sql_models import User # Importa tu modelo de usuario adaptado

bp = Blueprint('auth', __name__) # No necesita url_prefix aquí, se define al registrar

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard')) # Redirige al dashboard si ya está logueado

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = User.query.filter_by(Username=username).first()

        if user is None:
            error = 'Nombre de usuario incorrecto.'
        elif not user.check_password(password): # Usa el método del modelo
            error = 'Contraseña incorrecta.'

        if error is None:
            # Inicio de sesión exitoso
            session.clear()
            session['user_id'] = user.IDUser
            session['username'] = user.Username
            # session['role'] = user.role
            flash(f'Bienvenido {user.Username}!', 'success')
            return redirect(url_for('main.dashboard')) # Ir al dashboard después de login
        else:
            flash(error, 'danger')

    return render_template('auth/login.html', title='Iniciar Sesión')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))