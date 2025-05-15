import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class BaseDTO(BaseModel):
    class Config:
        from_attributes = True # Permite crear el DTO desde atributos de objeto (SQLAlchemy models)

class TextBookDTO(BaseDTO):
    IDTextBook: int
    AuthorName: str
    ImplementationDate: datetime.date
    PagesNumber: int
    NameBook: str
    Level: List['LevelDTO'] = [] # Forward reference

class BaptismalBookVolumeDTO(BaseDTO):
    IDBaptismalBookVolume: int
    Volume: int
    BaptismalBookPage: List['BaptismalBookPageDTO'] = []

class ClassPeriodDTO(BaseDTO):
    IDClassPeriod: int
    StartDate: datetime.date
    EndDate: datetime.date
    CurrentPeriod: bool
    Class_: List['ClassDTO'] = Field([], alias="Class") # Alias para evitar conflicto con 'Class' keyword

class DayOfTheWeekDTO(BaseDTO):
    IDDayOfTheWeek: int
    DayOfTheWeek: str
    Schedule: List['ScheduleDTO'] = []

class LocationDTO(BaseDTO):
    IDLocation: int
    Province: str
    State: str
    Country: str
    Address: List['AddressDTO'] = []
    Person: List['PersonDTO'] = []

class AllergyDTO(BaseDTO):
    IDAllergy: int
    Allergy: str
    HealthInformation: List['HealthInformationDTO'] = []

class BloodTypeDTO(BaseDTO):
    IDBloodType: int
    BloodType: str
    HealthInformation: List['HealthInformationDTO'] = []

class PhoneNumberTypeDTO(BaseDTO):
    IDPhoneNumberType: int
    PhoneNumberType: str
    PhoneNumber: List['PhoneNumberDTO'] = []

class RoleDTO(BaseDTO):
    Role: str
    User: List['UserDTO'] = []

class UserDTO(BaseDTO):
    IDUser: int
    Username: str
    Password: str
    Role: 'RoleDTO'
    Administrator: Optional['AdministratorDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    ParishPriest: Optional['ParishPriestDTO'] = None

class UserReadDTO(BaseDTO):
    IDUser: int
    Username: str
    Role: 'RoleDTO'
    Administrator: Optional['AdministratorDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    ParishPriest: Optional['ParishPriestDTO'] = None

class LevelDTO(BaseDTO):
    IDLevel: int
    Name: str
    MinAge: int
    MaxAge: int
    PreviousLevel: Optional['LevelDTO'] = Field(None, alias="Level") # Self-referential for parent
    SubsequentLevels: List['LevelDTO'] = Field([], alias="Level_reverse") # Self-referential for children
    TextBook: 'TextBookDTO'
    Sacrament: List['SacramentDTO'] = []
    Class_: List['ClassDTO'] = Field([], alias="Class")
    ParticularClass: List['ParticularClassDTO'] = []

class BaptismalBookPageDTO(BaseDTO):
    IDBaptismalBookPage: int
    Page: int
    BaptismalBookVolume: 'BaptismalBookVolumeDTO'
    BaptismalCertificate: List['BaptismalCertificateDTO'] = []

class ScheduleDTO(BaseDTO):
    IDSchedule: int
    StartHour: str
    EndHour: str
    DayOfTheWeek: 'DayOfTheWeekDTO'
    Class_: List['ClassDTO'] = Field([], alias="Class")

class AddressDTO(BaseDTO):
    IDAddress: int
    MainStreet: str
    Number: str
    SecondStreet: str
    Location: 'LocationDTO'
    Parish: List['ParishDTO'] = []
    Person: List['PersonDTO'] = []
    School: List['SchoolDTO'] = []

class PhoneNumberDTO(BaseDTO):
    IDPhoneNumer: int
    PhoneNumber: str
    PhoneNumberType: 'PhoneNumberTypeDTO'
    Person: List['PersonDTO'] = []

class AdministratorDTO(BaseDTO):
    IDUser: int
    User: 'UserDTO'

class ParishDTO(BaseDTO):
    IDParish: int
    Name: str
    Logo: str
    Address: 'AddressDTO'
    Classroom: List['ClassroomDTO'] = []
    ParishPriest: Optional['ParishPriestDTO'] = None

class SacramentDTO(BaseDTO):
    IDSacrament: int
    Name: str
    Level: 'LevelDTO'
    Catechizing: List['CatechizingDTO'] = []

class HealthInformationDTO(BaseDTO):
    IDCatechizing: int
    ImportantAspects: str
    Catechizing: 'CatechizingDTO' # La información de salud es DEL catequizando
    Allergy: List['AllergyDTO'] = []
    BloodType: 'BloodTypeDTO'
    EmergencyContact: 'PersonDTO' # La persona que es el contacto de emergencia

class PersonDTO(BaseDTO):
    IDPerson: int
    FirstName: str
    MiddleName: str
    FirstSurname: str
    SecondSurname: str
    BirthDate: datetime.date
    DNI: str
    Gender: str
    EmailAddress: str
    Address: 'AddressDTO'
    BirthLocation: 'LocationDTO'
    PhoneNumber: 'PhoneNumberDTO'
    HealthInformationEmergencyContactFor: List['HealthInformationDTO'] = Field([], alias="HealthInformation") # Casos donde esta persona es contacto de emergencia
    # Roles/Aspectos específicos de la persona
    ParishPriest: Optional['ParishPriestDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    SupportPerson: Optional['SupportPersonDTO'] = None
    Catechizing: Optional['CatechizingDTO'] = None
    Parent: Optional['ParentDTO'] = None
    Godparent: Optional['GodparentDTO'] = None

class SchoolDTO(BaseDTO):
    IDSchool: int
    SchoolName: str
    Address: 'AddressDTO'
    SchoolClassYear: List['SchoolClassYearDTO'] = []

class ClassroomDTO(BaseDTO):
    IDClassroom: int
    ClassroomName: str
    Parish: 'ParishDTO'
    Class_: List['ClassDTO'] = Field([], alias="Class")

class CatechistDTO(BaseDTO):
    IDCatechist: int # Es el mismo que Person.IDPerson
    User: 'UserDTO'
    Person: 'PersonDTO'
    Class_: List['ClassDTO'] = Field([], alias="Class")

class GodparentDTO(BaseDTO):
    IDGodparent: int # Es el mismo que Person.IDPerson
    Person: 'PersonDTO'
    Catechizing: List['CatechizingDTO'] = []

class ParentDTO(BaseDTO):
    IDParent: int # Es el mismo que Person.IDPerson
    Ocuppation: str
    Person: 'PersonDTO'
    Catechizing: List['CatechizingDTO'] = []

class ParishPriestDTO(BaseDTO):
    IDParishPriest: int # Es el mismo que Person.IDPerson
    Parish: 'ParishDTO'
    User: 'UserReadDTO'
    Person: 'PersonDTO'
    ClassAuthorization: List['ClassAuthorizationDTO'] = []
    BaptismalCertificate: List['BaptismalCertificateDTO'] = []

class SupportPersonDTO(BaseDTO):
    IDSupportPerson: int # Es el mismo que Person.IDPerson
    Person: 'PersonDTO'
    Class_: List['ClassDTO'] = Field([], alias="Class")

class SchoolClassYearDTO(BaseDTO):
    IDSchoolClassYear: int
    SchoolYear: str
    School: 'SchoolDTO'
    Catechizing: List['CatechizingDTO'] = []

class MainParishDTO(BaseDTO):
    IDMainParish: int

class ClassDTO(BaseDTO):
    IDClass: int
    Classroom: List['ClassroomDTO'] = []
    ClassPeriod: 'ClassPeriodDTO'
    Catechist: 'CatechistDTO'
    Level: 'LevelDTO'
    SupportPerson: 'SupportPersonDTO'
    Schedule: List['ScheduleDTO'] = []
    Catechizing: List['CatechizingDTO'] = []
    LevelCertificate: List['LevelCertificateDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []

class ClassAuthorizationDTO(BaseDTO):
    IDClassAuthorization: int
    IssueDate: datetime.date
    ParishPriest: 'ParishPriestDTO'
    ParticularClass: 'ParticularClassDTO'

class CatechizingDTO(BaseDTO):
    IDCatechizing: int # Es el mismo que Person.IDPerson
    IsLegitimate: bool
    SiblingsNumber: int
    ChildNumber: int
    PayedLevelCourse: bool
    Class_: 'ClassDTO' = Field(alias="Class")
    Person: 'PersonDTO'
    BaptismalCertificate: 'BaptismalCertificateDTO'
    DataSheet: 'DataSheetDTO'
    HealthInformation: 'HealthInformationDTO' # La Info de Salud DEL Catequizando
    SchoolClassYear: 'SchoolClassYearDTO'
    Sacrament: List['SacramentDTO'] = []
    Godparent: List['GodparentDTO'] = []
    Parent: List['ParentDTO'] = []
    LevelCertificate: List['LevelCertificateDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []
    ParticularClass: List['ParticularClassDTO'] = []

class DataSheetDTO(BaseDTO):
    IDPerson: int # FK a Catechizing.IDCatechizing
    DataSheetInformation: str
    Catechizing: 'CatechizingDTO'

class BaptismalCertificateDTO(BaseDTO):
    IDCatechizing: int # PK, FK a Catechizing.IDCatechizing
    IssueDate: datetime.date
    Catechizing: 'CatechizingDTO'
    BaptismalBookPage: 'BaptismalBookPageDTO'
    ParishPriest: 'ParishPriestDTO'

class LevelCertificateDTO(BaseDTO):
    IDLevelCertificate: int
    Catechizing: 'CatechizingDTO'
    Class_: 'ClassDTO' = Field(alias="Class")

class AttendedClassDTO(BaseDTO):
    IDCatechizing: int
    Date_: datetime.date = Field(alias="Date") # El modelo usa 'Date' como nombre de columna
    Catechizing: 'CatechizingDTO'
    Class_: 'ClassDTO' = Field(alias="Class")

class ParticularClassDTO(BaseDTO):
    IDParticularClass: int
    ClassDate: datetime.date
    Catechizing: 'CatechizingDTO'
    ClassAuthorization: 'ClassAuthorizationDTO'
    Level: 'LevelDTO'

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