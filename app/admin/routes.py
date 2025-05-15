from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.forms import ParishForm
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
    form = ParishForm()
    if request.method == 'POST' and form.validate_on_submit():
        parish = ParishCreateDTO(
            Name=form.Name.data,
            Logo=request.files[form.Logo.name],
            Address=AddressCreateDTO(
                MainStreet=form.Address.MainStreet.data,
                Number=form.Address.Number.data,
                SecondStreet=form.Address.SecondStreet.data,
                Location=LocationCreateDTO(
                    Country=form.Address.Location.Country.data,
                    State=form.Address.Location.State.data,
                    Province=form.Address.Location.Province.data
                ),
            ),
        )

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