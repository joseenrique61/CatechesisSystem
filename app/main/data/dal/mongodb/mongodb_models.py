from mongoengine import (Document, EmbeddedDocument, StringField, IntField, DateField,
                         BooleanField, ListField, ReferenceField, EmbeddedDocumentField)
from werkzeug.security import check_password_hash, generate_password_hash

# class RoleDocument(EmbeddedDocument):
#     """Rol del usuario, anidado en UserDocument."""
#     Role = StringField(required=True)

class LocationDocument(EmbeddedDocument):
    """Ubicación geográfica, anidada en AddressDocument y PersonDocument."""
    Province = StringField(required=True)
    State = StringField(required=True)
    Country = StringField(required=True)

class AddressDocument(EmbeddedDocument):
    """Dirección física, anidada en ParishDocument y PersonDocument."""
    MainStreet = StringField(required=True)
    Number = StringField(required=True)
    SecondStreet = StringField(required=True)
    Location = EmbeddedDocumentField(LocationDocument, required=True)

class PhoneNumberDocument(EmbeddedDocument):
    """Número de teléfono, anidado en PersonDocument."""
    PhoneNumber = StringField(required=True)
    PhoneNumberType = ReferenceField('PhoneNumberTypeDocument')

class TextBookDocument(EmbeddedDocument):
    """Libro de texto, anidado en LevelDocument."""
    AuthorName = StringField(required=True)
    ImplementationDate = DateField(required=True)
    PagesNumber = IntField(required=True)
    NameBook = StringField(required=True)

class SchoolEmbedded(EmbeddedDocument):
    """Información escolar del catequizando, anidada en CatechizingDocument."""
    SchoolYear = StringField(required=True)
    SchoolName = StringField(required=True)

class ScheduleEmbedded(EmbeddedDocument):
    """Horario de una clase, anidado en ClassDocument."""
    DayOfTheWeek = StringField(required=True) # CAMBIO: Simplificado a String.
    StartHour = StringField(required=True)
    EndHour = StringField(required=True)
    Classroom = ReferenceField('ClassroomDocument', required=True)

class DataSheetEmbedded(EmbeddedDocument):
    """Ficha de datos del catequizando, anidada en CatechizingDocument."""
    DataSheetInformation = StringField(required=True)

class HealthInformationEmbedded(EmbeddedDocument):
    """Información de salud del catequizando, anidada en CatechizingDocument."""
    ImportantAspects = StringField(required=True)
    BloodType = StringField()
    EmergencyContact = ReferenceField('PersonDocument')
    Allergy = ListField(StringField())

# REFACTORIZADO: Estructura aplanada para el libro bautismal.
class BaptismalBookEmbedded(EmbeddedDocument):
    """Libro bautismal, anidado en BaptismalCertificateDocument."""
    Page = IntField(required=True)
    Volume = IntField(required=True)

# REFACTORIZADO: Estructura del certificado de bautismo simplificada.
class BaptismalCertificateDocument(EmbeddedDocument):
    IssueDate = DateField(required=True)
    BaptismalBook = EmbeddedDocumentField(BaptismalBookEmbedded, required=True)
    ParishPriest = ReferenceField('ParishPriestDocument', required=True)

class ParticularClassEmbedded(EmbeddedDocument):
    """Clase particular, anidada como lista en CatechizingDocument."""
    IssueDate = DateField(required=True)
    ParishPriest = ReferenceField('ParishPriestDocument', required=True)
    Level = ReferenceField('LevelDocument', required=True)
    ClassDate = DateField(required=True)

class AttendedClassEmbedded(EmbeddedDocument):
    """Asistencia a clase, anidada como lista en CatechizingDocument."""
    Class = ReferenceField('ClassDocument', required=True)
    Date = DateField(required=True)

# --- Documentos Principales (Colecciones de Nivel Superior en MongoDB) ---

class PhoneNumberTypeDocument(Document):
    """Tipo de teléfono."""
    PhoneNumberType = StringField(required=True)
    meta = {'collection': 'PhoneNumberType'}

class PersonDocument(Document):
    FirstName = StringField()
    MiddleName = StringField()
    FirstSurname = StringField()
    SecondSurname = StringField()
    BirthDate = DateField()
    DNI = StringField()
    Gender = StringField()
    EmailAddress = StringField(required=True, unique=True)
    Address = EmbeddedDocumentField(AddressDocument)
    BirthLocation = EmbeddedDocumentField(LocationDocument)
    PhoneNumber = EmbeddedDocumentField(PhoneNumberDocument)
    meta = {'collection': 'Person'}

class ClassroomDocument(Document):
    ClassroomName = StringField(required=True)
    meta = {'collection': 'Classroom'}

class ParishDocument(Document):
    Name = StringField(required=True)
    Logo = StringField()
    Address = EmbeddedDocumentField(AddressDocument)
    Classroom = ListField(ReferenceField(ClassroomDocument))
    IsMainParish = BooleanField(default=False)
    meta = {'collection': 'Parish'}

class ClassPeriodDocument(Document):
    StartDate = DateField(required=True)
    EndDate = DateField(required=True)
    CurrentPeriod = BooleanField(default=False)
    meta = {'collection': 'ClassPeriod'}


class UserDocument(Document):
    Username = StringField(required=True, unique=True)
    Password = StringField(required=True)
    Role = StringField(required=True)
    meta = {'collection': 'User'}

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.Password, password)

    def set_password(self, password: str) -> None:
        self.Password = generate_password_hash(password)

class LevelDocument(Document):
    Name = StringField(required=True)
    MinAge = IntField(required=True)
    MaxAge = IntField(required=True)
    PreviousLevel = ReferenceField('self')
    TextBook = EmbeddedDocumentField(TextBookDocument, required=True)
    meta = {'collection': 'Level'}

class SacramentDocument(Document):
    Name = StringField(required=True, unique=True)
    meta = {'collection': 'Sacrament'}

# --- Documentos de Roles de Persona ---

class CatechistDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    User = ReferenceField(UserDocument, required=True, unique=True)
    Parish = ReferenceField(ParishDocument, required=True) # CAMBIO: Añadido campo Parish.
    meta = {'collection': 'Catechist'}

class GodparentDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    meta = {'collection': 'GodParent'}

class ParentDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    Ocuppation = StringField(required=True)
    meta = {'collection': 'Parent'}

class ParishPriestDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    User = ReferenceField(UserDocument, required=True, unique=True)
    Parish = ReferenceField(ParishDocument, required=True)
    meta = {'collection': 'ParishPriest'}

class SupportPersonDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    Parish = ReferenceField(ParishDocument, required=True) # CAMBIO: Añadido campo Parish.
    meta = {'collection': 'SupportPerson'} # CAMBIO: Nombre de colección en minúscula y con guión bajo.

class AdministratorDocument(Document):
    User = ReferenceField(UserDocument)
    meta = {'collection': 'Administrator'}

# --- Documentos Relacionales y Principales ---

class ClassDocument(Document):
    ClassPeriod = ReferenceField(ClassPeriodDocument, required=True)
    SupportPerson = ReferenceField(SupportPersonDocument)
    Catechist = ReferenceField(CatechistDocument, required=True)
    Level = ReferenceField(LevelDocument, required=True)
    Schedule = EmbeddedDocumentField(ScheduleEmbedded) 
    meta = {'collection': 'Class'}

class CatechizingDocument(Document):
    Person = ReferenceField(PersonDocument, required=True)
    Class = ReferenceField(ClassDocument)
    IsLegitimate = BooleanField(required=True)
    SiblingsNumber = IntField(required=True)
    ChildNumber = IntField(required=True)
    PayedLevelCourse = BooleanField(required=True)
    DataSheetInformation = StringField()

    # --- Campos Embebidos Refactorizados ---
    School = EmbeddedDocumentField(SchoolEmbedded)
    # DataSheet = EmbeddedDocumentField(DataSheetEmbedded)
    HealthInformation = EmbeddedDocumentField(HealthInformationEmbedded)
    BaptismalCertificate = EmbeddedDocumentField(BaptismalCertificateDocument)

    # --- Listas de Referencias (Relaciones 1-a-N) ---
    Parent = ListField(ReferenceField(ParentDocument))
    Godparent = ListField(ReferenceField(GodparentDocument))
    Sacrament = ListField(ReferenceField(SacramentDocument))
    LevelCertificate = ListField(ReferenceField(ClassDocument))

    # --- Listas de Documentos Embebidos (sin cambios estructurales) ---
    AttendedClass = ListField(EmbeddedDocumentField(AttendedClassEmbedded))
    ParticularClass = ListField(EmbeddedDocumentField(ParticularClassEmbedded))

    meta = {'collection': 'Catechizing'}
