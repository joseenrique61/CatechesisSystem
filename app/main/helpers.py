from datetime import date
from typing import Optional
from app.main.data.dtos.base_dtos import *
from app import dal

def calculate_age(born_date: Optional[date]) -> Optional[int]:
    if not born_date:
        return None
    today = date.today()
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))

def build_person_dto_from_form(person_form) -> PersonDTO:
    """
    Construye un PersonDTO completo a partir de un subformulario PersonForm.
    CORREGIDO: Construye los DTOs de forma explícita para evitar errores de "múltiples valores".
    """
    # 1. Construir el LocationDTO (esta parte estaba bien)
    location_dto = LocationDTO(**person_form.Address.Location.data)
    
    # 2. Construir el AddressDTO de forma explícita
    # ANTES (INCORRECTO): address_dto = AddressDTO(**person_form.Address.data, Location=location_dto)
    # AHORA (CORRECTO):
    address_dto = AddressDTO(
        MainStreet=person_form.Address.MainStreet.data,
        Number=person_form.Address.Number.data,
        SecondStreet=person_form.Address.SecondStreet.data,
        Location=location_dto  # Pasamos el DTO de Location que ya creamos
    )

    # 3. Construir el PhoneNumberDTO (esta lógica necesita la misma corrección)
    phone_type_id = person_form.PhoneNumber.PhoneNumberType.data
    phone_type_dto = dal.get_phone_number_type_by_id(phone_type_id)
    phone_number_dto = PhoneNumberDTO(
        PhoneNumber=person_form.PhoneNumber.PhoneNumber.data,
        PhoneNumberType=phone_type_dto
    )
    
    # 4. Construir el BirthLocationDTO
    birth_location_dto = LocationDTO(**person_form.BirthLocation.data)

    # 5. Construir el PersonDTO principal de forma explícita
    # ANTES (INCORRECTO): person_dto = PersonDTO(**person_form.data, Address=...)
    # AHORA (CORRECTO):
    person_dto = PersonDTO(
        FirstName=person_form.FirstName.data,
        MiddleName=person_form.MiddleName.data,
        FirstSurname=person_form.FirstSurname.data,
        SecondSurname=person_form.SecondSurname.data,
        BirthDate=person_form.BirthDate.data,
        DNI=person_form.DNI.data,
        Gender=person_form.Gender.data,
        EmailAddress=person_form.EmailAddress.data,
        Address=address_dto, # Pasamos el DTO de Address que creamos
        PhoneNumber=phone_number_dto, # Pasamos el DTO de PhoneNumber que creamos
        BirthLocation=birth_location_dto
    )
    
    return person_dto