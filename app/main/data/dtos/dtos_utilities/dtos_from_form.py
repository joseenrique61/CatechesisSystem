from app.main.forms import *
from app.auth.forms import *
from app.main.data.dtos.create_dtos import *
from app import dal

def user_from_form(form: UserForm, role: str) -> UserCreateDTO:
    """
    Converts a UserForm to a UserCreateDTO.
    """
    return UserCreateDTO(
        Username=form.Username.data,
        Password=form.Password.data,
        Role=dal.get_role(role=role),
    )

def location_from_form(form: LocationForm) -> LocationCreateDTO:
    """
    Converts a LocationForm to a LocationCreateDTO.
    """
    return LocationCreateDTO(
        Country=form.Country.data,
        State=form.State.data,
        Province=form.Province.data
    )

def address_from_form(form: AddressForm) -> AddressCreateDTO:
    """
    Converts an AddressForm to an AddressCreateDTO.
    """
    return AddressCreateDTO(
        MainStreet=form.MainStreet.data,
        Number=form.Number.data,
        SecondStreet=form.SecondStreet.data,
        Location=location_from_form(form.Location)
    )

def phone_number_from_form(form: PersonForm) -> PhoneNumberCreateDTO:
    """
    Converts a PersonForm to a PhoneNumberCreateDTO.
    """
    return PhoneNumberCreateDTO(
        Number=form.PhoneNumber.data,
        Type=form.PhoneNumberType.data,
    )

def person_from_form(form: PersonForm) -> PersonCreateDTO:
    """
    Converts a PersonForm to a PersonCreateDTO.
    """
    return PersonCreateDTO(
        FirstName=form.FirstName.data,
        MiddleName=form.MiddleName.data,
        FirstSurname=form.FirstSurname.data,
        SecondSurname=form.SecondSurname.data,
        BirthDate=form.BirthDate.data,
        BirthLocation=location_from_form(form.BirthLocation),
        DNI=form.DNI.data,
        Gender=form.Gender.data,
        Address=address_from_form(form.Address),
        PhoneNumber=phone_number_from_form(form),
        EmailAddress=form.EmailAddress.data,
    )

def parish_priest_from_form(form: ParishForm) -> ParishPriestCreateDTO:
    """
    Converts a ParishForm to a ParishCreateDTO.
    """
    return ParishPriestCreateDTO(
        Person=person_from_form(form.Person),
        IDParish=form.Parish.data,
        User=user_from_form(form.User, role='ParishPriest')
    )

def parish_from_form(form: ParishForm, request) -> ParishCreateDTO:
    """
    Converts a ParishForm to a ParishCreateDTO.
    """
    return ParishCreateDTO(
        Name=form.Name.data,
        Logo=request.files[form.Logo.name],
        Address=address_from_form(form.Address)
    )