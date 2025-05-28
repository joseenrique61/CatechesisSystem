from __future__ import annotations

import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.main.data.mapper import Mappable
from werkzeug.datastructures import FileStorage

# --- Base DTOs
class BaseDTO(BaseModel, Mappable):
    class Config:
        from_attributes = True # Permite crear el DTO desde atributos de objeto (SQLAlchemy models)
        arbitrary_types_allowed = True

class TextBookDTO(BaseDTO):
    IDTextBook: Optional[int] = None
    AuthorName: str
    ImplementationDate: datetime.date
    PagesNumber: int
    NameBook: str
    Level: Optional['LevelDTO'] = None

class BaptismalBookVolumeDTO(BaseDTO):
    IDBaptismalBookVolume: Optional[int] = None
    Volume: int
    BaptismalBookPage: List['BaptismalBookPageDTO'] = []

class ClassPeriodDTO(BaseDTO):
    IDClassPeriod: Optional[int] = None
    StartDate: datetime.date
    EndDate: datetime.date
    CurrentPeriod: bool = False
    Class: List['ClassDTO'] = []

    def __str__(self):
        return f"{'Actual' if self.CurrentPeriod else 'Antiguo'} - Fecha de inicio: {self.StartDate}, Fecha de fin: {self.EndDate}"

class DayOfTheWeekDTO(BaseDTO):
    IDDayOfTheWeek: Optional[int] = None
    DayOfTheWeek: str
    Schedule: List['ScheduleDTO'] = []

class LocationDTO(BaseDTO):
    IDLocation: Optional[int] = None
    Province: str
    State: str
    Country: str
    Address: List['AddressDTO'] = []
    Person: List['PersonDTO'] = []

class AllergyDTO(BaseDTO):
    IDAllergy: Optional[int] = None
    Allergy: str
    HealthInformation: List['HealthInformationDTO'] = []

class BloodTypeDTO(BaseDTO):
    IDBloodType: Optional[int] = None
    BloodType: str
    HealthInformation: List['HealthInformationDTO'] = []

class PhoneNumberTypeDTO(BaseDTO):
    IDPhoneNumberType: Optional[int] = None
    PhoneNumberType: str
    PhoneNumber: List['PhoneNumberDTO'] = []

class RoleDTO(BaseDTO):
    Role: str
    User: List['UserDTO'] = []

class UserDTO(BaseDTO):
    IDUser: Optional[int] = None
    Username: str
    Password: Optional[str] = None
    Role: Optional['RoleDTO'] = None
    Administrator: Optional['AdministratorDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    ParishPriest: Optional['ParishPriestDTO'] = None

class LevelDTO(BaseDTO):
    IDLevel: Optional[int] = None
    Name: str
    MinAge: int
    MaxAge: int
    IDPreviousLevel: Optional[int] = None
    TextBook: Optional['TextBookDTO'] = None
    Sacrament: Optional['SacramentDTO'] = None
    Class: List['ClassDTO'] = []
    ParticularClass: List['ParticularClassDTO'] = []

class BaptismalBookPageDTO(BaseDTO):
    IDBaptismalBookPage: Optional[int] = None
    Page: int
    BaptismalBookVolume: Optional['BaptismalBookVolumeDTO'] = None
    BaptismalCertificate: List['BaptismalCertificateDTO'] = []

class ScheduleDTO(BaseDTO):
    IDSchedule: Optional[int] = None
    StartHour: str
    EndHour: str
    IDDayOfTheWeek: Optional[int] = None
    DayOfTheWeek: Optional['DayOfTheWeekDTO'] = None
    IDClassroom: Optional[int] = None
    Classroom: Optional['ClassroomDTO'] = None
    Class: List['ClassDTO'] = []

class AddressDTO(BaseDTO):
    IDAddress: Optional[int] = None
    MainStreet: str
    Number: str
    SecondStreet: str
    Location: 'LocationDTO'
    Parish: List['ParishDTO'] = []
    Person: List['PersonDTO'] = []
    School: List['SchoolDTO'] = []

class PhoneNumberDTO(BaseDTO):
    IDPhoneNumer: Optional[int] = None
    PhoneNumber: str
    IDPhoneNumberType: Optional[int] = None
    PhoneNumberType: Optional['PhoneNumberTypeDTO'] = None
    Person: List['PersonDTO'] = []

class AdministratorDTO(BaseDTO):
    IDUser: Optional[int] = None
    User: Optional['UserDTO'] = None

class ParishDTO(BaseDTO):
    IDParish: Optional[int] = None
    Name: str
    Logo: Optional[str] = None
    LogoImage: Optional[FileStorage] = None
    Address: Optional['AddressDTO'] = None
    Classroom: List['ClassroomDTO'] = []
    ParishPriest: Optional['ParishPriestDTO'] = None

class SacramentDTO(BaseDTO):
    IDSacrament: Optional[int] = None
    Name: str
    Level: Optional['LevelDTO'] = None
    Catechizing: List['CatechizingDTO'] = []

class HealthInformationDTO(BaseDTO):
    ImportantAspects: str
    Catechizing: Optional['CatechizingDTO'] = None # La información de salud es DEL catequizando
    Allergy: List['AllergyDTO'] = []
    IDBloodType: Optional[int] = None
    BloodType: Optional['BloodTypeDTO'] = None
    EmergencyContact: Optional['PersonDTO'] = None # La persona que es el contacto de emergencia

class PersonDTO(BaseDTO):
    IDPerson: Optional[int] = None
    FirstName: str
    MiddleName: str
    FirstSurname: str
    SecondSurname: str
    BirthDate: datetime.date
    DNI: str
    Gender: str
    EmailAddress: str
    Address: Optional['AddressDTO'] = None
    BirthLocation: Optional['LocationDTO'] = None
    PhoneNumber: Optional['PhoneNumberDTO'] = None
    HealthInformation: List['HealthInformationDTO'] = []
    # Roles/Aspectos específicos de la persona
    ParishPriest: Optional['ParishPriestDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    SupportPerson: Optional['SupportPersonDTO'] = None
    Catechizing: Optional['CatechizingDTO'] = None
    Parent: Optional['ParentDTO'] = None
    Godparent: Optional['GodparentDTO'] = None

class SchoolDTO(BaseDTO):
    IDSchool: Optional[int] = None
    SchoolName: str
    Address: Optional['AddressDTO'] = None
    SchoolClassYear: List['SchoolClassYearDTO'] = []

class ClassroomDTO(BaseDTO):
    IDClassroom: Optional[int] = None
    ClassroomName: str
    Parish: Optional['ParishDTO'] = None
    Schedule: List['ScheduleDTO'] = []

class CatechistDTO(BaseDTO):
    IDCatechist: Optional[int] = None # Es el mismo que Person.IDPerson
    User: Optional['UserDTO'] = None
    Person: Optional['PersonDTO'] = None
    Class: List['ClassDTO'] = []

class GodparentDTO(BaseDTO):
    IDGodparent: Optional[int] = None # Es el mismo que Person.IDPerson
    Person: Optional['PersonDTO'] = None
    Catechizing: List['CatechizingDTO'] = []

class ParentDTO(BaseDTO):
    IDParent: Optional[int] = None # Es el mismo que Person.IDPerson
    Ocuppation: str
    Person: Optional['PersonDTO'] = None
    Catechizing: List['CatechizingDTO'] = []

class ParishPriestDTO(BaseDTO):
    IDParishPriest: Optional[int] = None # Es el mismo que Person.IDPerson
    IDParish: Optional[int] = None
    Parish: Optional['ParishDTO'] = None
    User: Optional['UserDTO'] = None
    Person: Optional['PersonDTO'] = None
    ClassAuthorization: List['ClassAuthorizationDTO'] = []
    BaptismalCertificate: List['BaptismalCertificateDTO'] = []

class SupportPersonDTO(BaseDTO):
    IDSupportPerson: Optional[int] = None # Es el mismo que Person.IDPerson
    Person: Optional['PersonDTO'] = None
    Class: List['ClassDTO'] = []

class SchoolClassYearDTO(BaseDTO):
    IDSchoolClassYear: Optional[int] = None
    SchoolYear: str
    School: Optional['SchoolDTO'] = None
    Catechizing: List['CatechizingDTO'] = []

class MainParishDTO(BaseDTO):
    IDMainParish: Optional[int] = None

class ClassDTO(BaseDTO):
    IDClass: Optional[int] = None
    IDClassPeriod: Optional[int] = None
    ClassPeriod: Optional['ClassPeriodDTO'] = None
    IDCatechist: Optional[int] = None
    Catechist: Optional['CatechistDTO'] = None
    IDLevel: Optional[int] = None
    Level: Optional['LevelDTO'] = None
    IDSupportPerson: Optional[int] = None
    SupportPerson: Optional['SupportPersonDTO'] = None
    Schedule: List['ScheduleDTO'] = []
    Catechizing: List['CatechizingDTO'] = []
    LevelCertificate: List['LevelCertificateDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []

class ClassAuthorizationDTO(BaseDTO):
    IDClassAuthorization: Optional[int] = None
    IssueDate: datetime.date
    ParishPriest: Optional['ParishPriestDTO'] = None
    ParticularClass: Optional['ParticularClassDTO'] = None

class CatechizingDTO(BaseDTO):
    IDCatechizing: Optional[int] = None # Es el mismo que Person.IDPerson
    IsLegitimate: bool
    SiblingsNumber: int
    ChildNumber: int
    PayedLevelCourse: bool
    IDClass: Optional[int] = None
    Class: Optional['ClassDTO'] = None
    Person: Optional['PersonDTO'] = None
    BaptismalCertificate: Optional['BaptismalCertificateDTO'] = None
    DataSheet: Optional['DataSheetDTO'] = None
    HealthInformation: Optional['HealthInformationDTO'] = None # La Info de Salud DEL Catequizando
    SchoolClassYear: Optional['SchoolClassYearDTO'] = None
    Sacrament: List['SacramentDTO'] = []
    Godparent: List['GodparentDTO'] = []
    Parent: List['ParentDTO'] = []
    LevelCertificate: List['LevelCertificateDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []
    ParticularClass: List['ParticularClassDTO'] = []

class DataSheetDTO(BaseDTO):
    IDPerson: Optional[int] = None # FK a Catechizing.IDCatechizing
    DataSheetInformation: str
    Catechizing: Optional['CatechizingDTO'] = None

class BaptismalCertificateDTO(BaseDTO):
    IDCatechizing: Optional[int] = None # PK, FK a Catechizing.IDCatechizing
    IssueDate: datetime.date
    Catechizing: Optional['CatechizingDTO'] = None
    BaptismalBookPage: Optional['BaptismalBookPageDTO'] = None
    ParishPriest: Optional['ParishPriestDTO'] = None

class LevelCertificateDTO(BaseDTO):
    IDLevelCertificate: Optional[int] = None
    Catechizing: Optional['CatechizingDTO'] = None
    Class: Optional['ClassDTO'] = None

class AttendedClassDTO(BaseDTO):
    IDCatechizing: Optional[int] = None
    Date: datetime.date
    Catechizing: Optional['CatechizingDTO'] = None
    Class: Optional['ClassDTO'] = None

class ParticularClassDTO(BaseDTO):
    IDParticularClass: Optional[int] = None
    ClassDate: datetime.date
    Catechizing: Optional['CatechizingDTO'] = None
    ClassAuthorization: Optional['ClassAuthorizationDTO'] = None
    Level: Optional['LevelDTO'] = None
    
# --- Rebuild Models to Resolve Forward References ---

dto_models = [
    TextBookDTO, BaptismalBookVolumeDTO, ClassPeriodDTO, DayOfTheWeekDTO,
    LocationDTO, AllergyDTO, BloodTypeDTO, PhoneNumberTypeDTO, RoleDTO, UserDTO,
    LevelDTO, BaptismalBookPageDTO, ScheduleDTO, AddressDTO, PhoneNumberDTO,
    AdministratorDTO, ParishDTO, SacramentDTO, HealthInformationDTO, PersonDTO,
    SchoolDTO, ClassroomDTO, CatechistDTO, GodparentDTO, ParentDTO, ParishPriestDTO,
    SupportPersonDTO, SchoolClassYearDTO, MainParishDTO, ClassDTO, ClassAuthorizationDTO,
    CatechizingDTO, DataSheetDTO, BaptismalCertificateDTO, LevelCertificateDTO,
    AttendedClassDTO, ParticularClassDTO
]

for model in dto_models:
    model.model_rebuild()