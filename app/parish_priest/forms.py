from wtforms import Form, FieldList, IntegerField, HiddenField, StringField, TimeField, SelectField, BooleanField, FormField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf import FlaskForm
from flask import session
from app.main.forms import PersonForm, PersonUpdateForm, AddressForm, UpdateFormBase
from app.auth.forms import UserForm
from app import dal

class SchoolForm(Form):
    SchoolName = StringField('Nombre de la escuela', validators=[DataRequired(), Length(max=50)])
    Address = FormField(AddressForm, label='Dirección del colegio')

class SchoolClassYearForm(Form):
    SchoolYear: str = StringField('Año Escolar', validators=[DataRequired(), Length(max=10)])
    School: 'SchoolForm' = FormField(SchoolForm, label='Información del colegio')

class AllergyForm(Form):
    Allergy: str = StringField('Alergia', validators=[DataRequired(), Length(max=100)])

class ParentForm(Form):
    Person: 'PersonForm' = FormField(PersonForm)
    Ocuppation: str = StringField('Ocupación', validators=[DataRequired(), Length(max=100)])

class GodparentForm(Form):
    Person: 'PersonForm' = FormField(PersonForm)

class HealthInformationForm(Form):
    ImportantAspects = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
    Allergy = FieldList(FormField(AllergyForm), 'Alergias', min_entries=1)
    IDBloodType = SelectField('Tipo de Sangre', validators=[DataRequired()], choices=[], coerce=int)
    EmergencyContact = FormField(PersonForm, 'Contacto de Emergencia')

    def __init__(self, *args, **kwargs):
        super(HealthInformationForm, self).__init__(*args, **kwargs)
        self.IDBloodType.choices = [(item.IDBloodType, item.BloodType) for item in dal.get_all_blood_types()]

# --- Formulario Principal ---
class DataSheetForm(Form):
    DataSheetInformation: str = TextAreaField('Información Adicional (Ficha)', validators=[Optional()])

class CatechizingForm(FlaskForm):
    Person = FormField(PersonForm, 'Datos Personales del Catequizando')
    IsLegitimate = BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False)
    SiblingsNumber = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber = IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)])

    SchoolClassYear = FormField(SchoolClassYearForm, 'Información Escolar')

    IDClass = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=int)

    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)

    Parent = FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2) # Al menos un padre/tutor
    Godparent = FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=1, max_entries=2) # Padrinos pueden ser opcionales inicialmente

    HealthInformation = FormField(HealthInformationForm, 'Información de Salud')

    # DataSheetCreateDTO se representa como un solo campo de texto
    DataSheet = FormField(DataSheetForm, label="Hoja de datos")

    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)

    # Podrías añadir un botón de envío aquí o en la plantilla
    Submit = SubmitField('Registrar Catequizando')

    def __init__(self, *args, **kwargs):
        super(CatechizingForm, self).__init__(*args, **kwargs)
        # TODO: Change when the login is working
        self.IDClass.choices = [(item.IDClass, f"{item.Level.Name}: {', '.join([sch.DayOfTheWeek.DayOfTheWeek + ': ' + sch.StartHour + ' - ' + sch.EndHour for sch in item.Schedule])}") for item in dal.get_classes_by_parish_id(dal.get_parish_priest_by_id(2).IDParish)]

class ScheduleForm(Form):
    IDDayOfTheWeek = SelectField('Día de la semana', coerce=int)
    StartHour = TimeField('Hora de inicio')
    EndHour = TimeField('Hora de fin')
    IDClassroom = SelectField('Aula')

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.IDDayOfTheWeek.choices = [(item.IDDayOfTheWeek, item.DayOfTheWeek) for item in dal.get_all_day_of_the_week()]
        # self.IDClassroom.choices = [(item.IDClassroom, item.ClassroomName) for item in dal.get_classroom_in_parish(dal.get_parish_priest_by_id(session.get("id")).IDParish)]
        # TODO: Change when the login is working
        self.IDClassroom.choices = [(item.IDClassroom, item.ClassroomName) for item in dal.get_classroom_in_parish(dal.get_parish_priest_by_id(2).IDParish)]
    
    def validate_StartHour(self, field):
        if field.data:
            field.data = f"{'0' if field.data.hour < 10 else ''}{field.data.hour}:{field.data.minute}"

    def validate_EndHour(self, field):
        if field.data:
            field.data = f"{'0' if field.data.hour < 10 else ''}{field.data.hour}:{field.data.minute}"

class ClassForm(FlaskForm):
    IDClassPeriod = SelectField('Periodo de clases', coerce=int)
    IDLevel = SelectField('Nivel de catecismo', coerce=int)
    IDCatechist = SelectField('Catequista encargado', coerce=int)
    IDSupportPerson = SelectField('Persona de soporte', coerce=int)
    Schedule = FieldList(FormField(ScheduleForm), min_entries=1, label='Horario')
    Submit = SubmitField('Registrar clase')

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        self.IDClassPeriod.choices = [(item.IDClassPeriod, str(item)) for item in dal.get_all_periods()]
        self.IDLevel.choices = [(item.IDLevel, item.Name) for item in dal.get_all_levels()]
        
        catechists = dal.get_all_catechists()
        if catechists:
            self.IDCatechist.choices = []
            for catechist in catechists:
                self.IDCatechist.choices.append((catechist.IDCatechist, f"{catechist.Person.FirstName} {catechist.Person.FirstSurname}"))

        support_persons = dal.get_all_support_person()
        if support_persons:
            self.IDSupportPerson.choices = []
            for support_person in support_persons:
                self.IDSupportPerson.choices.append((support_person.IDSupportPerson, f"{support_person.Person.FirstName} {support_person.Person.FirstSurname}"))

class CatechistForm(FlaskForm):
    User = FormField(UserForm, label='Datos de usuario')
    Person = FormField(PersonForm, label='Datos del catequista')
    Submit = SubmitField('Registrar catequista')

class SupportPersonForm(FlaskForm):
    Person = FormField(PersonForm, label='Datos de la persona de soporte')
    Submit = SubmitField('Registrar persona de soporte')
        

# --- Update forms ---

class HealthInformationUpdateForm(UpdateFormBase):
    ImportantAspects: str = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
    Allergy: list['AllergyForm'] = FieldList(FormField(AllergyForm), 'Alergias', min_entries=1)
    IDBloodType: int = HiddenField(SelectField('Tipo de Sangre', validators=[DataRequired()], choices=[], coerce=int))
    EmergencyContact: 'PersonForm' = FormField(PersonForm, 'Contacto de Emergencia')

    def __init__(self, *args, **kwargs):
        super(HealthInformationUpdateForm, self).__init__(*args, **kwargs)
        self.IDBloodType.choices = [(item.IDBloodType, item.BloodType) for item in dal.get_all_blood_types()]

class CatechizingUpdateForm(UpdateFormBase):
    Person: 'PersonUpdateForm' = FormField(PersonUpdateForm, 'Datos Personales del Catequizando')
    IsLegitimate: bool = HiddenField(BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False))
    SiblingsNumber: int = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber: int = HiddenField(IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)]))

    SchoolClassYear: 'SchoolClassYearForm' = FormField(SchoolClassYearForm, 'Información Escolar')

    IDClass: int = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=int)

    PayedLevelCourse: bool = BooleanField('¿Curso de Nivel Pagado?', default=False)

    Parent: list['ParentForm'] = HiddenField(FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2)) # Al menos un padre/tutor
    Godparent: list['GodparentForm'] = HiddenField(FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=0, max_entries=2)) # Padrinos pueden ser opcionales inicialmente

    HealthInformation: 'HealthInformationUpdateForm' = FormField(HealthInformationUpdateForm, 'Información de Salud')

    # DataSheetCreateDTO se representa como un solo campo de texto
    DataSheet: 'DataSheetForm' = FormField(DataSheetForm, label="Hoja de datos")

    HasParticularClass: bool = HiddenField(BooleanField('¿Tomó clases particulares?', default=False))

    # Podrías añadir un botón de envío aquí o en la plantilla
    Submit = SubmitField('Actualizar Catequizando')

    def __init__(self, *args, **kwargs):
        super(CatechizingUpdateForm, self).__init__(*args, **kwargs)
        # TODO: Change when the login is working
        self.IDClass.choices = [(item.IDClass, f"{item.Level.Name}: {', '.join([sch.DayOfTheWeek.DayOfTheWeek + ': ' + sch.StartHour + ' - ' + sch.EndHour for sch in item.Schedule])}") for item in dal.get_classes_by_parish_id(dal.get_parish_priest_by_id(2).IDParish)]