from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.forms import ParishForm
from app.main.model_utilities import *
from app import dal
from app.main.data.dtos.base_dtos import *
from app.main.data.dtos.dtos_utilities.dtos_from_form import parish_priest_from_form, parish_from_form

bp = Blueprint('admin', __name__)

# TODO: Login required decorator
@bp.route('/parish_priest/create', methods=['GET', 'POST'])
def register_parish_priest():
    form = ParishPriestForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        parish_priest = ParishPriestDTO.from_db_obj(form, depth=-1, custom_var_path="data")

        try:
            parish_priest, success = dal.register_parish_priest(parish_priest)
            if not success:
                return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        except Exception as e:
            print(f"Error inserting parish priest: {e}")
            flash('Error al registrar el sacerdote.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        flash(f'¡Sacerdote {parish_priest.Person.FirstName} {parish_priest.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)


@bp.route('/parish/create', methods=['GET', 'POST'])
def register_parish():
    form = ParishForm()
    if request.method == 'POST' and form.validate_on_submit():
        parish = parish_from_form(form, request)

        try:
            parish, success = dal.register_parish(parish)
            if not success:
                flash(f'La parroquia {parish.Name} ya existe.', 'danger')
                return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)
        except Exception as e:
            print(f"Error inserting parish: {e}")
            flash('Error al registrar la parroquia.', 'danger')
            return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)

        flash(f'¡Parroquia {parish.Name} registrada exitosamente!', 'success')
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)