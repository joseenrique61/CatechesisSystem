# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Allergyhealthinformation(models.Model):
    idallergy = models.IntegerField(db_column='IDAllergy')  # Field name made lowercase.
    idhealthinformation = models.IntegerField(db_column='IDHealthInformation')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AllergyHealthInformation'


class Bloodtype(models.Model):
    idbloodtype = models.IntegerField(db_column='IDBloodType')  # Field name made lowercase.
    bloodtype = models.CharField(db_column='BloodType', max_length=3, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BloodType'


class Healthinformation(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    importantaspects = models.TextField(db_column='ImportantAspects', db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase. This field type is a guess.
    idbloodtype = models.IntegerField(db_column='IDBloodType')  # Field name made lowercase.
    idemergencycontact = models.IntegerField(db_column='IDEmergencyContact')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'HealthInformation'


class Phonenumber(models.Model):
    idphonenumer = models.IntegerField(db_column='IDPhoneNumer')  # Field name made lowercase.
    phonenumber = models.CharField(db_column='PhoneNumber', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idphonenumbertype = models.IntegerField(db_column='IDPhoneNumberType')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PhoneNumber'


class Phonenumbertype(models.Model):
    idphonenumbertype = models.IntegerField(db_column='IDPhoneNumberType')  # Field name made lowercase.
    phonenumbertype = models.CharField(db_column='PhoneNumberType', max_length=50, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PhoneNumberType'


class School(models.Model):
    idschool = models.IntegerField(db_column='IDSchool')  # Field name made lowercase.
    schoolname = models.CharField(db_column='SchoolName', max_length=50, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idaddress = models.IntegerField(db_column='IDAddress')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'School'


class Schoolclassyear(models.Model):
    idschoolclassyear = models.IntegerField(db_column='IDSchoolClassYear')  # Field name made lowercase.
    schoolyear = models.CharField(db_column='SchoolYear', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idschool = models.IntegerField(db_column='IDSchool')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SchoolClassYear'


class Administrator(models.Model):
    iduser = models.IntegerField(db_column='IDUser')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Administrator'


class User(models.Model):
    iduser = models.IntegerField(db_column='IDUser')  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class Textbook(models.Model):
    idtextbook = models.IntegerField(db_column='IDTextBook')  # Field name made lowercase.
    authorname = models.CharField(db_column='AuthorName', max_length=200, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    implementationdate = models.DateField(db_column='ImplementationDate')  # Field name made lowercase.
    pagesnumber = models.IntegerField(db_column='PagesNumber')  # Field name made lowercase.
    namebook = models.CharField(db_column='NameBook', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TextBook'


class Catechizingsacrament(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    idsacrament = models.IntegerField(db_column='IDSacrament')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CatechizingSacrament'


class Datasheet(models.Model):
    idperson = models.IntegerField(db_column='IDPerson')  # Field name made lowercase.
    datasheetinformation = models.CharField(db_column='DataSheetInformation', max_length=500, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DataSheet'


class Level(models.Model):
    idlevel = models.IntegerField(db_column='IDLevel')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idtextbook = models.IntegerField(db_column='IDTextBook')  # Field name made lowercase.
    minage = models.IntegerField(db_column='MinAge')  # Field name made lowercase.
    maxage = models.IntegerField(db_column='MaxAge')  # Field name made lowercase.
    idpreviouslevel = models.IntegerField(db_column='IDPreviousLevel', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Level'


class Mainparish(models.Model):
    idmainparish = models.IntegerField(db_column='IDMainParish')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MainParish'


class Parish(models.Model):
    idparish = models.IntegerField(db_column='IDParish')  # Field name made lowercase.
    logo = models.BinaryField(db_column='Logo', blank=True, null=True)  # Field name made lowercase.
    idaddress = models.IntegerField(db_column='IDAddress')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Parish'


class Sacrament(models.Model):
    idsacrament = models.IntegerField(db_column='IDSacrament')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idlevel = models.IntegerField(db_column='IDLevel')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sacrament'


class Baptismalbookpage(models.Model):
    idbaptismalbookpage = models.IntegerField(db_column='IDBaptismalBookPage')  # Field name made lowercase.
    page = models.IntegerField(db_column='Page')  # Field name made lowercase.
    idbaptismalbookvolume = models.IntegerField(db_column='IDBaptismalBookVolume')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BaptismalBookPage'


class Baptismalbookvolume(models.Model):
    idbaptismalbookvolume = models.IntegerField(db_column='IDBaptismalBookVolume')  # Field name made lowercase.
    volume = models.IntegerField(db_column='Volume')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BaptismalBookVolume'


class Baptismalcertificate(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    issuedate = models.DateField(db_column='IssueDate')  # Field name made lowercase.
    idbaptismalbookpage = models.IntegerField(db_column='IDBaptismalBookPage')  # Field name made lowercase.
    idparishpriest = models.IntegerField(db_column='IDParishPriest')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BaptismalCertificate'


class Levelcertificate(models.Model):
    idlevelcertificate = models.IntegerField(db_column='IDLevelCertificate')  # Field name made lowercase.
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LevelCertificate'


class Attendedclass(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AttendedClass'


class Class(models.Model):
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    idlevel = models.IntegerField(db_column='IDLevel')  # Field name made lowercase.
    idclassperiod = models.IntegerField(db_column='IDClassPeriod')  # Field name made lowercase.
    idcatechist = models.IntegerField(db_column='IDCatechist')  # Field name made lowercase.
    idsupportperson = models.IntegerField(db_column='IDSupportPerson')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Class'


class Classauthorization(models.Model):
    idclassauthorization = models.IntegerField(db_column='IDClassAuthorization')  # Field name made lowercase.
    issuedate = models.DateField(db_column='IssueDate')  # Field name made lowercase.
    idparishpriest = models.IntegerField(db_column='IDParishPriest')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ClassAuthorization'


class Classclassroom(models.Model):
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    idclasroom = models.IntegerField(db_column='IDClasroom')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ClassClassroom'


class Classperiod(models.Model):
    idclassperiod = models.IntegerField(db_column='IDClassPeriod')  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate')  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate')  # Field name made lowercase.
    currentperiod = models.BooleanField(db_column='CurrentPeriod')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ClassPeriod'


class Classroom(models.Model):
    idclassroom = models.IntegerField(db_column='IDClassroom')  # Field name made lowercase.
    classroomname = models.CharField(db_column='ClassroomName', max_length=5, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idparish = models.IntegerField(db_column='IDParish')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Classroom'


class Classschedule(models.Model):
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    idschedule = models.IntegerField(db_column='IDSchedule')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ClassSchedule'


class Dayoftheweek(models.Model):
    iddayoftheweek = models.IntegerField(db_column='IDDayOfTheWeek')  # Field name made lowercase.
    dayoftheweek = models.CharField(db_column='DayOfTheWeek', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DayOfTheWeek'


class Particularclass(models.Model):
    idparticularclass = models.IntegerField(db_column='IDParticularClass')  # Field name made lowercase.
    idclassauthorization = models.IntegerField(db_column='IDClassAuthorization')  # Field name made lowercase.
    idlevel = models.IntegerField(db_column='IDLevel')  # Field name made lowercase.
    classdate = models.DateField(db_column='ClassDate')  # Field name made lowercase.
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ParticularClass'


class Schedule(models.Model):
    idschedule = models.IntegerField(db_column='IDSchedule')  # Field name made lowercase.
    iddayoftheweek = models.IntegerField(db_column='IDDayOfTheWeek')  # Field name made lowercase.
    starthour = models.CharField(db_column='StartHour', max_length=5, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    endhour = models.CharField(db_column='EndHour', max_length=5, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Schedule'


class Address(models.Model):
    idaddress = models.IntegerField(db_column='IDAddress')  # Field name made lowercase.
    idlocation = models.IntegerField(db_column='IDLocation')  # Field name made lowercase.
    mainstreet = models.CharField(db_column='MainStreet', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    number = models.CharField(db_column='Number', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    secondstreet = models.CharField(db_column='SecondStreet', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Address'


class Location(models.Model):
    idlocation = models.IntegerField(db_column='IDLocation')  # Field name made lowercase.
    province = models.CharField(db_column='Province', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Location'


class Catechist(models.Model):
    idcatechist = models.IntegerField(db_column='IDCatechist')  # Field name made lowercase.
    iduser = models.IntegerField(db_column='IDUser')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Catechist'


class Catechizing(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    islegitimate = models.BooleanField(db_column='IsLegitimate')  # Field name made lowercase.
    siblingsnumber = models.IntegerField(db_column='SiblingsNumber')  # Field name made lowercase.
    childnumber = models.IntegerField(db_column='ChildNumber')  # Field name made lowercase.
    idschoolclassyear = models.IntegerField(db_column='IDSchoolClassYear')  # Field name made lowercase.
    idclass = models.IntegerField(db_column='IDClass')  # Field name made lowercase.
    payedlevelcourse = models.BooleanField(db_column='PayedLevelCourse')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Catechizing'


class Catechizinggodparent(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    idgodparent = models.IntegerField(db_column='IDGodparent')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CatechizingGodparent'


class Catechizingparent(models.Model):
    idcatechizing = models.IntegerField(db_column='IDCatechizing')  # Field name made lowercase.
    idparent = models.IntegerField(db_column='IDParent')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CatechizingParent'


class Godparent(models.Model):
    idgodparent = models.IntegerField(db_column='IDGodparent')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Godparent'


class Parent(models.Model):
    idparent = models.IntegerField(db_column='IDParent')  # Field name made lowercase.
    ocuppation = models.CharField(db_column='Ocuppation', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Parent'


class Parishpriest(models.Model):
    idparishpriest = models.IntegerField(db_column='IDParishPriest')  # Field name made lowercase.
    iduser = models.IntegerField(db_column='IDUser')  # Field name made lowercase.
    idparish = models.IntegerField(db_column='IDParish')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ParishPriest'


class Person(models.Model):
    idperson = models.IntegerField(db_column='IDPerson')  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    middlename = models.CharField(db_column='MiddleName', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    firstsurname = models.CharField(db_column='FirstSurname', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    secondsurname = models.CharField(db_column='SecondSurname', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    birthdate = models.DateField(db_column='BirthDate')  # Field name made lowercase.
    idbirthlocation = models.IntegerField(db_column='IDBirthLocation')  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=10, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=1, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.
    idaddress = models.IntegerField(db_column='IDAddress')  # Field name made lowercase.
    idphonenumber = models.IntegerField(db_column='IDPhoneNumber')  # Field name made lowercase.
    emailaddress = models.CharField(db_column='EmailAddress', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Person'


class Supportperson(models.Model):
    idsupportperson = models.IntegerField(db_column='IDSupportPerson')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SupportPerson'


class Allergy(models.Model):
    idallergy = models.IntegerField(db_column='IDAllergy')  # Field name made lowercase.
    allergy = models.CharField(db_column='Allergy', max_length=100, db_collation='Modern_Spanish_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Allergy'
