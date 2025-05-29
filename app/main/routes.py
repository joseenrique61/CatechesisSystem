from flask import Blueprint, render_template, session, redirect, url_for, flash
# from app.models import Usuario # Podrías necesitar modelos para datos del dashboard

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # La página raíz redirige al dashboard si está logueado, o al login si no
    if 'id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    if 'id' not in session:
        flash('Debes iniciar sesión para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))

    match session["role"]:
        case "ParishPriest":
            return redirect(url_for("parish_priest.dashboard"))
        case "Admin":
            return redirect(url_for("admin.dashboard"))
        case "Catechist":
            return redirect(url_for("catechist.dashboard"))
            