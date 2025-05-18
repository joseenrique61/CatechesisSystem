from app.main.forms import *
from app.auth.forms import *
from app.parish_priest.forms import *
from app.main.data.dtos.base_dtos import *
from app import dal

def user_from_form(form: UserForm, role: str) -> UserDTO:
    """
    Converts a UserForm to a UserDTO.
    """
    return UserDTO(
        Username=form.Username.data,
        Password=form.Password.data,
        Role=dal.get_role(role=role),
    )

def location_from_form(form: LocationForm) -> LocationDTO:
    """
    Converts a LocationForm to a LocationDTO.
    """
    return LocationDTO(
        Country=form.Country.data,
        State=form.State.data,
        Province=form.Province.data
    )

def address_from_form(form: AddressForm) -> AddressDTO:
    """
    Converts an AddressForm to an AddressDTO.
    """
    return AddressDTO(
        MainStreet=form.MainStreet.data,
        Number=form.Number.data,
        SecondStreet=form.SecondStreet.data,
        Location=location_from_form(form.Location)
    )

def phone_number_from_form(form: PersonForm) -> PhoneNumberDTO:
    """
    Converts a PersonForm to a PhoneNumberDTO.
    """
    return PhoneNumberDTO(
        PhoneNumber=form.PhoneNumber.data,
        PhoneNumberType=dal.get_phone_number_type_by_id(form.IDPhoneNumberType.data)
    )

def person_from_form(form: PersonForm) -> PersonDTO:
    """
    Converts a PersonForm to a PersonDTO.
    """
    return PersonDTO(
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

def parish_priest_from_form(form: ParishForm) -> ParishPriestDTO:
    """
    Converts a ParishForm to a ParishDTO.
    """
    return ParishPriestDTO(
        Person=person_from_form(form.Person),
        IDParish=form.IDParish.data,
        User=user_from_form(form.User, role='ParishPriest')
    )

def parish_from_form(form: ParishForm, request) -> ParishDTO:
    """
    Converts a ParishForm to a ParishDTO.
    """
    return ParishCreateDTO(
        Name=form.Name.data,
        LogoImage=request.files[form.Logo.name],
        Address=address_from_form(form.Address)
    )

def catechizing_from_form(form: CatechizingForm) -> CatechizingDTO:
    """
    Converts a CatechistForm to a CatechistDTO.
    """
    return CatechizingDTO(
        Person=person_from_form(form.Person),
        IsLegitimate=form.IsLegitimate.data,
        SiblingsNumber=form.SiblingsNumber.data,
        ChildNumber=form.ChildNumber.data,
        SchoolClassYear=SchoolClassYearDTO(
            SchoolYear=form.SchoolClassYear.SchoolYear.data,
            IDSchool=form.SchoolClassYear.IDSchool,
        ),
        IDClass=form.IDClass.data,
        PayedLevelCourse=form.PayedLevelCourse.data,
        Parents=[ParentDTO(
            Person=person_from_form(parent),
            Occupation=parent.Occupation.data,
        ) for parent in form.Parents],
        Godparents=[GodparentDTO(
            Person=person_from_form(godparent),
        ) for godparent in form.Godparents],
        HealthInformation=HealthInformationDTO(
            ImportantAspects=form.ImportantAspects.data,
            Allergy=[AllergyDTO(
                Allergy=allergy.data
            ) for allergy in form.Allergies],
            BloodType=dal.get_blood_type_by_id(form.IDBloodType.data),
            EmergencyContact=person_from_form(form.EmergencyContact)
        ),
        DataSheet=DataSheetDTO(
            DataSheetInformation=form.DataSheetInformation.data
        ),
        ParticularClass=ParticularClassDTO(
                ClassDate=form.ParticularClass.ClassDate.data,
                ClassAuthorization=ClassAuthorizationDTO(
                    IssueDate=form.ParticularClass.ClassAuthorization.IssueDate.data,
                    ParishPriest=dal.get_parish_priest_by_id(0)
                ),
                Level=dal.get_level_by_name(dal.get_class_by_id(form.ParticularClass.IDClass.data).Level.Name)
            ) if form.HasParticularClass.data else None,
    )