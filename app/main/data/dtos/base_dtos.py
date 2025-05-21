from __future__ import annotations

import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
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
    Class_: List['ClassDTO'] = Field([], alias="Class") # Alias para evitar conflicto con Optional['Class'] = None keyword

class ClassPeriodReadDTO(BaseDTO):
    IDClassPeriod: Optional[int] = None
    StartDate: datetime.date
    EndDate: datetime.date
    CurrentPeriod: bool 

class DayOfTheWeekDTO(BaseDTO):
    IDDayOfTheWeek: Optional[int] = None
    DayOfTheWeek: str
    Schedule: List['ScheduleDTO'] = []

# class DayOfTheWeekReadDTO(BaseDTO):
#     IDDayOfTheWeek: Optional[int] = None
#     DayOfTheWeek: str

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

# class UserReadDTO(BaseDTO):
#     IDUser: Optional[int] = None
#     Username: str
#     Role: Optional['RoleDTO'] = None
#     Administrator: Optional['AdministratorDTO'] = None
#     Catechist: Optional['CatechistDTO'] = None
#     ParishPriest: Optional['ParishPriestDTO'] = None

class LevelDTO(BaseDTO):
    IDLevel: Optional[int] = None
    Name: str
    MinAge: int
    MaxAge: int
    IDPreviousLevel: Optional[int] = None
    TextBook: Optional['TextBookDTO'] = None
    Sacrament: Optional['SacramentDTO'] = None
    Class_: List['ClassDTO'] = Field([], alias="Class")
    ParticularClass: List['ParticularClassDTO'] = []

# class LevelReadDTO(BaseDTO):
#     IDLevel: Optional[int] = None
#     Name: str
#     MinAge: int
#     MaxAge: int
#     IDPreviousLevel: Optional[int] = None
#     TextBook: Optional['TextBookDTO'] = None
#     Sacrament: Optional['SacramentReadDTO'] = None

class BaptismalBookPageDTO(BaseDTO):
    IDBaptismalBookPage: Optional[int] = None
    Page: int
    BaptismalBookVolume: Optional['BaptismalBookVolumeDTO'] = None
    BaptismalCertificate: List['BaptismalCertificateDTO'] = []

class ScheduleDTO(BaseDTO):
    IDSchedule: Optional[int] = None
    StartHour: str
    EndHour: str
    DayOfTheWeek: Optional['DayOfTheWeekDTO'] = None
    Class_: List['ClassDTO'] = Field([], alias="Class")

# class ScheduleReadDTO(BaseDTO):
#     IDSchedule: Optional[int] = None
#     StartHour: str
#     EndHour: str
#     DayOfTheWeek: Optional['DayOfTheWeekReadDTO'] = None

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

# class SacramentReadDTO(BaseDTO):
#     IDSacrament: Optional[int] = None
#     Name: str

class HealthInformationDTO(BaseDTO):
    Catechizing: Optional['CatechizingDTO'] = None
    ImportantAspects: str
    Catechizing: Optional['CatechizingDTO'] = None # La información de salud es DEL catequizando
    Allergy: List['AllergyDTO'] = []
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
    HealthInformationEmergencyContactFor: List['HealthInformationDTO'] = Field([], alias="HealthInformation") # Casos donde esta persona es contacto de emergencia
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
    Class_: List['ClassDTO'] = Field([], alias="Class")

# class ClassroomReadDTO(BaseDTO):
#     IDClassroom: Optional[int] = None
#     ClassroomName: str
#     Parish: Optional['ParishDTO'] = None

class CatechistDTO(BaseDTO):
    IDCatechist: Optional[int] = None # Es el mismo que Person.IDPerson
    User: Optional['UserDTO'] = None
    Person: Optional['PersonDTO'] = None
    Class_: List['ClassDTO'] = Field([], alias="Class")

# class CatechistReadDTO(BaseDTO):
#     IDCatechist: Optional[int] = None
#     Person: Optional['PersonDTO'] = None

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
    Class_: List['ClassDTO'] = Field([], alias="Class")

# class SupportPersonReadDTO(BaseDTO):
#     IDSupportPerson: Optional[int] = None # Es el mismo que Person.IDPerson
#     Person: Optional['PersonDTO'] = None

class SchoolClassYearDTO(BaseDTO):
    IDSchoolClassYear: Optional[int] = None
    SchoolYear: str
    School: Optional['SchoolDTO'] = None
    Catechizing: List['CatechizingDTO'] = []

class MainParishDTO(BaseDTO):
    IDMainParish: Optional[int] = None

class ClassDTO(BaseDTO):
    IDClass: Optional[int] = None
    Classroom: List['ClassroomDTO'] = []
    ClassPeriod: Optional['ClassPeriodDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    Level: Optional['LevelDTO'] = None
    SupportPerson: Optional['SupportPersonDTO'] = None
    Schedule: List['ScheduleDTO'] = []
    Catechizing: List['CatechizingDTO'] = []
    LevelCertificate: List['LevelCertificateDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []

# class ClassReadDTO(BaseDTO):
#     IDClass: Optional[int] = None
#     Classroom: List['ClassroomReadDTO'] = []
#     ClassPeriod: Optional['ClassPeriodReadDTO'] = None
#     Catechist: Optional['CatechistReadDTO'] = None
#     Level: Optional['LevelReadDTO'] = None
#     SupportPerson: Optional['SupportPersonReadDTO'] = None
#     Schedule: List['ScheduleReadDTO'] = []

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
    Class_: Optional['ClassDTO'] = Field(None, alias="Class")
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
    Class_: Optional['ClassDTO'] = Field(None, alias="Class")

class AttendedClassDTO(BaseDTO):
    IDCatechizing: Optional[int] = None
    Date_: datetime.date = Field(alias="Date")
    Catechizing: Optional['CatechizingDTO'] = None
    Class_: Optional['ClassDTO'] = Field(None, alias="Class")

class ParticularClassDTO(BaseDTO):
    IDParticularClass: Optional[int] = None
    ClassDate: datetime.date
    Catechizing: Optional['CatechizingDTO'] = None
    ClassAuthorization: Optional['ClassAuthorizationDTO'] = None
    Level: Optional['LevelDTO'] = None
    
# --- Create DTOs
# class UserCreateDTO(BaseDTO):
#     Username: str
#     Password: str
#     Role: RoleDTO

# class PhoneNumberCreateDTO(BaseDTO):
#     Number: str
#     Type: int

# class PersonCreateDTO(BaseDTO):
#     FirstName: str
#     MiddleName: str
#     FirstSurname: str
#     SecondSurname: str
#     BirthDate: datetime.date
#     BirthLocation: 'LocationCreateDTO'
#     DNI: str
#     Gender: str
#     Address: 'AddressCreateDTO'
#     PhoneNumber: PhoneNumberCreateDTO
#     EmailAddress: str

# class ClassroomCreateDTO(BaseDTO):
#     ClassroomName: str

# class ParishCreateDTO(ParishDTO):
#     LogoImage: Optional[FileStorage] = None

# class ParishUpdateDTO(BaseDTO):
#     Name: Optional[str] = None
#     IDAddress: Optional[int] = None
#     Logo: Optional[bytes] = None # Permite enviar None para borrar el logo si se implementa así

# class ParishPriestCreateDTO(BaseDTO):
#     Person: PersonCreateDTO # Datos para crear la persona asociada
#     User: UserCreateDTO     # Datos para crear el usuario asociado
#     IDParish: Optional[int] = None           # ID de la parroquia a la que se asigna

# class ParishPriestUpdateDTO(BaseDTO):
#     # Define qué se puede actualizar. Por ejemplo, reasignar parroquia.
#     # La actualización de Person o User podría ser a través de sus propios métodos.
#     IDParish: Optional[int] = None
#     # Podrías añadir campos para actualizar datos de User o Person si la lógica lo permite aquí
#     # User_Username: Optional[str] = None
#     # Person_Email: Optional[str] = None


# class CatechistCreateDTO(BaseDTO):
#     Person: PersonCreateDTO
#     User: UserCreateDTO

# class CatechistUpdateDTO(BaseDTO):
#     # Similar a ParishPriestUpdateDTO, define qué se puede modificar.
#     # Por ejemplo, si un catequista cambia de email (actualizando Person)
#     # Person_Email: Optional[str] = None
#     pass

# class SchoolClassYearCreateDTO(BaseDTO):
#     SchoolYear: str
#     IDSchool: Optional[int] = None

# class AllergyCreateDTO(BaseDTO):
#     Allergy: str

# class HealthInformationCreateDTO(BaseDTO):
#     ImportantAspects: str
#     Allergy: List['AllergyCreateDTO'] = []
#     BloodType: 'BloodTypeDTO'
#     EmergencyContact: 'PersonDTO' # La persona que es el contacto de emergencia

# class DataSheetCreateDTO(BaseDTO):
#     DataSheetInformation: str

# class ClassAuthorizationCreateDTO(BaseDTO):
#     IssueDate: datetime.date
#     ParishPriest: 'ParishPriestDTO'

# class ParticularClassCreateDTO(BaseDTO):
#     ClassDate: datetime.date
#     ClassAuthorization: 'ClassAuthorizationCreateDTO'
#     Level: 'LevelDTO'

# class ParentCreateDTO(BaseDTO):
#     Person: PersonCreateDTO
#     Occupation: str

# class GodparentCreateDTO(BaseDTO):
#     Person: PersonCreateDTO

# class CatechizingCreateDTO(BaseDTO):
#     Person: PersonCreateDTO
#     IsLegitimate: bool
#     SiblingsNumber: int
#     ChildNumber: int
#     SchoolClassYear: 'SchoolClassYearCreateDTO'
#     IDClass: Optional[int] = None           # ID de la clase existente
#     PayedLevelCourse: bool
#     Parents: List['ParentCreateDTO'] = [] # Para crear o enlazar padres
#     Godparents: List['GodparentCreateDTO'] = [] # Para crear o enlazar padrinos
#     HealthInformation: 'HealthInformationCreateDTO'
#     DataSheet: 'DataSheetCreateDTO'
#     ParticularClass: Optional['ParticularClassCreateDTO'] = None

# class CatechizingUpdateDTO(BaseDTO):
#     IsLegitimate: Optional[bool] = None
#     SiblingsNumber: Optional[int] = None
#     ChildNumber: Optional[int] = None
#     IDSchoolClassYear: Optional[int] = None
#     IDClass: Optional[int] = None
#     PayedLevelCourse: Optional[bool] = None

# class LocationCreateDTO(BaseDTO):
#     Country: str
#     State: str
#     Province: str


# class AddressCreateDTO(BaseDTO):
#     Location: LocationCreateDTO
#     MainStreet: str
#     Number: str
#     SecondStreet: str

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