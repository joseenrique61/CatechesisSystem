from app import dal
from flask import Blueprint, render_template, flash, redirect, url_for, session

from app.auth.authentication import login_required

bp = Blueprint('catechist', __name__)

@bp.route("/dashboard", methods=["GET"])
@login_required("Catechist")
def catechist_dashboard():
    # Obtener el DTO del catequista para conseguir su ID de documento de rol
    catechist_dto = dal.get_dto_by_user(session.get('username'))
    if not catechist_dto:
        flash('No se pudo encontrar tu información de catequista.', 'danger')
        return redirect(url_for('auth.logout'))

    my_classes = dal.get_classes_by_catechist_id(catechist_dto.id, include=["Level", "Schedule"])
    
    return render_template('catechist/dashboard.html', title='Mis Clases', classes=my_classes)