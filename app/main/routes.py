from flask import Blueprint, render_template, session, redirect, url_for, flash
# from app.models import Usuario # Podrías necesitar modelos para datos del dashboard

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # La página raíz redirige al dashboard si está logueado, o al login si no
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))

    # Aquí podrías cargar datos específicos del usuario o globales para el dashboard
    username = session.get('username', 'Invitado')
    role = session.get('role', 'Desconocido')

    # Pasa datos a la plantilla
    return render_template('main/dashboard.html', title='Dashboard', username=username, role=role)