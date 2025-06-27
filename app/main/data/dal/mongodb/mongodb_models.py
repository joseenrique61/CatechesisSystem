from mongoengine import (Document, EmbeddedDocument, StringField, IntField, DateField,
                         BooleanField, ListField, ReferenceField, EmbeddedDocumentField)
from werkzeug.security import check_password_hash, generate_password_hash

# --- Documentos Embebidos (Estructuras de datos anidadas) ---
# Estas clases representan datos que, según el diagrama, existen DENTRO de otros documentos.
# Heredan de EmbeddedDocument, no tienen PK ni 'meta' class.

class RoleDocument(EmbeddedDocument):
    """Rol del usuario, anidado en UserDocument."""
    Role = StringField(required=True)

class LocationDocument(EmbeddedDocument):
    """Ubicación geográfica, anidada en AddressDocument y PersonDocument."""
    Province = StringField(required=True)
    State = StringField(required=True)
    Country = StringField(required=True)

class AddressDocument(EmbeddedDocument):
    """Dirección física, anidada en ParishDocument, PersonDocument y SchoolDocument."""
    MainStreet = StringField(required=True)
    Number = StringField(required=True)
    SecondStreet = StringField(required=True)
    Location = EmbeddedDocumentField(LocationDocument, required=True)

class PhoneNumberTypeDocument(EmbeddedDocument):
    """Tipo de teléfono, anidado en PhoneNumberDocument."""
    PhoneNumberType = StringField(required=True)

class PhoneNumberDocument(EmbeddedDocument):
    """Número de teléfono, anidado en PersonDocument."""
    PhoneNumber = StringField(required=True)
    PhoneNumberType = EmbeddedDocumentField(PhoneNumberTypeDocument, required=True)

class TextBookDocument(EmbeddedDocument):
    """Libro de texto, anidado en LevelDocument."""
    AuthorName = StringField(required=True)
    ImplementationDate = DateField(required=True)
    PagesNumber = IntField(required=True)
    NameBook = StringField(required=True)

class SchoolDocument(EmbeddedDocument):
    """Información de la escuela, anidada en SchoolClassYearDocument."""
    SchoolName = StringField(required=True)
    Address = EmbeddedDocumentField(AddressDocument)

class SchoolClassYearDocument(EmbeddedDocument):
    """Año escolar del catequizando, anidado en CatechizingDocument."""
    SchoolYear = StringField(required=True)
    School = EmbeddedDocumentField(SchoolDocument, required=True)

class DayOfTheWeekDocument(EmbeddedDocument):
    """Día de la semana, anidado en ScheduleEmbedded."""
    DayOfTheWeek = StringField(required=True)

class ScheduleEmbedded(EmbeddedDocument):
    """Horario de una clase, anidado como lista en ClassDocument."""
    DayOfTheWeek = EmbeddedDocumentField(DayOfTheWeekDocument, required=True)
    StartHour = StringField(required=True)
    EndHour = StringField(required=True)
    Classroom = ReferenceField('ClassroomDocument', required=True, db_field="IDClassroom")

class DataSheetEmbedded(EmbeddedDocument):
    """Ficha de datos del catequizando, anidada en CatechizingDocument."""
    DataSheetInformation = StringField(required=True)

class AllergyDocument(EmbeddedDocument):
    """Alergia, anidada como lista en HealthInformationEmbedded."""
    Allergy = StringField(required=True)

class BloodTypeDocument(EmbeddedDocument):
    """Tipo de sangre, anidado en HealthInformationEmbedded."""
    BloodType = StringField(required=True)

class HealthInformationEmbedded(EmbeddedDocument):
    """Información de salud del catequizando, anidada en CatechizingDocument."""
    ImportantAspects = StringField(required=True)
    BloodType = EmbeddedDocumentField(BloodTypeDocument)
    EmergencyContact = ReferenceField('PersonDocument', db_field="IDEmergencyContact")
    Allergy = ListField(EmbeddedDocumentField(AllergyDocument))

class BaptismalBookVolumeDocument(EmbeddedDocument):
    """Volumen del libro bautismal, anidado en BaptismalBookPageDocument."""
    Volume = IntField(required=True)

class BaptismalBookPageDocument(EmbeddedDocument):
    """Página del libro bautismal, anidada en BaptismalCertificateDocument."""
    Page = IntField(required=True)
    BaptismalBookVolume = EmbeddedDocumentField(BaptismalBookVolumeDocument, required=True)

class AttendedClassEmbedded(EmbeddedDocument):
    """Refleja una asistencia a clase. Anidada como lista en CatechizingDocument según el diagrama."""
    Class = ReferenceField('ClassDocument', required=True, db_field="IDClass")
    Date = DateField(required=True)

class ParticularClassEmbedded(EmbeddedDocument):
    """Refleja una clase particular. Anidada como lista en CatechizingDocument según el diagrama."""
    ClassAuthorization = ReferenceField('ClassAuthorizationDocument', required=True, db_field="IDClassAuthorization")
    IssueDate = DateField(required=True)
    ParishPriest = ReferenceField('ParishPriestDocument', required=True, db_field="IDParishPriest")
    Level = ReferenceField('LevelDocument', required=True, db_field="IDLevel")
    ClassDate = DateField(required=True)

# --- Documentos Principales (Colecciones de Nivel Superior en MongoDB) ---
# Estas clases heredan de Document y representan colecciones independientes.

class ClassPeriodDocument(Document):
    IDClassPeriod = IntField(primary_key=True, db_field='_id')
    StartDate = DateField(required=True)
    EndDate = DateField(required=True)
    CurrentPeriod = BooleanField(default=False)
    meta = {'collection': 'ClassPeriod'}

class ClassroomDocument(Document):
    IDClassroom = IntField(primary_key=True, db_field='_id')
    ClassroomName = StringField(required=True)
    Parish = ReferenceField('ParishDocument', required=True, db_field="IDParish")
    meta = {'collection': 'Classroom'}

class PersonDocument(Document):
    IDPerson = IntField(primary_key=True, db_field='_id')
    FirstName = StringField()
    MiddleName = StringField()
    FirstSurname = StringField()
    SecondSurname = StringField()
    BirthDate = DateField()
    DNI = StringField()
    Gender = StringField()
    EmailAddress = StringField(required=True)
    Address = EmbeddedDocumentField(AddressDocument)
    BirthLocation = EmbeddedDocumentField(LocationDocument)
    PhoneNumber = EmbeddedDocumentField(PhoneNumberDocument)
    meta = {'collection': 'Person'}

class UserDocument(Document):
    IDUser = IntField(primary_key=True, db_field="_id")
    Username = StringField(required=True, unique=True)
    Password = StringField()
    Role = EmbeddedDocumentField(RoleDocument, required=True)
    meta = {'collection': 'User'}
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.Password, password)

    def set_password(self, password: str) -> None:
        self.Password = generate_password_hash(password)

class LevelDocument(Document):
    IDLevel = IntField(primary_key=True, db_field='_id')
    Name = StringField(required=True)
    MinAge = IntField(required=True)
    MaxAge = IntField(required=True)
    PreviousLevel = ReferenceField('self', db_field="IDPreviousLevel")
    TextBook = EmbeddedDocumentField(TextBookDocument, required=True)
    meta = {'collection': 'Level'}

class SacramentDocument(Document):
    IDSacrament = IntField(primary_key=True, db_field='_id')
    Name = StringField(required=True, unique=True)
    Level = ReferenceField(LevelDocument, db_field="IDLevel", unique=True, required=False)
    meta = {'collection': 'Sacrament'}

class ParishDocument(Document):
    IDParish = IntField(primary_key=True, db_field='_id')
    Name = StringField(required=True)
    Logo = StringField()
    Address = EmbeddedDocumentField(AddressDocument)
    IsMainParish = BooleanField(default=False)
    meta = {'collection': 'Parish'}

# --- Documentos de Roles de Persona ---

class CatechistDocument(Document):
    IDCatechist = IntField(primary_key=True, db_field='_id')
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    User = ReferenceField(UserDocument, required=True, unique=True, db_field="IDUser")
    meta = {'collection': 'Catechist'}

class GodparentDocument(Document):
    IDGodparent = IntField(primary_key=True, db_field='_id')
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    meta = {'collection': 'GodParent'}

class ParentDocument(Document):
    IDParent = IntField(primary_key=True, db_field='_id')
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    Ocuppation = StringField(required=True)
    meta = {'collection': 'Parent'}

class ParishPriestDocument(Document):
    IDParishPriest = IntField(primary_key=True, db_field='_id')
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    User = ReferenceField(UserDocument, required=True, unique=True, db_field="IDUser")
    Parish = ReferenceField(ParishDocument, required=True, db_field="IDParish")
    meta = {'collection': 'ParishPriest'}

class SupportPersonDocument(Document):
    IDSupportPerson = IntField(primary_key=True, db_field='_id')
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    meta = {'collection': 'support_person'}

# --- Documentos Relacionales y Principales ---

class ClassDocument(Document):
    IDClass = IntField(primary_key=True)
    ClassPeriod = ReferenceField(ClassPeriodDocument, required=True, db_field="IDClassPeriod")
    Catechist = ReferenceField(CatechistDocument, required=True, db_field="IDCatechist")
    Level = ReferenceField(LevelDocument, required=True, db_field="IDLevel")
    SupportPerson = ReferenceField(SupportPersonDocument, db_field="IDSupportPerson")
    Schedule = ListField(EmbeddedDocumentField(ScheduleEmbedded))
    meta = {'collection': 'Class'}

class ClassAuthorizationDocument(EmbeddedDocument):
    IDClassAuthorization = IntField(primary_key=True)
    IssueDate = DateField(required=True)
    ParishPriest = ReferenceField(ParishPriestDocument, required=True, db_field="IDParishPriest")

class CatechizingDocument(Document):
    IDCatechizing = IntField(primary_key=True)
    Person = ReferenceField(PersonDocument, required=True, db_field="IDPerson")
    IsLegitimate = BooleanField(required=True)
    SiblingsNumber = IntField(required=True)
    ChildNumber = IntField(required=True)
    PayedLevelCourse = BooleanField(required=True)
    Class = ReferenceField(ClassDocument, db_field="IDClass")
    
    # --- Campos Embebidos ---
    SchoolClassYear = EmbeddedDocumentField(SchoolClassYearDocument)
    DataSheet = EmbeddedDocumentField(DataSheetEmbedded)
    HealthInformation = EmbeddedDocumentField(HealthInformationEmbedded)
    
    # --- Listas de Referencias (Relaciones 1-a-N) ---
    Parent = ListField(ReferenceField(ParentDocument))
    Godparent = ListField(ReferenceField(GodparentDocument))
    Sacrament = ListField(ReferenceField(SacramentDocument))
    
    # --- Listas de Documentos Embebidos (según diagrama) ---
    AttendedClass = ListField(EmbeddedDocumentField(AttendedClassEmbedded))
    ParticularClass = ListField(EmbeddedDocumentField(ParticularClassEmbedded))

    meta = {'collection': 'Catechizing'}
    
class AdministratorDocument(Document): # Asume que este IDUser es la PK y referencia a UserDocument
    User = ReferenceField(UserDocument, db_field="IDUser")
    meta = {'collection': 'Administrator'}

class BaptismalCertificateDocument(EmbeddedDocument):
    Catechizing = ReferenceField(CatechizingDocument, primary_key=True, db_field="IDCatechizing")
    IssueDate = DateField(required=True)
    BaptismalBookPage = EmbeddedDocumentField(BaptismalBookPageDocument, required=True)
    ParishPriest = ReferenceField(ParishPriestDocument, required=True, db_field="IDParishPriest")

class LevelCertificateDocument(EmbeddedDocument):
    IDLevelCertificate = IntField(primary_key=True)
    Catechizing = ReferenceField(CatechizingDocument, required=True, db_field="IDCatechizing")
    Class = ReferenceField(ClassDocument, required=True, db_field="IDClass")