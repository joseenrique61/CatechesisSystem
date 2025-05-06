from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.forms import ParishForm
from app.main.models import ParishPriest
from app.main.model_utilities import *
from app import db

bp = Blueprint('admin', __name__)

# TODO: Login required decorator
@bp.route('/parish_priest/create', methods=['GET', 'POST'])
def register_parish_priest():
    form = ParishPriestForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user, success = register_user(form.User)
        if not success:
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        person, success = register_person(form.Person)
        if not success:
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
         
        parishPriest = ParishPriest(
            User=user,
            Person=person,
            IDParish=form.Parish.data,
        )
        try:
            parishPriest, correct, _ = insert_model(parishPriest, [['IDParish'], ['IDUser']])
            if not correct:
                flash(f'El sacerdote {parishPriest.Person.FirstName} {parishPriest.Person.FirstSurname} ya existe.', 'danger')
                return redirect(url_for('admin.register_parish_priest'))
        except Exception as e:
            print(f"Error inserting parish priest: {e}")
            flash('Error al registrar el sacerdote.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()
            flash('Error al registrar el sacerdote.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        flash(f'Sacerdote {parishPriest.Person.FirstName} {parishPriest.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)


@bp.route('/parish/create', methods=['GET', 'POST'])
def register_parish():
    form = ParishForm(request.form)
    if request.method == 'POST' and form.validate():
        # parish = Parish(
        #     Name=form.Name.data,
        #     Address=Address(
        #         MainStreet=form.Address.MainStreet.data,
        #         Number=form.Address.Number.data,
        #         SecondStreet=form.Address.SecondStreet.data,
        #         Location=Location.get_default_location()
        #     ),
        # )
        # db.session.add(parish)
        # db.session.commit()

        # Aquí deberías agregar la lógica para registrar la parroquia en la base de datos
        # Por ejemplo, usando SQLAlchemy:
        # new_parish = Parish(name=form.Name.data, address=form.Address.data)
        # db.session.add(new_parish)
        # db.session.commit()

        # if error is None:
        flash(f'Parroquia {form.Name.data} registrada exitosamente!', 'success')
        #     return redirect(url_for('admin.register_parish'))
        # else:
            # flash(error, 'danger')
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)