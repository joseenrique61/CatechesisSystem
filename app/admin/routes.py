from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.forms import ParishForm
from app.main.data.dal.sql_server.sql_models import Parish, ParishPriest
from app.main.model_utilities import *
from app import db, dal
from app.main.data.dtos.base_dtos import *
from app.main.data.dtos.create_dtos import *

bp = Blueprint('admin', __name__)

# TODO: Login required decorator
@bp.route('/parish_priest/create', methods=['GET', 'POST'])
def register_parish_priest():
    form = ParishPriestForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        # user, success = register_user(form.User)
        # if not success:
        #     return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        # person, success = register_person(form.Person)
        # if not success:
        #     return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
         
        # parishPriest = ParishPriest(
        #     User=user,
        #     Person=person,
        #     IDParish=form.Parish.data,
        # )
        # try:
        #     parishPriest, correct, _ = insert_model(parishPriest, [['IDParish'], ['IDUser']])
        #     if not correct:
        #         flash(f'El sacerdote {parishPriest.Person.FirstName} {parishPriest.Person.FirstSurname} ya existe.', 'danger')
        #         return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        # except Exception as e:
        #     print(f"Error inserting parish priest: {e}")
        #     flash('Error al registrar el sacerdote.', 'danger')
        #     return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     print(f"Error committing to database: {e}")
        #     db.session.rollback()
        #     flash('Error al registrar el sacerdote.', 'danger')
        #     return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)

        parish_priest = ParishPriestCreateDTO(
            Person=PersonCreateDTO(
                FirstName=form.Person.FirstName.data,
                MiddleName=form.Person.MiddleName.data,
                FirstSurname=form.Person.FirstSurname.data,
                SecondSurname=form.Person.SecondSurname.data,
                BirthDate=form.Person.BirthDate.data,
                BirthLocation=LocationCreateDTO(
                    Country=form.Person.BirthLocation.Country.data,
                    State=form.Person.BirthLocation.State.data,
                    Province=form.Person.BirthLocation.Province.data
                ),
                DNI=form.Person.DNI.data,
                Gender=form.Person.Gender.data,
                Address=AddressCreateDTO(
                    MainStreet=form.Person.Address.MainStreet.data,
                    Number=form.Person.Address.Number.data,
                    SecondStreet=form.Person.Address.SecondStreet.data,
                    Location=LocationCreateDTO(
                        Country=form.Person.Address.Location.Country.data,
                        State=form.Person.Address.Location.State.data,
                        Province=form.Person.Address.Location.Province.data
                    ),
                ),
                PhoneNumber=PhoneNumberCreateDTO(
                    Number=form.Person.PhoneNumber.data,
                    Type=form.Person.PhoneNumberType.data,
                ),
                EmailAddress=form.Person.EmailAddress.data,
            ),
            IDParish=form.Parish.data,
            User=UserCreateDTO(
                Username=form.User.Username.data,
                Password=form.User.Password.data,
                Role=dal.get_role(role='ParishPriest'),
            ),
        )

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
    form = ParishForm(request.form)
    if request.method == 'POST' and form.validate():
        # address, correct = register_address(form.Address)
        # if not correct:
        #     return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)
        
        # parish = Parish(
        #     Name=form.Name.data,
        #     Address=address,
        #     Logo=request.files[form.Logo.name].read(),
        # )
        # try:
        #     parish, correct, _ = insert_model(parish, [['Name']])
        #     if not correct:
        #         flash(f'La parroquia {parish.Name} ya existe.', 'danger')
        #         return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)
        # except Exception as e:
        #     print(f"Error inserting parish: {e}")
        #     flash('Error al registrar la parroquia.', 'danger')
        #     return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)
        
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     print(f"Error committing to database: {e}")
        #     db.session.rollback()
        #     flash('Error al registrar la parroquia.', 'danger')
        #     return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)

        parish = ParishCreateDTO(
            Name=form.Name.data,
            IDAddress=form.Address.data,
            Logo=request.files[form.Logo.name].read() if form.Logo.data else None,
        )

        parish, success = dal.register_parish(parish)
        if not success:
            return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)

        flash(f'¡Parroquia {parish.Name} registrada exitosamente!', 'success')
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)