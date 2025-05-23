from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.forms import ParishForm
from app import dal
from app.main.data.dtos.base_dtos import *

bp = Blueprint('admin', __name__)

# TODO: Login required decorator
@bp.route('/parish_priest/create', methods=['GET', 'POST'])
def register_parish_priest():
    form = ParishPriestForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        parish_priest = ParishPriestDTO.from_other_obj(form, depth=-1, custom_var_path="data")
        parish_priest.Parish = dal.get_parish_by_id(parish_priest.IDParish)

        try:
            parish_priest, success = dal.register_parish_priest(parish_priest)
            if not success:
                return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        except DuplicateColumnException as e:
            print(f"Error inserting parish priest: {e}")

            match e.table:
                case "User":
                    error_message = f"El usuario {parish_priest.User.Username} ya existe."
                case "Person":
                    match e.columns[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {parish_priest.Person.DNI} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {parish_priest.Person.FirstName} {parish_priest.Person.FirstSurname}."

            flash(error_message, 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        flash(f'¡Sacerdote {parish_priest.Person.FirstName} {parish_priest.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)


@bp.route('/parish/create', methods=['GET', 'POST'])
def register_parish():
    form = ParishForm()
    if request.method == 'POST' and form.validate_on_submit():
        parish = ParishDTO.from_other_obj(form, depth=-1, custom_var_path="data", include=["Classroom"])

        try:
            parish, success = dal.register_parish(parish)
            if not success:
                flash(f'La parroquia {parish.Name} ya existe.', 'danger')
                return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)
        except DuplicateColumnException as e:
            print(f"Error inserting parish priest: {e}")

            error_message = f"Ya existe una parroquia con el nombre {parish.Name}"
            flash(error_message, 'danger')
            return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)

        flash(f'¡Parroquia {parish.Name} registrada exitosamente!', 'success')
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)