from wtforms import Form, FieldList, IntegerField, HiddenField, StringField, TimeField, SelectField, BooleanField, FormField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf import FlaskForm
from flask import session
from app.main.forms import PersonForm, PersonUpdateForm, AddressForm
from app.auth.forms import UserForm
from app import dal

class SchoolForm(Form):
    SchoolName = StringField('Nombre de la escuela', validators=[DataRequired(), Length(max=50)])

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
    
    # FIX: El campo ahora se llama como en el DTO y no fuerza a 'int'.
    BloodType = SelectField('Tipo de Sangre')
    
    EmergencyContact = FormField(PersonForm, 'Contacto de Emergencia')

    def __init__(self, *args, **kwargs):
        super(HealthInformationForm, self).__init__(*args, **kwargs)
        # FIX: Las opciones ahora usan el valor de string directamente.
        self.BloodType.choices = [(bt) for bt in dal.get_all_blood_types()]

# --- Formulario Principal ---
class DataSheetForm(Form):
    DataSheetInformation: str = TextAreaField('Información Adicional (Ficha)', validators=[Optional()])

class CatechizingForm(FlaskForm):
    Person = FormField(PersonForm, 'Datos Personales del Catequizando')
    IsLegitimate = BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False)
    SiblingsNumber = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber = IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)])
    SchoolClassYear = FormField(SchoolClassYearForm, 'Información Escolar')

    # FIX: Campo renombrado de 'Class' a 'Class' y se elimina 'coerce=int'.
    Class = SelectField('Clase Asignada', validators=[DataRequired()], choices=[])

    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)
    Parent = FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2)
    Godparent = FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=1, max_entries=2)
    HealthInformation = FormField(HealthInformationForm, 'Información de Salud')
    DataSheet = FormField(DataSheetForm, label="Hoja de datos")
    Submit = SubmitField('Registrar Catequizando')

    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)

    def __init__(self, *args, **kwargs):
        super(CatechizingForm, self).__init__(*args, **kwargs)
        # FIX: Se pueblan las opciones del campo 'Class' usando el 'item.id' (string) como valor.
        priest_dto = dal.get_parish_priest_by_id(session["id"])
        if priest_dto and priest_dto.Parish:
            classes = dal.get_classes_by_parish_id(priest_dto.Parish.id)
            self.Class.choices = [(c.id, f"{c.Level.Name}: {c.Schedule.DayOfTheWeek if c.Schedule else '' } ( {c.Schedule.StartHour} - {c.Schedule.EndHour}) ") for c in classes]

class ScheduleForm(Form):
    DayOfTheWeek = SelectField('Día de la semana', coerce=int)
    StartHour = TimeField('Hora de inicio')
    EndHour = TimeField('Hora de fin')
    Classroom = SelectField('Aula')

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.DayOfTheWeek.choices = [(item.DayOfTheWeek, item.DayOfTheWeek) for item in dal.get_all_day_of_the_week()]
        self.Classroom.choices = [(item.Classroom, item.ClassroomName) for item in dal.get_classroom_in_parish(dal.get_parish_priest_by_id(session["id"]).Parish)]
    
    def validate_StartHour(self, field):
        if field.data:
            field.data = f"{'0' if field.data.hour < 10 else ''}{field.data.hour}:{field.data.minute}"

    def validate_EndHour(self, field):
        if field.data:
            field.data = f"{'0' if field.data.hour < 10 else ''}{field.data.hour}:{field.data.minute}"

class ClassForm(FlaskForm):
    # FIX: Campos renombrados para coincidir con DTOs y sin coerce=int
    ClassPeriod = SelectField('Periodo de clases')
    Level = SelectField('Nivel de catecismo')
    Catechist = SelectField('Catequista encargado')
    SupportPerson = SelectField('Persona de soporte', validators=[Optional()])
    Schedule = FieldList(FormField(ScheduleForm), min_entries=1, label='Horario')
    Submit = SubmitField('Registrar clase')

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        # FIX: Poblando choices con el 'id' string de los DTOs
        self.ClassPeriod.choices = [("", "Seleccione...")] + [(item.id, str(item)) for item in dal.get_all_periods()]
        self.Level.choices = [("", "Seleccione...")] + [(item.id, item.Name) for item in dal.get_all_levels()]
        
        priest_dto = dal.get_parish_priest_by_id(session.get("id"))
        if priest_dto and priest_dto.Parish:
            parish_id = priest_dto.Parish.id
            catechists = dal.get_catechists_by_parish_id(parish_id, include=["Person"])
            support_persons = dal.get_support_persons_by_parish_id(parish_id, include=["Person"])
            
            # FIX: Usar el 'id' del DTO, no un atributo inexistente
            self.Catechist.choices = [("", "Seleccione...")] + [(c.id, f"{c.Person.FirstName} {c.Person.FirstSurname}") for c in catechists]
            self.SupportPerson.choices = [("", "Seleccione...")] + [(sp.id, f"{sp.Person.FirstName} {sp.Person.FirstSurname}") for sp in support_persons]


class CatechistForm(FlaskForm):
    User = FormField(UserForm, label='Datos de usuario')
    Person = FormField(PersonForm, label='Datos del catequista')
    Submit = SubmitField('Registrar catequista')

class SupportPersonForm(FlaskForm):
    Person = FormField(PersonForm, label='Datos de la persona de soporte')
    Submit = SubmitField('Registrar persona de soporte')

# --- Update forms ---

class HealthInformationUpdateForm(Form):
    ImportantAspects: str = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
    Allergy: list['AllergyForm'] = FieldList(FormField(AllergyForm), 'Alergias', min_entries=1)
    BloodType: str = HiddenField(SelectField('Tipo de Sangre', validators=[DataRequired()], choices=[]))
    # BloodType: RadioField('Género', choices=[('M', 'Masculino'), ('F', 'Femenino')], default="M")
    EmergencyContact: 'PersonForm' = FormField(PersonForm, 'Contacto de Emergencia')

    def __init__(self, *args, **kwargs):
        super(HealthInformationUpdateForm, self).__init__(*args, **kwargs)
        # self.BloodType.choices = [(item.BloodType, item.BloodType) for item in dal.get_all_blood_types()]
        self.BloodType.choices = [(bt) for bt in dal.get_all_blood_types()]

class CatechizingUpdateForm(FlaskForm):
    
    Person: 'PersonUpdateForm' = FormField(PersonUpdateForm, 'Datos Personales del Catequizando')
    IsLegitimate: bool = HiddenField(BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False))
    SiblingsNumber: int = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber: int = HiddenField(IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)]))

    SchoolClassYear: 'SchoolClassYearForm' = FormField(SchoolClassYearForm, 'Información Escolar')

    Class: int = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=int)

    PayedLevelCourse: bool = BooleanField('¿Curso de Nivel Pagado?', default=False)

    Parent: list['ParentForm'] = HiddenField(FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2)) # Al menos un padre/tutor
    Godparent: list['GodparentForm'] = HiddenField(FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=0, max_entries=2)) # Padrinos pueden ser opcionales inicialmente

    HealthInformation: 'HealthInformationUpdateForm' = FormField(HealthInformationUpdateForm, 'Información de Salud')

    DataSheet: 'DataSheetForm' = FormField(DataSheetForm, label="Hoja de datos")
    
    HasParticularClass: bool = HiddenField(BooleanField('¿Tomó clases particulares?', default=False))

    # Podrías añadir un botón de envío aquí o en la plantilla
    Submit = SubmitField('Actualizar Catequizando')

    def __init__(self, *args, **kwargs):
            super(CatechizingForm, self).__init__(*args, **kwargs)
            # FIX: Se pueblan las opciones del campo 'Class' usando el 'item.id' (string) como valor.
            priest_dto = dal.get_parish_priest_by_id(session["id"])
            if priest_dto and priest_dto.Parish:
                classes = dal.get_classes_by_parish_id(priest_dto.Parish.id)
                self.Class.choices = [(c.id, f"{c.Level.Name}: {c.Schedule.DayOfTheWeek if c.Schedule else '' } ( {c.Schedule.StartHour} - {c.Schedule.EndHour} ) ") for c in classes]
