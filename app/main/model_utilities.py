from flask import flash
from app import db
from sqlalchemy.exc import IntegrityError

from app.main.data.dal.sql_server.sql_models import Address, Location, Person, PhoneNumber, PhoneNumberType, Role, User

def insert_model(model, attribute_lists: list[list[str]]) -> tuple[object, bool, int]:
    """
    Insert a model into the database.

    :param model: The model to insert.
    :param attribute_lists: A list of lists of attributes to check for duplicates.
    :return: First, the model itself, whether it is the passed to the function or the one from the db, is returned. Second, True if the model was inserted successfully, False otherwise. Last, the index of the model in the attribute_lists is returned.
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

def register_user(user__form) -> tuple[User, bool]:
    success = True
    try:
        user = User(
            Username=user__form.Username.data,
            Role=Role.query.filter_by(Role='ParishPriest').first(),
        )
        user.set_password(user__form.Password.data)

        user, correct, _ = insert_model(user, [['Username']])
        if not correct:
            flash(f'El usuario {user.Username} ya existe.', 'danger')
            success = False
    except Exception as e:
        print(f"Error inserting user: {e}")
        flash('Error al registrar el usuario.', 'danger')
        success = False
    return user, success

def register_location(location_form) -> tuple[Location, bool]:
    success = True
    try:
        location = Location(
            Country=location_form.Country.data,
            State=location_form.State.data,
            Province=location_form.Province.data,
        )

        location, _, _ = insert_model(location, [['Country', 'State', 'Province']])
    except Exception as e:
        print(f"Error inserting location: {e}")
        flash('Error al registrar la ubicación.', 'danger')
        success = False
    return location, success

def register_address(address_form) -> tuple[Address, bool]:
    success = True
    try:
        location, success = register_location(address_form.Location)
        address = Address(
            MainStreet=address_form.MainStreet.data,
            Number=address_form.Number.data,
            SecondStreet=address_form.SecondStreet.data,
            Location=location,
        )

        address, _, _ = insert_model(address, [['MainStreet', 'Number', 'SecondStreet']])
    except Exception as e:
        print(f"Error inserting address: {e}")
        flash('Error al registrar la dirección.', 'danger')
        success = False
    return address, success

def register_phone(person_form) -> tuple[PhoneNumber, bool]:
    success = True
    try:
        phoneNumber = PhoneNumber(
            PhoneNumber=person_form.PhoneNumber.data,
            PhoneNumberType=PhoneNumberType.query.get(person_form.PhoneNumberType.data),
        )

        phoneNumber, _, _ = insert_model(phoneNumber, [['PhoneNumber']])
    except Exception as e:
        print(f"Error inserting phone: {e}")
        flash('Error al registrar el teléfono.', 'danger')
        success = False
    return phoneNumber, success

def register_person(person_form) -> tuple[object, bool]:
    success = True
    try:
        birthLocation, success = register_location(person_form.BirthLocation)
        phoneNumber, success1 = register_phone(person_form)
        address, success2 = register_address(person_form.Address)

        person = Person(
            FirstName=person_form.FirstName.data,
            MiddleName=person_form.MiddleName.data,
            FirstSurname=person_form.FirstSurname.data,
            SecondSurname=person_form.SecondSurname.data,
            DNI=person_form.DNI.data,
            BirthDate=person_form.BirthDate.data,
            BirthLocation=birthLocation,
            Gender=person_form.Gender.data,
            PhoneNumber=phoneNumber,
            Address=address,
            EmailAddress=person_form.Email.data,
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