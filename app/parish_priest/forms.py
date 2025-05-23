from wtforms import FieldList, IntegerField, StringField, TimeField, SelectField, BooleanField, FormField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf import FlaskForm
from flask import session
from app.main.forms import PersonForm
from app import dal

class SchoolClassYearForm(FlaskForm):
    SchoolYear = StringField('Año Escolar', validators=[DataRequired(), Length(max=10)])
    IDSchool = SelectField('Escuela', validators=[DataRequired()], choices=[], coerce=int)

class AllergyForm(FlaskForm):
    Allergy = StringField('Alergia', validators=[DataRequired(), Length(max=100)])

class ParentForm(FlaskForm):
    Person = FormField(PersonForm)
    Occupation = StringField('Ocupación', validators=[DataRequired(), Length(max=100)])

class GodparentForm(FlaskForm):
    Person = FormField(PersonForm)

class HealthInformationForm(FlaskForm):
    ImportantAspects = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
    Allergies = FieldList(FormField(AllergyForm), 'Alergias', min_entries=0)
    IDBloodType = SelectField('Tipo de Sangre', validators=[DataRequired()], choices=[], coerce=int)
    EmergencyContact = FormField(PersonForm, 'Contacto de Emergencia')

# --- Formulario Principal ---

class CatechizingForm(FlaskForm):
    Person = FormField(PersonForm, 'Datos Personales del Catequizando')
    IsLegitimate = BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False)
    SiblingsNumber = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber = IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)])

    SchoolClassYear = FormField(SchoolClassYearForm, 'Información Escolar')

    IDClass = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=int)

    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)

    Parents = FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2) # Al menos un padre/tutor
    Godparents = FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=0, max_entries=2) # Padrinos pueden ser opcionales inicialmente

    HealthInformation = FormField(HealthInformationForm, 'Información de Salud')

    # DataSheetCreateDTO se representa como un solo campo de texto
    DataSheetInformation = TextAreaField('Información Adicional (Ficha)', validators=[Optional()])

    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)

    # Podrías añadir un botón de envío aquí o en la plantilla
    Submit = SubmitField('Registrar Catequizando')

class ScheduleForm(FlaskForm):
    IDDayOfTheWeek = SelectField('Día de la semana', coerce=int)
    StartHour = TimeField('Hora de inicio')
    EndHour = TimeField('Hora de fin')
    IDClassroom = SelectField('Aula')

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.IDDayOfTheWeek.choices = [(item.IDDayOfTheWeek, item.DayOfTheWeek) for item in dal.get_all_day_of_the_week()]
        # self.IDClassroom.choices = [(item.IDClassroom, item.ClassroomName) for item in dal.get_classroom_in_parish(dal.get_parish_priest_by_id(session.get("id")).IDParish)]
        self.IDClassroom.choices = [(item.IDClassroom, item.ClassroomName) for item in dal.get_classroom_in_parish(dal.get_parish_priest_by_id(37).IDParish)]

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
        self.IDCatechist.choices = [(item.IDCatechist, f"{item.Person.FirstName} {item.Person.FirstSurname}") for item in dal.get_all_catechists()]
        self.IDSupportPerson.choices = [(item.IDSupportPerson, f"{item.Person.FirstName} {item.Person.FirstSurname}") for item in dal.get_all_support_person()]
        