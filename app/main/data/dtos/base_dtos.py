# base_dtos.py (REFACTORIZADO)

from __future__ import annotations
import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.main.data.mapper import Mappable
from werkzeug.datastructures import FileStorage

# --- Base DTOs
class BaseDTO(BaseModel, Mappable):
    id: Optional[str] = None
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class TextBookDTO(BaseDTO):
    AuthorName: str
    ImplementationDate: datetime.date
    PagesNumber: int
    NameBook: str

# REFACTORIZADO: Estructura aplanada para el libro bautismal.
class BaptismalBookDTO(BaseDTO):
    Volume: int
    Page: int

class ClassPeriodDTO(BaseDTO):
    StartDate: datetime.date
    EndDate: datetime.date
    CurrentPeriod: bool = False

    def __str__(self):
        return f"{'Actual' if self.CurrentPeriod else 'Antiguo'} - Fecha de inicio: {self.StartDate}, Fecha de fin: {self.EndDate}"

class LocationDTO(BaseDTO):
    Province: str
    State: str
    Country: str
    
class BloodTypeDTO(BaseDTO):
    Type: str
    
class DayOfTheWeekDTO(BaseDTO):
    Day: str

class PhoneNumberTypeDTO(BaseDTO):
    PhoneNumberType: str

class UserDTO(BaseDTO):
    Username: str
    Password: Optional[str] = None
    Role: str

class LevelDTO(BaseDTO):
    Name: str
    MinAge: int
    MaxAge: int
    PreviousLevel: Optional[LevelDTO] = None
    TextBook: Optional['TextBookDTO'] = None

# REFACTORIZADO: El horario es un único objeto.
class ScheduleDTO(BaseDTO):
    DayOfTheWeek: str  # CAMBIO: Simplificado a string.
    StartHour: str
    EndHour: str
    Classroom: Optional['ClassroomDTO'] = None

class AddressDTO(BaseDTO):
    MainStreet: str
    Number: str
    SecondStreet: str
    Location: 'LocationDTO'

class PhoneNumberDTO(BaseDTO):
    PhoneNumber: str
    PhoneNumberType: Optional['PhoneNumberTypeDTO'] = None

class AdministratorDTO(BaseDTO):
    User: Optional['UserDTO'] = None

class ParishDTO(BaseDTO):
    Name: str
    Logo: Optional[str] = None
    LogoImage: Optional[FileStorage] = None
    Address: Optional['AddressDTO'] = None
    Classroom: List['ClassroomDTO'] = None 
    IsMainParish: bool

class SacramentDTO(BaseDTO):
    Name: str

# REFACTORIZADO: DTO de información de salud simplificado.
class HealthInformationDTO(BaseDTO):
    ImportantAspects: str
    BloodType: Optional[str] = None # CAMBIO: Simplificado a string.
    EmergencyContact: Optional['PersonDTO'] = None
    Allergy: List[str] = [] # CAMBIO: Simplificado a lista de strings.

class PersonDTO(BaseDTO):
    FirstName: Optional[str] = None
    FirstSurname: Optional[str] = None
    MiddleName: Optional[str] = None
    SecondSurname: Optional[str] = None
    BirthDate: Optional[datetime.date] = None
    Gender: Optional[str] = None
    DNI: Optional[str] = None
    EmailAddress: str
    Address: Optional['AddressDTO'] = None
    BirthLocation: Optional['LocationDTO'] = None
    PhoneNumber: Optional['PhoneNumberDTO'] = None

# REFACTORIZADO: Estructura aplanada para información escolar.
class SchoolDTO(BaseDTO):
    SchoolYear: str
    SchoolName: str

class ClassroomDTO(BaseDTO):
    ClassroomName: str
    Parish: Optional['ParishDTO'] = None

class CatechistDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None
    User: Optional['UserDTO'] = None
    Parish: Optional['ParishDTO'] = None # CAMBIO: Añadido Parish.

class GodparentDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None

class ParentDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None
    Ocuppation: str

class ParishPriestDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None
    User: Optional['UserDTO'] = None
    Parish: Optional['ParishDTO'] = None

class SupportPersonDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None
    Parish: Optional['ParishDTO'] = None
    
class MainParishDTO(BaseDTO):
    Parish: Optional[ParishDTO] = None

class ClassDTO(BaseDTO):
    ClassPeriod: Optional['ClassPeriodDTO'] = None
    SupportPerson: Optional['SupportPersonDTO'] = None
    Catechist: Optional['CatechistDTO'] = None
    Level: Optional['LevelDTO'] = None
    Schedule: Optional['ScheduleDTO'] = None

class ClassAuthorizationDTO(BaseDTO):
    IssueDate: datetime.date
    ParishPriest: Optional['ParishPriestDTO'] = None
    ParticularClass: Optional['ParticularClassDTO'] = None

class DataSheetDTO(BaseDTO):
    DataSheetInformation: str

class BaptismalCertificateDTO(BaseDTO):
    IssueDate: datetime.date
    BaptismalBook: Optional['BaptismalBookDTO'] = None
    ParishPriest: Optional['ParishPriestDTO'] = None

class AttendedClassDTO(BaseDTO):
    Date: datetime.date
    Class: Optional['ClassDTO'] = None

class ParticularClassDTO(BaseDTO):
    IssueDate: datetime.date
    Level: Optional['LevelDTO'] = None
    ClassDate: datetime.date
    
class CatechizingDTO(BaseDTO):
    Person: Optional['PersonDTO'] = None
    IsLegitimate: bool
    SiblingsNumber: int
    ChildNumber: int
    PayedLevelCourse: bool
    DataSheetInformation: str
    
    # --- DTOs Embebidos Refactorizados ---
    Class: Optional['ClassDTO'] = None
    School: Optional['SchoolDTO'] = None # CAMBIO: Nueva estructura aplanada.
    HealthInformation: Optional['HealthInformationDTO'] = None # CAMBIO: Utiliza la nueva estructura.
    BaptismalCertificate: Optional['BaptismalCertificateDTO'] = None # CAMBIO: Utiliza la nueva estructura.
    
    # --- Listas de DTOs ---
    Parent: List['ParentDTO'] = []
    Godparent: List['GodparentDTO'] = []
    Sacrament: List['SacramentDTO'] = []
    # CAMBIO: De lista de DTOs embebidos a lista de DTOs referenciados.
    LevelCertificate: List['ClassDTO'] = []
    AttendedClass: List['AttendedClassDTO'] = []
    ParticularClass: List['ParticularClassDTO'] = []

# --- Rebuild Models to Resolve Forward References ---
dto_models = [
    TextBookDTO, BaptismalBookDTO, ClassPeriodDTO, LocationDTO, 
    PhoneNumberTypeDTO, UserDTO, LevelDTO, ScheduleDTO, AddressDTO, 
    PhoneNumberDTO, AdministratorDTO, ParishDTO, SacramentDTO, HealthInformationDTO, 
    PersonDTO, SchoolDTO, ClassroomDTO, CatechistDTO, GodparentDTO, ParentDTO, 
    ParishPriestDTO, SupportPersonDTO, MainParishDTO, ClassDTO, 
    ClassAuthorizationDTO, DataSheetDTO, BaptismalCertificateDTO, 
    AttendedClassDTO, ParticularClassDTO, CatechizingDTO
]

for model in dto_models:
    model.model_rebuild()