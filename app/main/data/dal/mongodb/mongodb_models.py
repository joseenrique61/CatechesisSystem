from mongoengine import (Document, EmbeddedDocument, StringField, IntField, DateField,
                         BooleanField, ListField, ReferenceField, EmbeddedDocumentField,
                         ObjectIdField)
import datetime

# --- Documentos de Catálogo / Entidades Independientes ---

class LocationDocument(Document):
    IDLocation = IntField(primary_key=True)
    Province = StringField(required=True)
    State = StringField(required=True)
    Country = StringField(required=True)
    meta = {'collection': 'LocationInformation_Location'}

class AddressDocument(Document):
    IDAddress = IntField(primary_key=True)
    MainStreet = StringField(required=True)
    Number = StringField(required=True)
    SecondStreet = StringField(required=True)
    # Atributo Python 'Location', en BD se almacena en 'IDLocation'
    Location = ReferenceField(LocationDocument, required=True, db_field="IDLocation")
    meta = {'collection': 'LocationInformation_Address'}

class PhoneNumberTypeDocument(Document):
    IDPhoneNumberType = IntField(primary_key=True)
    PhoneNumberType = StringField(required=True)
    meta = {'collection': 'PersonalInformation_PhoneNumberType'}

class PhoneNumberDocument(Document):
    IDPhoneNumer = IntField(primary_key=True) # DTO tiene 'IDPhoneNumer'
    PhoneNumber = StringField(required=True)
    # Atributo Python 'PhoneNumberType', en BD se almacena en 'IDPhoneNumberType'
    PhoneNumberType = ReferenceField(PhoneNumberTypeDocument, required=True, db_field="IDPhoneNumberType")
    meta = {'collection': 'PersonalInformation_PhoneNumber'}

class TextBookDocument(Document):
    IDTextBook = IntField(primary_key=True)
    AuthorName = StringField(required=True)
    ImplementationDate = DateField(required=True)
    PagesNumber = IntField(required=True)
    NameBook = StringField(required=True)
    meta = {'collection': 'Book_TextBook'}

class BaptismalBookVolumeDocument(Document):
    IDBaptismalBookVolume = IntField(primary_key=True)
    Volume = IntField(required=True)
    meta = {'collection': 'Certificate_BaptismalBookVolume'}

class BaptismalBookPageDocument(Document):
    IDBaptismalBookPage = IntField(primary_key=True)
    Page = IntField(required=True)
    # Atributo Python 'BaptismalBookVolume', en BD se almacena en 'IDBaptismalBookVolume'
    BaptismalBookVolume = ReferenceField(BaptismalBookVolumeDocument, required=True, db_field="IDBaptismalBookVolume")
    meta = {'collection': 'Certificate_BaptismalBookPage'}

class ClassPeriodDocument(Document):
    IDClassPeriod = IntField(primary_key=True)
    StartDate = DateField(required=True)
    EndDate = DateField(required=True)
    CurrentPeriod = BooleanField(default=False)
    meta = {'collection': 'ClassInformation_ClassPeriod'}

class DayOfTheWeekDocument(Document):
    IDDayOfTheWeek = IntField(primary_key=True)
    DayOfTheWeek = StringField(required=True)
    meta = {'collection': 'ClassInformation_DayOfTheWeek'}

class AllergyDocument(Document):
    IDAllergy = IntField(primary_key=True)
    Allergy = StringField(required=True)
    meta = {'collection': 'PersonalInformation_Allergy'}

class BloodTypeDocument(Document):
    IDBloodType = IntField(primary_key=True)
    BloodType = StringField(required=True)
    meta = {'collection': 'PersonalInformation_BloodType'}

class RoleDocument(Document):
    IDRole = IntField(primary_key=True)
    Role = StringField(required=True)
    meta = {'collection': 'User_Role'}

class SchoolDocument(Document):
    IDSchool = IntField(primary_key=True)
    SchoolName = StringField(required=True)
    Address = ReferenceField(AddressDocument, db_field="IDAddress")
    meta = {'collection': 'SchoolInformation_School'}

class SchoolClassYearDocument(Document):
    IDSchoolClassYear = IntField(primary_key=True)
    SchoolYear = StringField(required=True)
    School = ReferenceField(SchoolDocument, required=True, db_field="IDSchool")
    meta = {'collection': 'SchoolInformation_SchoolClassYear'}

class ClassroomDocument(Document):
    IDClassroom = IntField(primary_key=True)
    ClassroomName = StringField(required=True)
    Parish = ReferenceField('ParishDocument', required=True, db_field="IDParish")
    meta = {'collection': 'ClassInformation_Classroom'}

# --- Documentos Principales ---

class PersonDocument(Document):
    IDPerson = IntField(primary_key=True)
    FirstName = StringField()
    MiddleName = StringField()
    FirstSurname = StringField()
    SecondSurname = StringField()
    BirthDate = DateField()
    DNI = StringField()
    Gender = StringField()
    EmailAddress = StringField(required=True)
    Address = ReferenceField(AddressDocument, db_field="IDAddress")
    BirthLocation = ReferenceField(LocationDocument, db_field="IDBirthLocation")
    PhoneNumber = ReferenceField(PhoneNumberDocument, db_field="IDPhoneNumber")
    meta = {'collection': 'Person_Person'}

class UserDocument(Document):
    IDUser = IntField(primary_key=True)
    Username = StringField(required=True, unique=True)
    Password = StringField()
    Role = ReferenceField(RoleDocument, required=True, db_field="IDRole")
    meta = {'collection': 'User_User'}

class AdministratorDocument(Document): # Asume que este IDUser es la PK y referencia a UserDocument
    User = ReferenceField(UserDocument, primary_key=True, db_field="IDUser")
    meta = {'collection': 'User_Administrator'}

class LevelDocument(Document):
    IDLevel = IntField(primary_key=True)
    Name = StringField(required=True)
    MinAge = IntField(required=True)
    MaxAge = IntField(required=True)
    PreviousLevel = ReferenceField('self', db_field="IDPreviousLevel") # Nombre DTO: IDPreviousLevel
    TextBook = ReferenceField(TextBookDocument, required=True, db_field="IDTextBook") # Nombre DTO: TextBook
    meta = {'collection': 'Catechesis_Level'}

class SacramentDocument(Document): # Define los TIPOS de sacramentos
    IDSacrament = IntField(primary_key=True)
    Name = StringField(required=True, unique=True)
    Level = ReferenceField(LevelDocument, db_field="IDLevel", unique=True, required=False)
    meta = {'collection': 'Catechesis_Sacrament'}

class ParishDocument(Document):
    IDParish = IntField(primary_key=True)
    Name = StringField(required=True)
    Logo = StringField()
    Address = ReferenceField(AddressDocument, db_field="IDAddress")
    IsMainParish = BooleanField(default=False) # Nombre de atributo Python igual al DTO
    meta = {'collection': 'Catechesis_Parish'}

# --- Tipos de Persona ---

class CatechistDocument(Document):
    IDCatechist = IntField(primary_key=True) # PK de esta colección
    Person = ReferenceField(PersonDocument, required=True, db_field="IDCatechist") # El campo en BD es IDCatechist y apunta a PersonDocument
    User = ReferenceField(UserDocument, required=True, unique=True, db_field="IDUser")
    meta = {'collection': 'Person_Catechist'}

class GodparentDocument(Document):
    IDGodparent = IntField(primary_key=True)
    Person = ReferenceField(PersonDocument, required=True, db_field="IDGodparent")
    meta = {'collection': 'Person_Godparent'}

class ParentDocument(Document):
    IDParent = IntField(primary_key=True)
    Person = ReferenceField(PersonDocument, required=True, db_field="IDParent")
    Ocuppation = StringField(required=True)
    meta = {'collection': 'Person_Parent'}

class ParishPriestDocument(Document):
    IDParishPriest = IntField(primary_key=True)
    Person = ReferenceField(PersonDocument, required=True, db_field="IDParishPriest")
    User = ReferenceField(UserDocument, required=True, unique=True, db_field="IDUser")
    Parish = ReferenceField(ParishDocument, required=True, db_field="IDParish")
    meta = {'collection': 'Person_ParishPriest'}

class SupportPersonDocument(Document):
    IDSupportPerson = IntField(primary_key=True)
    Person = ReferenceField(PersonDocument, required=True, db_field="IDSupportPerson")
    meta = {'collection': 'Person_SupportPerson'}

# --- Schedule Anidado ---
class ScheduleEmbedded(EmbeddedDocument):
    DayOfTheWeek = ReferenceField(DayOfTheWeekDocument, required=True, db_field="IDDayOfTheWeek")
    StartHour = StringField(required=True)
    EndHour = StringField(required=True)
    Classroom = ReferenceField(ClassroomDocument, required=True, db_field="IDClassroom")
    # El DTO original de ScheduleDTO tiene un IDSchedule. Si Schedule se embebe,
    # este IDSchedule no tendría sentido como PK. Si Schedule fuera su propia colección, SÍ tendría IDSchedule.
    # Por ahora, al ser embebido, no le pongo IDSchedule.

class ClassDocument(Document):
    IDClass = IntField(primary_key=True)
    ClassPeriod = ReferenceField(ClassPeriodDocument, required=True, db_field="IDClassPeriod")
    Catechist = ReferenceField(CatechistDocument, required=True, db_field="IDCatechist")
    Level = ReferenceField(LevelDocument, required=True, db_field="IDLevel")
    SupportPerson = ReferenceField(SupportPersonDocument, required=True, db_field="IDSupportPerson")
    Schedule = ListField(EmbeddedDocumentField(ScheduleEmbedded)) # El campo en BD se llamará 'Schedule'
    meta = {'collection': 'ClassInformation_Class'}

class ClassAuthorizationDocument(Document):
    IDClassAuthorization = IntField(primary_key=True)
    IssueDate = DateField(required=True)
    ParishPriest = ReferenceField(ParishPriestDocument, required=True, db_field="IDParishPriest")
    meta = {'collection': 'ClassInformation_ClassAuthorization'}

# --- Documentos Específicos de Catechizing ---

class HealthInformationEmbedded(EmbeddedDocument):
    ImportantAspects = StringField(required=True)
    BloodType = ReferenceField(BloodTypeDocument, db_field="IDBloodType")
    EmergencyContact = ReferenceField(PersonDocument, db_field="IDEmergencyContact") # Atributo 'EmergencyContact', campo en BD 'IDEmergencyContact'
    Allergy = ListField(ReferenceField(AllergyDocument)) # El campo en BD será 'Allergy' y contendrá lista de IDs

class DataSheetEmbedded(EmbeddedDocument):
    DataSheetInformation = StringField(required=True)
    # IDPerson del DTO no es necesario aquí como PK del DataSheet embebido.
    # Se asocia al Catequizando padre.

class CatechizingDocument(Document):
    IDCatechizing = IntField(primary_key=True)
    # DTO: Person: Optional['PersonDTO']
    Person = ReferenceField(PersonDocument, required=True, db_field="IDCatechizing") # Campo BD: IDCatechizing (PK de Person)
    IsLegitimate = BooleanField(required=True)
    SiblingsNumber = IntField(required=True)
    ChildNumber = IntField(required=True)
    PayedLevelCourse = BooleanField(required=True)
    # DTO: Class: Optional['ClassDTO']
    Class = ReferenceField(ClassDocument, db_field="IDClass") # Campo BD: IDClass
    # DTO: SchoolClassYear: Optional['SchoolClassYearDTO']
    SchoolClassYear = ReferenceField(SchoolClassYearDocument, db_field="IDSchoolClassYear") # Campo BD: IDSchoolClassYear

    DataSheet = EmbeddedDocumentField(DataSheetEmbedded) # Asumiendo que DataSheetEmbedded está definido
    HealthInformation = EmbeddedDocumentField(HealthInformationEmbedded) # Asumiendo que HealthInformationEmbedded está definido

    # DTO: Parent: List['ParentDTO']
    Parent = ListField(ReferenceField(ParentDocument)) # Campo BD 'Parent', lista de IDs de Parent
    # DTO: Godparent: List['GodparentDTO']
    Godparent = ListField(ReferenceField(GodparentDocument)) # Campo BD 'Godparent', lista de IDs de Godparent

    # DTO: Sacrament: List['SacramentDTO'] = []
    # Esto será una lista de referencias a SacramentDocument.
    # El campo en BD almacenará una lista de IDSacrament.
    Sacrament = ListField(ReferenceField(SacramentDocument)) # El campo en BD se llamará 'Sacrament'

    meta = {'collection': 'Person_Catechizing'}


class BaptismalCertificateDocument(Document):
    # DTO tiene IDCatechizing como PK y FK.
    Catechizing = ReferenceField(CatechizingDocument, primary_key=True, db_field="IDCatechizing")
    IssueDate = DateField(required=True)
    BaptismalBookPage = ReferenceField(BaptismalBookPageDocument, required=True, db_field="IDBaptismalBookPage")
    ParishPriest = ReferenceField(ParishPriestDocument, required=True, db_field="IDParishPriest")
    meta = {'collection': 'Certificate_BaptismalCertificate'}

class LevelCertificateDocument(Document):
    IDLevelCertificate = IntField(primary_key=True)
    Catechizing = ReferenceField(CatechizingDocument, required=True, db_field="IDCatechizing")
    Class = ReferenceField(ClassDocument, required=True, db_field="IDClass") # Atributo 'Class', campo BD 'IDClass'
    meta = {'collection': 'Certificate_LevelCertificate'}

class AttendedClassDocument(Document):
    # Como antes, usando índice único para la clave semántica
    IDCatechizing = ReferenceField(CatechizingDocument, required=True) # Atributo y campo BD son IDCatechizing
    IDClass = ReferenceField(ClassDocument, required=True) # Atributo y campo BD son IDClass
    Date = DateField(required=True)
    meta = {
        'collection': 'ClassInformation_AttendedClass',
        'indexes': [
            {'fields': ('IDCatechizing', 'IDClass', 'Date'), 'unique': True}
        ]
    }

class ParticularClassDocument(Document):
    IDParticularClass = IntField(primary_key=True)
    ClassDate = DateField(required=True)
    Catechizing = ReferenceField(CatechizingDocument, required=True, db_field="IDCatechizing")
    ClassAuthorization = ReferenceField(ClassAuthorizationDocument, required=True, db_field="IDClassAuthorization")
    Level = ReferenceField(LevelDocument, required=True, db_field="IDLevel")
    meta = {'collection': 'ClassInformation_ParticularClass'}