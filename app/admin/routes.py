from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.forms import ParishPriestForm
from app.main.forms import ParishForm
from app.main.models import Parish, Address, Location, User, ParishPriest, PhoneNumberType, Person, PhoneNumber, Role
from app.main.model_utilities import insert_model
from app import db

bp = Blueprint('admin', __name__)

# TODO: Login required decorator
@bp.route('/parish_priest/create', methods=['GET', 'POST'])
def register_parish_priest():
    form = ParishPriestForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = User(
            Username=form.User.Username.data,
            Role=Role.query.filter_by(Role='ParishPriest').first(),
        )
        user.set_password(form.User.Password.data)
        try:
            user, correct = insert_model(user)
            if not correct:
                flash(f'El usuario {user.Username} ya existe.', 'danger')
                return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        except Exception as e:
            print(f"Error inserting user: {e}")
            flash('Error al registrar el usuario.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        addressLocation = Location(
            Country=form.Person.Address.Location.Country.data,
            State=form.Person.Address.Location.State.data,
            Province=form.Person.Address.Location.Province.data,
        )
        try:
            addressLocation, correct = insert_model(addressLocation)
        except Exception as e:
            print(f"Error inserting location: {e}")
            flash('Error al registrar la ubicación.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        address = Address(
            MainStreet=form.Person.Address.MainStreet.data,
            Number=form.Person.Address.Number.data,
            SecondStreet=form.Person.Address.SecondStreet.data,
            Location=addressLocation
        )
        try:
            address, correct = insert_model(address)
        except Exception as e:
            print(f"Error inserting address: {e}")
            flash('Error al registrar la dirección.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)

        birthLocation = Location(
            Country=form.Person.BirthLocation.Country.data,
            State=form.Person.BirthLocation.State.data,
            Province=form.Person.BirthLocation.Province.data,
        )
        try:
            birthLocation, correct = insert_model(birthLocation)
        except Exception as e:
            print(f"Error inserting birth location: {e}")
            flash('Error al registrar la ubicación de nacimiento.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        phoneNumber = PhoneNumber(
            PhoneNumber=form.Person.PhoneNumber.data,
            PhoneNumberType=PhoneNumberType.query.get(form.Person.PhoneNumberType.data),
        )

        person = Person(
            FirstName=form.Person.FirstName.data,
            MiddleName=form.Person.MiddleName.data,
            FirstSurname=form.Person.FirstSurname.data,
            SecondSurname=form.Person.SecondSurname.data,
            DNI=form.Person.DNI.data,
            BirthDate=form.Person.BirthDate.data,
            BirthLocation=birthLocation,
            Gender=form.Person.Gender.data,
            PhoneNumber=phoneNumber,
            Address=address,
            EmailAddress=form.Person.Email.data,
        )
        try:
            person, correct = insert_model(person)
            if not correct:
                flash(f'La persona {person.FirstName} {person.SecondName} {person.FirstSurname} {person.SecondSurname} ya existe.', 'danger')
                db.session.rollback()
                return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        except Exception as e:
            print(f"Error inserting person: {e}")
            flash('Error al registrar la persona.', 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        parishPriest = ParishPriest(
            User=user,
            Person=person,
            IDParish=form.Parish.data,
        )
        try:
            parishPriest, correct = insert_model(parishPriest)
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