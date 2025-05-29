from typing import List, Optional

from sqlalchemy import Boolean, CHAR, Column, Date, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, String, TEXT, Table, Unicode, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from app import db
from werkzeug.security import check_password_hash, generate_password_hash

from app.main.data.mapper import Mappable

class BaseModel(db.Model, Mappable):
    __abstract__ = True
    __should_raise_error_if_duplicate__ = False

class TextBook(BaseModel):
    __tablename__ = 'TextBook'
    __table_args__ = (
        PrimaryKeyConstraint('IDTextBook', name='pk_Book_IDBook'),
        {'schema': 'Book'}
    )

    IDTextBook: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    AuthorName: Mapped[str] = mapped_column(Unicode(200, 'Modern_Spanish_CI_AS'))
    ImplementationDate: Mapped[datetime.date] = mapped_column(Date)
    PagesNumber: Mapped[int] = mapped_column(Integer)
    NameBook: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))

    Level: Mapped[List['Level']] = relationship('Level', back_populates='TextBook')


class BaptismalBookVolume(BaseModel):
    __tablename__ = 'BaptismalBookVolume'
    __table_args__ = (
        PrimaryKeyConstraint('IDBaptismalBookVolume', name='pk_BaptismalBookVolume_IDBaptismalBookVolume'),
        Index('uk_BaptismalBookVolume_Volume', 'Volume', unique=True),
        {'schema': 'Certificate'}
    )

    IDBaptismalBookVolume: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Volume: Mapped[int] = mapped_column(Integer)

    BaptismalBookPage: Mapped[List['BaptismalBookPage']] = relationship('BaptismalBookPage', back_populates='BaptismalBookVolume')


class ClassPeriod(BaseModel):
    __tablename__ = 'ClassPeriod'
    __table_args__ = (
        PrimaryKeyConstraint('IDClassPeriod', name='pk_ClassPeriod_IDClassPeriod'),
        Index('uk_ClassPeriod_StartDate_EndDate', 'StartDate', 'EndDate', unique=True),
        {'schema': 'ClassInformation'}
    )

    IDClassPeriod: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    StartDate: Mapped[datetime.date] = mapped_column(Date)
    EndDate: Mapped[datetime.date] = mapped_column(Date)
    CurrentPeriod: Mapped[bool] = mapped_column(Boolean)

    Class: Mapped[List['Class']] = relationship('Class', back_populates='ClassPeriod')


class DayOfTheWeek(BaseModel):
    __tablename__ = 'DayOfTheWeek'
    __table_args__ = (
        PrimaryKeyConstraint('IDDayOfTheWeek', name='pk_DayOfTheWeek_IDDayOfTheWeek'),
        Index('uk_DayOfTheWeek_DayOfTheWeek', 'DayOfTheWeek', unique=True),
        {'schema': 'ClassInformation'}
    )

    IDDayOfTheWeek: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    DayOfTheWeek: Mapped[str] = mapped_column(Unicode(10, 'Modern_Spanish_CI_AS'))

    Schedule: Mapped[List['Schedule']] = relationship('Schedule', back_populates='DayOfTheWeek')


class Location(BaseModel):
    __tablename__ = 'Location'
    __table_args__ = (
        PrimaryKeyConstraint('IDLocation', name='pk_Location_IDLocation'),
        Index('uk_Location_Province_State_Country', 'Province', 'State', 'Country', unique=True),
        {'schema': 'LocationInformation'}
    )

    IDLocation: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Province: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'), server_default=text("('PICHINCHA')"))
    State: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'), server_default=text("('QUITO')"))
    Country: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'), server_default=text("('ECUADOR')"))

    Address: Mapped[List['Address']] = relationship('Address', back_populates='Location')
    Person: Mapped[List['Person']] = relationship('Person', back_populates='BirthLocation')

    @staticmethod
    def get_default_location():
        return Location.query.filter_by(Country='Ecuador', Province='Pichincha', State='Quito').first()


class Allergy(BaseModel):
    __tablename__ = 'Allergy'
    __table_args__ = (
        PrimaryKeyConstraint('IDAllergy', name='pk_Allergy_IDAllergy'),
        Index('uk_Allergy_Allergy', 'Allergy', unique=True),
        {'schema': 'PersonalInformation'}
    )

    IDAllergy: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Allergy: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))

    HealthInformation: Mapped[List['HealthInformation']] = relationship('HealthInformation', secondary='personalinformation.AllergyHealthInformation', back_populates='Allergy')


class BloodType(BaseModel):
    __tablename__ = 'BloodType'
    __table_args__ = (
        PrimaryKeyConstraint('IDBloodType', name='pk_BloodType_IDBloodType'),
        Index('uk_BloodType_BloodType', 'BloodType', unique=True),
        {'schema': 'PersonalInformation'}
    )

    IDBloodType: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    BloodType: Mapped[str] = mapped_column(Unicode(3, 'Modern_Spanish_CI_AS'))

    HealthInformation: Mapped[List['HealthInformation']] = relationship('HealthInformation', back_populates='BloodType')


class PhoneNumberType(BaseModel):
    __tablename__ = 'PhoneNumberType'
    __table_args__ = (
        PrimaryKeyConstraint('IDPhoneNumberType', name='pk_PhoneNumberType_IDPhoneNumberType'),
        Index('uk_PhoneNumberType_PhoneNumberType', 'PhoneNumberType', unique=True),
        {'schema': 'PersonalInformation'}
    )

    IDPhoneNumberType: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    PhoneNumberType: Mapped[str] = mapped_column(Unicode(50, 'Modern_Spanish_CI_AS'))

    PhoneNumber: Mapped[List['PhoneNumber']] = relationship('PhoneNumber', back_populates='PhoneNumberType')

class Role(BaseModel):
    __tablename__ = 'Role'
    __table_args__ = (
        PrimaryKeyConstraint('IDRole', name='pk_Role_IDRole'),
        Index('uk_Role_Role', 'Role', unique=True),
        {'schema': 'User'}
    )
    
    IDRole: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Role: Mapped[str] = mapped_column(Unicode(20, 'Modern_Spanish_CI_AS'))
    
    User: Mapped[List['User']] = relationship('User', back_populates='Role')

class User(BaseModel):
    __tablename__ = 'User'
    __table_args__ = (
        ForeignKeyConstraint(['IDRole'], ['User.Role.IDRole'], name='fk_Role_User'),
        PrimaryKeyConstraint('IDUser', name='pk_User_IDUser'),
        Index('uk_User_Username', 'Username', unique=True),
        {'schema': 'User'}
    )
    __should_raise_error_if_duplicate__ = True

    IDUser: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Username: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    Password: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    IDRole: Mapped[int] = mapped_column(Integer)

    Role: Mapped['Role'] = relationship('Role', back_populates='User')
    Administrator: Mapped['Administrator'] = relationship('Administrator', back_populates='User')
    Catechist: Mapped['Catechist'] = relationship('Catechist', back_populates='User')
    ParishPriest: Mapped['ParishPriest'] = relationship('ParishPriest', back_populates='User')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.Password, password)

    def set_password(self, password: str) -> None:
        self.Password = generate_password_hash(password)


class Level(BaseModel):
    __tablename__ = 'Level'
    __table_args__ = (
        ForeignKeyConstraint(['IDPreviousLevel'], ['Catechesis.Level.IDLevel'], name='fk_Level_PreviousLevel'),
        ForeignKeyConstraint(['IDTextBook'], ['Book.TextBook.IDTextBook'], name='fk_Book_Level'),
        PrimaryKeyConstraint('IDLevel', name='pk_Level_IDLevel'),
        Index('uk_Level_Name', 'Name', unique=True),
        Index('uk_Level_TextBookName', 'IDTextBook', unique=True),
        {'schema': 'Catechesis'}
    )

    IDLevel: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Name: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    IDTextBook: Mapped[int] = mapped_column(Integer)
    MinAge: Mapped[int] = mapped_column(Integer)
    MaxAge: Mapped[int] = mapped_column(Integer)
    IDPreviousLevel: Mapped[Optional[int]] = mapped_column(Integer)

    Level: Mapped[Optional['Level']] = relationship('Level', remote_side=[IDLevel], back_populates='Level_reverse')
    Level_reverse: Mapped[List['Level']] = relationship('Level', remote_side=[IDPreviousLevel], back_populates='Level')
    TextBook: Mapped['TextBook'] = relationship('TextBook', back_populates='Level')
    Sacrament: Mapped['Sacrament'] = relationship('Sacrament', back_populates='Level', uselist=False)
    Class: Mapped[List['Class']] = relationship('Class', back_populates='Level')
    ParticularClass: Mapped[List['ParticularClass']] = relationship('ParticularClass', back_populates='Level')


class BaptismalBookPage(BaseModel):
    __tablename__ = 'BaptismalBookPage'
    __table_args__ = (
        ForeignKeyConstraint(['IDBaptismalBookVolume'], ['Certificate.BaptismalBookVolume.IDBaptismalBookVolume'], name='fk_BaptismalBookVolume_BaptismalBookPage'),
        PrimaryKeyConstraint('IDBaptismalBookPage', name='pk_BaptismalBookPage_IDBaptismalBookPage'),
        Index('uk_BaptismalBookPage_Page_IDBaptismalBookVolume', 'Page', 'IDBaptismalBookVolume', unique=True),
        {'schema': 'Certificate'}
    )

    IDBaptismalBookPage: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Page: Mapped[int] = mapped_column(Integer)
    IDBaptismalBookVolume: Mapped[int] = mapped_column(Integer)

    BaptismalBookVolume: Mapped['BaptismalBookVolume'] = relationship('BaptismalBookVolume', back_populates='BaptismalBookPage')
    BaptismalCertificate: Mapped[List['BaptismalCertificate']] = relationship('BaptismalCertificate', back_populates='BaptismalBookPage')


class Schedule(BaseModel):
    __tablename__ = 'Schedule'
    __table_args__ = (
        ForeignKeyConstraint(['IDDayOfTheWeek'], ['ClassInformation.DayOfTheWeek.IDDayOfTheWeek'], name='fk_DayOfTheWeek_Schedule'),
        ForeignKeyConstraint(['IDClassroom'], ['ClassInformation.Classroom.IDClassroom'], name='fk_Classroom_Schedule'),
        PrimaryKeyConstraint('IDSchedule', name='pk_Schedule_IDSchedule'),
        Index('uk_Schedule_IDDayOfTheWeek_StartHour_EndHour_IDClassroom', 'IDDayOfTheWeek', 'IDClassroom', 'StartHour', 'EndHour', unique=True),
        {'schema': 'ClassInformation'}
    )

    IDSchedule: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDDayOfTheWeek: Mapped[int] = mapped_column(Integer)
    IDClassroom: Mapped[int] = mapped_column(Integer)
    StartHour: Mapped[str] = mapped_column(String(5, 'Modern_Spanish_CI_AS'))
    EndHour: Mapped[str] = mapped_column(String(5, 'Modern_Spanish_CI_AS'))

    Classroom: Mapped['Classroom'] = relationship('Classroom', back_populates='Schedule')
    DayOfTheWeek: Mapped['DayOfTheWeek'] = relationship('DayOfTheWeek', back_populates='Schedule')
    Class: Mapped[List['Class']] = relationship('Class', secondary='classinformation.ClassSchedule', back_populates='Schedule')


class Address(BaseModel):
    __tablename__ = 'Address'
    __table_args__ = (
        ForeignKeyConstraint(['IDLocation'], ['LocationInformation.Location.IDLocation'], name='fk_Location_Address'),
        PrimaryKeyConstraint('IDAddress', name='pk_Address_IDAddress'),
        Index('ix_AddressStrets', 'MainStreet', 'SecondStreet'),
        Index('uk_Address_IDLocation_MainStreet_Number_SecondStreet', 'IDLocation', 'MainStreet', 'Number', 'SecondStreet', unique=True),
        {'schema': 'LocationInformation'}
    )

    IDAddress: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDLocation: Mapped[int] = mapped_column(Integer)
    MainStreet: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    Number: Mapped[str] = mapped_column(Unicode(10, 'Modern_Spanish_CI_AS'))
    SecondStreet: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))

    Location: Mapped['Location'] = relationship('Location', back_populates='Address')
    Parish: Mapped[List['Parish']] = relationship('Parish', back_populates='Address')
    Person: Mapped[List['Person']] = relationship('Person', back_populates='Address')
    School: Mapped[List['School']] = relationship('School', back_populates='Address')


class PhoneNumber(BaseModel):
    __tablename__ = 'PhoneNumber'
    __table_args__ = (
        ForeignKeyConstraint(['IDPhoneNumberType'], ['PersonalInformation.PhoneNumberType.IDPhoneNumberType'], name='fk_PhoneNumberType_PhoneNumber'),
        PrimaryKeyConstraint('IDPhoneNumer', name='pk_PhoneNumber_IDPhoneNumer'),
        Index('uk_PhoneNumber_PhoneNumber', 'PhoneNumber', unique=True),
        {'schema': 'PersonalInformation'}
    )

    IDPhoneNumer: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    PhoneNumber: Mapped[str] = mapped_column(String(10, 'Modern_Spanish_CI_AS'))
    IDPhoneNumberType: Mapped[int] = mapped_column(Integer)

    PhoneNumberType: Mapped['PhoneNumberType'] = relationship('PhoneNumberType', back_populates='PhoneNumber')
    Person: Mapped[List['Person']] = relationship('Person', back_populates='PhoneNumber')


class Administrator(BaseModel):
    __tablename__ = 'Administrator'
    __table_args__ = (
        ForeignKeyConstraint(['IDUser'], ['User.User.IDUser'], name='fk_User_Administrator'),
        PrimaryKeyConstraint('IDUser', name='pk_Administrator_IDUser'),
        {'schema': 'user'}
    )

    IDUser: Mapped[int] = mapped_column(Integer, primary_key=True)

    User: Mapped['User'] = relationship('User', back_populates='Administrator')


class Parish(BaseModel):
    __tablename__ = 'Parish'
    __table_args__ = (
        ForeignKeyConstraint(['IDAddress'], ['LocationInformation.Address.IDAddress'], name='fk_Address_Parish'),
        PrimaryKeyConstraint('IDParish', name='pk_Parish_IDParish'),
        Index('uk_Parish_Name', 'Name', unique=True),
        {'schema': 'Catechesis'}
    )
    __should_raise_error_if_duplicate__ = True

    IDParish: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDAddress: Mapped[int] = mapped_column(Integer)
    Name: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    Logo: Mapped[str] = mapped_column(Unicode(40, 'Modern_Spanish_CI_AS'))

    Address: Mapped['Address'] = relationship('Address', back_populates='Parish')
    Classroom: Mapped[List['Classroom']] = relationship('Classroom', back_populates='Parish')
    ParishPriest: Mapped['ParishPriest'] = relationship('ParishPriest', back_populates='Parish')


class Sacrament(BaseModel):
    __tablename__ = 'Sacrament'
    __table_args__ = (
        ForeignKeyConstraint(['IDLevel'], ['Catechesis.Level.IDLevel'], name='fk_Level_Sacrament'),
        PrimaryKeyConstraint('IDSacrament', name='pk_Sacrament_IDSacrament'),
        Index('uk_Sacrament_IDLevel', 'IDLevel', unique=True),
        Index('uk_Sacrament_Name', 'Name', unique=True),
        {'schema': 'Catechesis'}
    )

    IDSacrament: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Name: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    IDLevel: Mapped[int] = mapped_column(Integer)

    Level: Mapped['Level'] = relationship('Level', back_populates='Sacrament', uselist=False)
    Catechizing: Mapped[List['Catechizing']] = relationship('Catechizing', secondary='catechesis.CatechizingSacrament', back_populates='Sacrament')


class HealthInformation(BaseModel):
    __tablename__ = 'HealthInformation'
    __table_args__ = (
        ForeignKeyConstraint(['IDBloodType'], ['PersonalInformation.BloodType.IDBloodType'], name='fk_BloodType_HealthInformation'),
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_HealthInformation'),
        ForeignKeyConstraint(['IDEmergencyContact'], ['Person.Person.IDPerson'], name='fk_Person_HealthInformation'),
        PrimaryKeyConstraint('IDCatechizing', name='pk_HealthInformation_IDPerson'),
        {'schema': 'PersonalInformation'}
    )

    IDCatechizing: Mapped[int] = mapped_column(Integer, primary_key=True)
    ImportantAspects: Mapped[str] = mapped_column(TEXT(247483647, 'Modern_Spanish_CI_AS'))
    IDBloodType: Mapped[int] = mapped_column(Integer)
    IDEmergencyContact: Mapped[int] = mapped_column(Integer)

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='HealthInformation', foreign_keys=[IDCatechizing])
    Allergy: Mapped[List['Allergy']] = relationship('Allergy', secondary='personalinformation.AllergyHealthInformation', back_populates='HealthInformation')
    BloodType: Mapped['BloodType'] = relationship('BloodType', back_populates='HealthInformation')
    EmergencyContact: Mapped['Person'] = relationship('Person', back_populates='HealthInformation', foreign_keys=[IDEmergencyContact])

class Person(BaseModel):
    __tablename__ = 'Person'
    __table_args__ = (
        ForeignKeyConstraint(['IDAddress'], ['LocationInformation.Address.IDAddress'], name='fk_Address_Person'),
        ForeignKeyConstraint(['IDBirthLocation'], ['LocationInformation.Location.IDLocation'], name='fk_Location_Person'),
        ForeignKeyConstraint(['IDPhoneNumber'], ['PersonalInformation.PhoneNumber.IDPhoneNumer'], name='fk_PhoneNumber_Person'),
        PrimaryKeyConstraint('IDPerson', name='pk_Person_IDPerson'),
        Index('ix_PersonBirthDay', 'BirthDate'),
        Index('ix_PersonDNI', 'DNI'),
        Index('ix_PersonEmail', 'EmailAddress'),
        Index('ix_PersonFirstNames', 'FirstName', 'MiddleName'),
        Index('ix_PersonGender', 'Gender'),
        Index('ix_PersonSurnames', 'FirstSurname', 'SecondSurname'),
        Index('uk_Person_DNI', 'DNI', unique=True),
        Index('uk_Person_FirstName_MiddleName_FirstSurname_SecondSurname', 'FirstName', 'MiddleName', 'FirstSurname', 'SecondSurname', unique=True),
        {'schema': 'Person'}
    )
    __should_raise_error_if_duplicate__ = True

    IDPerson: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    FirstName: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    MiddleName: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    FirstSurname: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    SecondSurname: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))
    BirthDate: Mapped[Optional[datetime.date]] = mapped_column(Date)
    IDBirthLocation: Mapped[int] = mapped_column(Integer)
    DNI: Mapped[str] = mapped_column(String(10, 'Modern_Spanish_CI_AS'))
    Gender: Mapped[str] = mapped_column(CHAR(1, 'Modern_Spanish_CI_AS'))
    IDAddress: Mapped[int] = mapped_column(Integer)
    IDPhoneNumber: Mapped[int] = mapped_column(Integer)
    EmailAddress: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))

    Address: Mapped['Address'] = relationship('Address', back_populates='Person')
    BirthLocation: Mapped['Location'] = relationship('Location', back_populates='Person')
    PhoneNumber: Mapped['PhoneNumber'] = relationship('PhoneNumber', back_populates='Person')
    HealthInformation: Mapped[List['HealthInformation']] = relationship('HealthInformation', back_populates='EmergencyContact', foreign_keys=[HealthInformation.IDEmergencyContact])
    ParishPriest: Mapped['ParishPriest'] = relationship('ParishPriest', back_populates='Person')
    Catechist: Mapped['Catechist'] = relationship('Catechist', back_populates='Person')
    SupportPerson: Mapped['SupportPerson'] = relationship('SupportPerson', back_populates='Person')
    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='Person')
    Parent: Mapped['Parent'] = relationship('Parent', back_populates='Person')
    Godparent: Mapped['Godparent'] = relationship('Godparent', back_populates='Person')


class School(BaseModel):
    __tablename__ = 'School'
    __table_args__ = (
        ForeignKeyConstraint(['IDAddress'], ['LocationInformation.Address.IDAddress'], name='fk_Address_School'),
        PrimaryKeyConstraint('IDSchool', name='pk_School_IDSchool'),
        Index('uk_School_SchoolName', 'SchoolName', unique=True),
        {'schema': 'SchoolInformation'}
    )

    IDSchool: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    SchoolName: Mapped[str] = mapped_column(Unicode(50, 'Modern_Spanish_CI_AS'))
    IDAddress: Mapped[int] = mapped_column(Integer)

    Address: Mapped['Address'] = relationship('Address', back_populates='School')
    SchoolClassYear: Mapped[List['SchoolClassYear']] = relationship('SchoolClassYear', back_populates='School')


class Classroom(BaseModel):
    __tablename__ = 'Classroom'
    __table_args__ = (
        ForeignKeyConstraint(['IDParish'], ['Catechesis.Parish.IDParish'], name='fk_Parish_Classroom'),
        PrimaryKeyConstraint('IDClassroom', name='pk_ClassRoom_IDClassroom'),
        {'schema': 'ClassInformation'}
    )

    IDClassroom: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    ClassroomName: Mapped[str] = mapped_column(String(5, 'Modern_Spanish_CI_AS'))
    IDParish: Mapped[int] = mapped_column(Integer)

    Parish: Mapped['Parish'] = relationship('Parish', back_populates='Classroom')
    Schedule: Mapped[List['Schedule']] = relationship('Schedule', back_populates='Classroom')


class Catechist(BaseModel):
    __tablename__ = 'Catechist'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechist'], ['Person.Person.IDPerson'], name='fk_Person_Catechist'),
        ForeignKeyConstraint(['IDUser'], ['User.User.IDUser'], name='fk_User_Catechist'),
        PrimaryKeyConstraint('IDCatechist', name='pk_Catechist_IDCatechist'),
        {'schema': 'Person'}
    )

    IDCatechist: Mapped[int] = mapped_column(Integer, primary_key=True)
    IDUser: Mapped[int] = mapped_column(Integer)

    User: Mapped['User'] = relationship('User', back_populates='Catechist')
    Person: Mapped['Person'] = relationship('Person', back_populates='Catechist')
    Class: Mapped[List['Class']] = relationship('Class', back_populates='Catechist')


class Godparent(BaseModel):
    __tablename__ = 'Godparent'
    __table_args__ = (
        ForeignKeyConstraint(['IDGodparent'], ['Person.Person.IDPerson'], name='fk_Person_GodParent'),
        PrimaryKeyConstraint('IDGodparent', name='pk_GodParent_IDPerson'),
        {'schema': 'Person'}
    )

    IDGodparent: Mapped[int] = mapped_column(Integer, primary_key=True)

    Person: Mapped['Person'] = relationship('Person', back_populates='Godparent')
    Catechizing: Mapped[List['Catechizing']] = relationship('Catechizing', secondary='person.CatechizingGodparent', back_populates='Godparent')


class Parent(BaseModel):
    __tablename__ = 'Parent'
    __table_args__ = (
        ForeignKeyConstraint(['IDParent'], ['Person.Person.IDPerson'], name='fk_Person_Parent'),
        PrimaryKeyConstraint('IDParent', name='pk_Parent_IDPerson'),
        {'schema': 'Person'}
    )

    IDParent: Mapped[int] = mapped_column(Integer, primary_key=True)
    Ocuppation: Mapped[str] = mapped_column(Unicode(100, 'Modern_Spanish_CI_AS'))

    Person: Mapped['Person'] = relationship('Person', back_populates='Parent')
    Catechizing: Mapped[List['Catechizing']] = relationship('Catechizing', secondary='person.CatechizingParent', back_populates='Parent')


class ParishPriest(BaseModel):
    __tablename__ = 'ParishPriest'
    __table_args__ = (
        ForeignKeyConstraint(['IDParish'], ['Catechesis.Parish.IDParish'], name='fk_Parish_ParishPriest'),
        ForeignKeyConstraint(['IDParishPriest'], ['Person.Person.IDPerson'], name='fk_Person_ParishPriest'),
        ForeignKeyConstraint(['IDUser'], ['User.User.IDUser'], name='fk_User_ParishPriest'),
        PrimaryKeyConstraint('IDParishPriest', name='pk_ParishPriest_IDPerson'),
        {'schema': 'Person'}
    )

    IDParishPriest: Mapped[int] = mapped_column(Integer, primary_key=True)
    IDUser: Mapped[int] = mapped_column(Integer)
    IDParish: Mapped[int] = mapped_column(Integer)

    Parish: Mapped['Parish'] = relationship('Parish', back_populates='ParishPriest')
    User: Mapped['User'] = relationship('User', back_populates='ParishPriest')
    Person: Mapped['Person'] = relationship('Person', back_populates='ParishPriest')
    ClassAuthorization: Mapped[List['ClassAuthorization']] = relationship('ClassAuthorization', back_populates='ParishPriest')
    BaptismalCertificate: Mapped[List['BaptismalCertificate']] = relationship('BaptismalCertificate', back_populates='ParishPriest')


class SupportPerson(BaseModel):
    __tablename__ = 'SupportPerson'
    __table_args__ = (
        ForeignKeyConstraint(['IDSupportPerson'], ['Person.Person.IDPerson'], name='fk_Person_SupportPerson'),
        PrimaryKeyConstraint('IDSupportPerson', name='pk_SupportPerson_IDPerson'),
        {'schema': 'Person'}
    )

    IDSupportPerson: Mapped[int] = mapped_column(Integer, primary_key=True)

    Person: Mapped['Person'] = relationship('Person', back_populates='SupportPerson')
    Class: Mapped[List['Class']] = relationship('Class', back_populates='SupportPerson')


class SchoolClassYear(BaseModel):
    __tablename__ = 'SchoolClassYear'
    __table_args__ = (
        ForeignKeyConstraint(['IDSchool'], ['SchoolInformation.School.IDSchool'], name='fk_School_SchoolClassYear'),
        PrimaryKeyConstraint('IDSchoolClassYear', name='pk_SchoolYear_IDSchoolYear'),
        Index("uk_SchoolClassYear_SchoolYear_IDSchool", "SchoolYear", "IDSchool", unique=True),
        {'schema': 'SchoolInformation'}
    )

    IDSchoolClassYear: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    SchoolYear: Mapped[str] = mapped_column(Unicode(10, 'Modern_Spanish_CI_AS'))
    IDSchool: Mapped[int] = mapped_column(Integer)

    School: Mapped['School'] = relationship('School', back_populates='SchoolClassYear')
    Catechizing: Mapped[List['Catechizing']] = relationship('Catechizing', back_populates='SchoolClassYear')


class MainParish(BaseModel):
    __tablename__ = 'MainParish'
    __table_args__ = (
        ForeignKeyConstraint(['IDMainParish'], ['Catechesis.Parish.IDParish'], name='fk_Parish_MainParish'),
        PrimaryKeyConstraint('IDMainParish', name='pk_MainParish_IDMainParish'),
        {'schema': 'catechesis'}
    )

    IDMainParish: Mapped[int] = mapped_column(Integer, primary_key=True)


class Class(BaseModel):
    __tablename__ = 'Class'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechist'], ['Person.Catechist.IDCatechist'], name='fk_Catechist_Class'),
        ForeignKeyConstraint(['IDClassPeriod'], ['ClassInformation.ClassPeriod.IDClassPeriod'], name='fk_ClassPeriod_Class'),
        ForeignKeyConstraint(['IDLevel'], ['Catechesis.Level.IDLevel'], name='fk_Level_Class'),
        ForeignKeyConstraint(['IDSupportPerson'], ['Person.SupportPerson.IDSupportPerson'], name='fk_SupportPerson_Class'),
        PrimaryKeyConstraint('IDClass', name='pk_Class_IDClass'),
        Index('ix_ClassLevel', 'IDLevel'),
        Index('ix_ClassPeriod', 'IDClassPeriod'),
        {'schema': 'ClassInformation'}
    )

    IDClass: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDLevel: Mapped[int] = mapped_column(Integer)
    IDClassPeriod: Mapped[int] = mapped_column(Integer)
    IDCatechist: Mapped[int] = mapped_column(Integer)
    IDSupportPerson: Mapped[int] = mapped_column(Integer)

    ClassPeriod: Mapped['ClassPeriod'] = relationship('ClassPeriod', back_populates='Class')
    Catechist: Mapped['Catechist'] = relationship('Catechist', back_populates='Class')
    Level: Mapped['Level'] = relationship('Level', back_populates='Class')
    SupportPerson: Mapped['SupportPerson'] = relationship('SupportPerson', back_populates='Class')
    Schedule: Mapped[List['Schedule']] = relationship('Schedule', secondary='classinformation.ClassSchedule', back_populates='Class')
    Catechizing: Mapped[List['Catechizing']] = relationship('Catechizing', back_populates='Class')
    LevelCertificate: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='Class')
    AttendedClass: Mapped[List['AttendedClass']] = relationship('AttendedClass', back_populates='Class')


class ClassAuthorization(BaseModel):
    __tablename__ = 'ClassAuthorization'
    __table_args__ = (
        ForeignKeyConstraint(['IDParishPriest'], ['Person.ParishPriest.IDParishPriest'], name='fk_ParishPriest_ClassAuthorization'),
        PrimaryKeyConstraint('IDClassAuthorization', name='pk_ClassAuthorization_IDClassAuthorization'),
        {'schema': 'ClassInformation'}
    )

    IDClassAuthorization: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IssueDate: Mapped[datetime.date] = mapped_column(Date, server_default=text('(getdate())'))
    IDParishPriest: Mapped[int] = mapped_column(Integer)

    ParishPriest: Mapped['ParishPriest'] = relationship('ParishPriest', back_populates='ClassAuthorization')
    ParticularClass: Mapped['ParticularClass'] = relationship('ParticularClass', back_populates='ClassAuthorization')


class Catechizing(BaseModel):
    __tablename__ = 'Catechizing'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Person.IDPerson'], name='fk_Person_Catechizing'),
        ForeignKeyConstraint(['IDClass'], ['ClassInformation.Class.IDClass'], name='fk_Class_Catechizing'),
        ForeignKeyConstraint(['IDSchoolClassYear'], ['SchoolInformation.SchoolClassYear.IDSchoolClassYear'], name='fk_SchoolClassYear_Catechizing'),
        PrimaryKeyConstraint('IDCatechizing', name='pk_Catechizing_IDPerson'),
        Index('ix_CatechizingPayedCourse', 'PayedLevelCourse'),
        {'schema': 'Person'}
    )

    IDCatechizing: Mapped[int] = mapped_column(Integer, primary_key=True)
    IsLegitimate: Mapped[bool] = mapped_column(Boolean)
    SiblingsNumber: Mapped[int] = mapped_column(Integer)
    ChildNumber: Mapped[int] = mapped_column(Integer)
    IDSchoolClassYear: Mapped[int] = mapped_column(Integer)
    IDClass: Mapped[int] = mapped_column(Integer)
    PayedLevelCourse: Mapped[bool] = mapped_column(Boolean)

    Class: Mapped['Class'] = relationship('Class', back_populates='Catechizing')
    Person: Mapped['Person'] = relationship('Person', back_populates='Catechizing', cascade="all, delete")
    BaptismalCertificate: Mapped['BaptismalCertificate'] = relationship('BaptismalCertificate', back_populates='Catechizing', cascade="all, delete")
    DataSheet: Mapped['DataSheet'] = relationship('DataSheet', back_populates='Catechizing', cascade="all, delete")
    HealthInformation: Mapped['HealthInformation'] = relationship('HealthInformation', back_populates='Catechizing', foreign_keys=[HealthInformation.IDCatechizing], cascade="all, delete")
    SchoolClassYear: Mapped['SchoolClassYear'] = relationship('SchoolClassYear', back_populates='Catechizing')
    Sacrament: Mapped[List['Sacrament']] = relationship('Sacrament', secondary='catechesis.CatechizingSacrament', back_populates='Catechizing')
    Godparent: Mapped[List['Godparent']] = relationship('Godparent', secondary='person.CatechizingGodparent', back_populates='Catechizing')
    Parent: Mapped[List['Parent']] = relationship('Parent', secondary='person.CatechizingParent', back_populates='Catechizing')
    LevelCertificate: Mapped[List['LevelCertificate']] = relationship('LevelCertificate', back_populates='Catechizing', cascade="all, delete")
    AttendedClass: Mapped[List['AttendedClass']] = relationship('AttendedClass', back_populates='Catechizing', cascade="all, delete")
    ParticularClass: Mapped[List['ParticularClass']] = relationship('ParticularClass', back_populates='Catechizing', cascade="all, delete")



t_ClassSchedule = Table(
    'ClassSchedule', db.Model.metadata,
    Column('IDClass', Integer, primary_key=True, nullable=False),
    Column('IDSchedule', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['IDClass'], ['ClassInformation.Class.IDClass'], name='fk_Class_ClassSchedule'),
    ForeignKeyConstraint(['IDSchedule'], ['ClassInformation.Schedule.IDSchedule'], name='fk_Schedule_ClassSchedule'),
    PrimaryKeyConstraint('IDClass', 'IDSchedule', name='pk_ClassSchedule_IDClass_IDSchedule'),
    schema='classinformation'
)



t_CatechizingSacrament = Table(
    'CatechizingSacrament', db.Model.metadata,
    Column('IDCatechizing', Integer, primary_key=True, nullable=False),
    Column('IDSacrament', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_CatechizingSacrament'),
    ForeignKeyConstraint(['IDSacrament'], ['Catechesis.Sacrament.IDSacrament'], name='fk_Sacrament_CatechizingSacrament'),
    PrimaryKeyConstraint('IDCatechizing', 'IDSacrament', name='pk_CatechizingSacrament_IDCatechizing_IDSacrament'),
    schema='catechesis'
)


class DataSheet(BaseModel):
    __tablename__ = 'DataSheet'
    __table_args__ = (
        ForeignKeyConstraint(['IDPerson'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_DataSheet'),
        PrimaryKeyConstraint('IDPerson', name='pk_DataSheet_IDPerson'),
        {'schema': 'catechesis'}
    )

    IDCatechizing: Mapped[int] = mapped_column(Integer, primary_key=True, name="IDPerson")

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='DataSheet')
    DataSheetInformation: Mapped[str] = mapped_column(Unicode(500, 'Modern_Spanish_CI_AS'))


class BaptismalCertificate(BaseModel):
    __tablename__ = 'BaptismalCertificate'
    __table_args__ = (
        ForeignKeyConstraint(['IDBaptismalBookPage'], ['Certificate.BaptismalBookPage.IDBaptismalBookPage'], name='fk_BaptismalBookPage_BaptismalCertificate'),
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_BaptismalCertificate'),
        ForeignKeyConstraint(['IDParishPriest'], ['Person.ParishPriest.IDParishPriest'], name='fk_ParishPriest_BaptismalCertificate'),
        PrimaryKeyConstraint('IDCatechizing', name='pk_BaptismalCertificate_IDBaptismalCertificate'),
        {'schema': 'certificate'}
    )

    IDCatechizing: Mapped[int] = mapped_column(Integer, primary_key=True)
    IssueDate: Mapped[datetime.date] = mapped_column(Date, server_default=text('(getdate())'))
    IDBaptismalBookPage: Mapped[int] = mapped_column(Integer)
    IDParishPriest: Mapped[int] = mapped_column(Integer)

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='BaptismalCertificate')
    BaptismalBookPage: Mapped['BaptismalBookPage'] = relationship('BaptismalBookPage', back_populates='BaptismalCertificate')
    ParishPriest: Mapped['ParishPriest'] = relationship('ParishPriest', back_populates='BaptismalCertificate')


class LevelCertificate(BaseModel):
    __tablename__ = 'LevelCertificate'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_LevelCertificate'),
        ForeignKeyConstraint(['IDClass'], ['ClassInformation.Class.IDClass'], name='fk_Class_LevelCertificate'),
        PrimaryKeyConstraint('IDLevelCertificate', name='pk_LevelCertificate_IDLevelCertificate'),
        Index('uk_LevelCertificate_IDClass_IDCatechizing', 'IDClass', 'IDCatechizing', unique=True),
        {'schema': 'certificate'}
    )

    IDLevelCertificate: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDClass: Mapped[int] = mapped_column(Integer)
    IDCatechizing: Mapped[int] = mapped_column(Integer)

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='LevelCertificate')
    Class: Mapped['Class'] = relationship('Class', back_populates='LevelCertificate')


class AttendedClass(BaseModel):
    __tablename__ = 'AttendedClass'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Person_AttendedClass'),
        ForeignKeyConstraint(['IDClass'], ['ClassInformation.Class.IDClass'], name='fk_Class_AttendedClass'),
        PrimaryKeyConstraint('IDCatechizing', 'IDClass', 'Date', name='pk_AttendedClass_IDPerson_IDClass_Date'),
        {'schema': 'classinformation'}
    )

    IDCatechizing: Mapped[int] = mapped_column(Integer, primary_key=True)
    IDClass: Mapped[int] = mapped_column(Integer, primary_key=True)
    Date_: Mapped[datetime.date] = mapped_column('Date', Date, primary_key=True)

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='AttendedClass')
    Class: Mapped['Class'] = relationship('Class', back_populates='AttendedClass')


class ParticularClass(BaseModel):
    __tablename__ = 'ParticularClass'
    __table_args__ = (
        ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_ParticularClass'),
        ForeignKeyConstraint(['IDClassAuthorization'], ['ClassInformation.ClassAuthorization.IDClassAuthorization'], name='fk_ClassAuthorization_ParticularClass'),
        ForeignKeyConstraint(['IDLevel'], ['Catechesis.Level.IDLevel'], name='fk_Level_ParticularClass'),
        PrimaryKeyConstraint('IDParticularClass', name='pk_ParticularClass_IDParticularClass'),
        {'schema': 'classinformation'}
    )

    IDParticularClass: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    IDClassAuthorization: Mapped[int] = mapped_column(Integer)
    IDLevel: Mapped[int] = mapped_column(Integer)
    ClassDate: Mapped[datetime.date] = mapped_column(Date)
    IDCatechizing: Mapped[int] = mapped_column(Integer)

    Catechizing: Mapped['Catechizing'] = relationship('Catechizing', back_populates='ParticularClass')
    ClassAuthorization: Mapped['ClassAuthorization'] = relationship('ClassAuthorization', back_populates='ParticularClass')
    Level: Mapped['Level'] = relationship('Level', back_populates='ParticularClass')


t_CatechizingGodparent = Table(
    'CatechizingGodparent', db.Model.metadata,
    Column('IDCatechizing', Integer, primary_key=True, nullable=False),
    Column('IDGodparent', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_CatechizingGodparent'),
    ForeignKeyConstraint(['IDGodparent'], ['Person.Godparent.IDGodparent'], name='fk_Godparent_CatechizingGodparent'),
    PrimaryKeyConstraint('IDCatechizing', 'IDGodparent', name='pk_CatechizingGodparent_IDCatechizing_IDGodparent'),
    schema='person'
)


t_CatechizingParent = Table(
    'CatechizingParent', db.Model.metadata,
    Column('IDCatechizing', Integer, primary_key=True, nullable=False),
    Column('IDParent', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['IDCatechizing'], ['Person.Catechizing.IDCatechizing'], name='fk_Catechizing_CatechizingParent'),
    ForeignKeyConstraint(['IDParent'], ['Person.Parent.IDParent'], name='fk_Parent_CatechizingParent'),
    PrimaryKeyConstraint('IDCatechizing', 'IDParent', name='pk_CatechizingParent_IDCatechizing_IDParent'),
    schema='person'
)


t_AllergyHealthInformation = Table(
    'AllergyHealthInformation', db.Model.metadata,
    Column('IDAllergy', Integer, primary_key=True, nullable=False),
    Column('IDHealthInformation', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['IDAllergy'], ['PersonalInformation.Allergy.IDAllergy'], name='fk_Allergy_AllergyHealthInformation'),
    ForeignKeyConstraint(['IDHealthInformation'], ['PersonalInformation.HealthInformation.IDCatechizing'], name='fk_HealthInformation_AllergyHealthInformation'),
    PrimaryKeyConstraint('IDAllergy', 'IDHealthInformation', name='pk_AllergyHealthInformation_IDAllergy_IDHealthInformation'),
    schema='personalinformation'
)
