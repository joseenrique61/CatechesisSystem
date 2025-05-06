from flask import flash
from app import db
from sqlalchemy.exc import IntegrityError

from app.main.models import Address, Location, Person, PhoneNumber, PhoneNumberType, Role, User

def insert_model(model, attribute_lists: list[list[str]]) -> tuple[object, bool, int]:
    """
    Insert a model into the database.
    :param model: The model to insert.
    :return: True if the model was inserted successfully, False otherwise. The model itself, whether it is the passed to the function or the one from the db, is returned.
    """
    try:
        db.session.add(model)
        db.session.flush()
        return model, True, None
    except IntegrityError as e:
        db.session.rollback()
        results = []
        for attribute_list in attribute_lists:
            filter_conditions = {}

            for column_name in attribute_list:
                if hasattr(model, column_name):
                    value = getattr(model, column_name)
                    filter_conditions[column_name] = value
                else:
                    print(f"El modelo no tiene el atributo {column_name}.")

            if not filter_conditions:
                print("No se generaron condiciones de filtro válidas a partir de los atributos del modelo.")
                return None, False

            results.append(db.session.query(type(model)).filter_by(**filter_conditions).one_or_none())

        result = next((result for result in results if result is not None), None)
        return result, False, results.index(result)
    except Exception as e:
        db.session.rollback()
        raise e

def register_user(userForm) -> tuple[User, bool]:
    success = True
    try:
        user = User(
            Username=userForm.Username.data,
            Role=Role.query.filter_by(Role='ParishPriest').first(),
        )
        user.set_password(userForm.Password.data)

        user, correct, _ = insert_model(user, [['Username']])
        if not correct:
            flash(f'El usuario {user.Username} ya existe.', 'danger')
            success = False
    except Exception as e:
        print(f"Error inserting user: {e}")
        flash('Error al registrar el usuario.', 'danger')
        success = False
    return user, success

def register_location(locationForm) -> tuple[Location, bool]:
    success = True
    try:
        location = Location(
            Country=locationForm.Country.data,
            State=locationForm.State.data,
            Province=locationForm.Province.data,
        )

        location, _, _ = insert_model(location, [['Country', 'State', 'Province']])
    except Exception as e:
        print(f"Error inserting location: {e}")
        flash('Error al registrar la ubicación.', 'danger')
        success = False
    return location, success

def register_address(addressForm) -> tuple[Address, bool]:
    success = True
    try:
        location, success = register_location(addressForm.Location)
        address = Address(
            MainStreet=addressForm.MainStreet.data,
            Number=addressForm.Number.data,
            SecondStreet=addressForm.SecondStreet.data,
            Location=location,
        )

        address, _, _ = insert_model(address, [['MainStreet', 'Number', 'SecondStreet']])
    except Exception as e:
        print(f"Error inserting address: {e}")
        flash('Error al registrar la dirección.', 'danger')
        success = False
    return address, success

def register_phone(personForm) -> tuple[PhoneNumber, bool]:
    success = True
    try:
        phoneNumber = PhoneNumber(
            PhoneNumber=personForm.PhoneNumber.data,
            PhoneNumberType=PhoneNumberType.query.get(personForm.PhoneNumberType.data),
        )

        phoneNumber, _, _ = insert_model(phoneNumber, [['PhoneNumber']])
    except Exception as e:
        print(f"Error inserting phone: {e}")
        flash('Error al registrar el teléfono.', 'danger')
        success = False
    return phoneNumber, success

def register_person(personForm) -> tuple[object, bool]:
    success = True
    try:
        birthLocation, success = register_location(personForm.BirthLocation)
        phoneNumber, success1 = register_phone(personForm)
        address, success2 = register_address(personForm.Address)

        person = Person(
            FirstName=personForm.FirstName.data,
            MiddleName=personForm.MiddleName.data,
            FirstSurname=personForm.FirstSurname.data,
            SecondSurname=personForm.SecondSurname.data,
            DNI=personForm.DNI.data,
            BirthDate=personForm.BirthDate.data,
            BirthLocation=birthLocation,
            Gender=personForm.Gender.data,
            PhoneNumber=phoneNumber,
            Address=address,
            EmailAddress=personForm.Email.data,
        )
        person, correct, option = insert_model(person, [['FirstName', 'MiddleName', 'FirstSurname', 'SecondSurname'], ['DNI']])
        if not correct:
            if option == 0:
                flash(f'La persona {person.FirstName} {person.MiddleName} {person.FirstSurname} {person.SecondSurname} ya existe.', 'danger')
            elif option == 1:
                flash(f'La persona con DNI {person.DNI} ya existe.', 'danger')
            success = False
    except Exception as e:
        print(f"Error inserting person: {e}")
        flash('Error al registrar la persona.', 'danger')
        success = False
    return person, success and success1 and success2