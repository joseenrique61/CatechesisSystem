from wtforms import Form, HiddenField, StringField, validators, FormField, DateField, RadioField, SubmitField, SelectField, TextAreaField, BooleanField, TimeField, IntegerField, PasswordField
from wtforms.fields import EmailField, FieldList
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from flask import session
from app import dal
from app.main.data.mapper import Mappable
from datetime import datetime

class LoginForm(FlaskForm):
    """
    Formulario para iniciar sesión
    """
    Username = StringField('Nombre de usuario', [validators.Length(min=1, max=100)])
    Password = PasswordField('Contraseña', [
            validators.DataRequired(),
            validators.Length(min=1, max=100)])

class UserForm(Form):
    """
    Formulario para registrar un usuario
    """
    Username = StringField('Nombre de usuario', [validators.Length(min=1, max=100)])
    Password = PasswordField('Contraseña', [
            validators.DataRequired(),
            validators.Length(min=1, max=100),
            validators.EqualTo('ConfirmPassword', message='Las contraseñas no coinciden')
        ])
    ConfirmPassword = PasswordField('Confirmar contraseña', [validators.Length(min=1, max=100)])
    Role = StringField("")

    def validate_Password(self, field):
        if field.data:
            field.data = generate_password_hash(field.data)

class LocationForm(Form):
    """
    Formulaio para registrar una ubicación
    """
    Country = StringField('País', [validators.Length(min=1, max=100)])
    Province = StringField('Provincia', [validators.Length(min=1, max=100)])
    State = StringField('Estado', [validators.Length(min=1, max=100)])
    
class AddressForm(Form):
    """
    Formulario para registrar una dirección
    """
    MainStreet = StringField('Calle principal', [validators.Length(min=1, max=100)])
    Number = StringField('Número', [validators.Length(min=1, max=10)])
    SecondStreet = StringField('Calle secundaria', [validators.Length(min=1, max=100)])
    Location: 'LocationForm' = FormField(LocationForm, label='Ubicación')

class PhoneNumberForm(Form):
    """
    Formulario para registrar un número de teléfono 
    """
    PhoneNumber = StringField('Teléfono', [validators.Length(min=10, max=10)])
    PhoneNumberType = SelectField('Tipo de teléfono')

    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.PhoneNumberType.choices = [phone_type.PhoneNumberType for phone_type in dal.get_all_phone_number_types()]

class PersonForm(Form):
    """
    Formulario parar registrar una persona
    """
    FirstName = StringField('Primer nombre', [validators.Length(min=1, max=100)])
    MiddleName = StringField('Segundo nombre', [validators.Length(min=1, max=100)])
    FirstSurname = StringField('Primer apellido', [validators.Length(min=1, max=100)])
    SecondSurname = StringField('Segundo Apellido', [validators.Length(min=1, max=100)])
    BirthDate = DateField('Fecha de nacimiento', format='%Y-%m-%d', validators=[validators.DataRequired()])
    BirthLocation = FormField(LocationForm, label='Lugar de nacimiento')
    DNI = StringField('Cédula', [validators.Length(min=10, max=10)])
    Gender = RadioField('Género', choices=[('M', 'Masculino'), ('F', 'Femenino')], default="M")
    Address = FormField(AddressForm, label='Dirección de vivienda')
    PhoneNumber = FormField(PhoneNumberForm, label="Número de teléfono")
    EmailAddress = EmailField('Correo electrónico', [validators.Length(min=1, max=100)])

class ClassroomForm(Form):
    """
    Formulario para registrar un aula de clases
    """
    ClassroomName = StringField("Nombre del aula", [validators.Length(min=1, max=20)])

class ParishForm(FlaskForm):
    """
    Formulario para registrar una parroquia
    """
    Name = StringField('Nombre de la parroquia', [validators.Length(min=1, max=100)])
    LogoImage = FileField('Logo', render_kw={'accept': 'image/png, image/jpeg, image/jpg'}, validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    Address = FormField(AddressForm, label='Dirección')
    Classroom = FieldList(FormField(ClassroomForm), min_entries=1, label='Aulas')
    Submit = SubmitField('Registrar')

# --- Update forms ---
class PersonUpdateForm(Form):
    """
    Formulario para actualizar datos de una persona.
    """
    EmailAddress = EmailField('Correo Electrónico', [validators.DataRequired(), validators.Email()])
    Address = FormField(AddressForm, label='Dirección de Vivienda')
    PhoneNumber = FormField(PhoneNumberForm, label="Número de Teléfono")
    FirstName = HiddenField()
    FirstSurname = HiddenField()
    DNI = HiddenField()

class SchoolForm(Form):
    """
    Formulario para actualizar la información escolar de un catequizando.
    """
    SchoolYear = StringField('Año Escolar/Grado', [DataRequired(), validators.Length(max=20)])
    SchoolName = StringField('Nombre de la Institución Educativa', [validators.DataRequired(), validators.Length(max=100)])

class ParentForm(Form):
    """
    Formulario para registrar al/a los tutores de un catequizando.
    """
    Person: 'PersonForm' = FormField(PersonForm)
    Ocuppation = StringField('Ocupación', [validators.DataRequired(), Length(max=100)])

class GodparentForm(Form):
    """
    Formulario para registrar al/a los padrinos de un catequizando.
    """
    Person: 'PersonForm' = FormField(PersonForm)

class HealthInformationForm(Form):
    """
    Formulario para registrar la información de salud de un catequizando
    """
    ImportantAspects = TextAreaField('Aspectos Importantes de Salud', [validators.DataRequired()])
    BloodType = SelectField('Tipo de Sangre', [validators.Optional()], choices=[])
    
    Allergy = FieldList(StringField('Alergia', [validators.Length(max=100)]), label='Alergias', min_entries=0)
    
    EmergencyContact = SelectField('Contacto de Emergencia', [validators.Optional()], coerce=str)
    RegisterNewContact = BooleanField('Registrar un nuevo contacto de emergencia', default=False)
    NewEmergencyContact = FormField(PersonForm, label='Datos del Nuevo Contacto')

    def __init__(self, *args, **kwargs):
        super(HealthInformationForm, self).__init__(*args, **kwargs)
        
        blood_types = dal.get_all_blood_types()
        self.BloodType.choices = [('', '--- Seleccione ---')] + [(bt.Type, bt.Type) for bt in blood_types]
        self.EmergencyContact.choices = [('', '--- Seleccione de la lista o registre uno nuevo ---')]

class ScheduleForm(Form):
    """
    Formulario para registrar 
    """
    DayOfTheWeek = SelectField('Día de la semana', [validators.DataRequired()], choices=[])
    StartHour = TimeField('Hora de inicio', [validators.DataRequired()], format='%H:%M')
    EndHour = TimeField('Hora de fin', [validators.DataRequired()], format='%H:%M')
    Classroom = SelectField('Aula', [validators.DataRequired()], coerce=str)

    def __init__(self, parish_id, *args, **kwargs):
        from app import dal # Importación local
        super(ScheduleForm, self).__init__(*args, **kwargs)
        
        days = dal.get_all_day_of_the_week()
        classrooms = dal.get_classrooms_by_parish(parish_id)

        self.DayOfTheWeek.choices = [('', '---')] + [(day.DayOfTheWeek, day.DayOfTheWeek) for day in days]
        self.Classroom.choices = [('', '---')] + [(cr.id, cr.ClassroomName) for cr in classrooms]

class CatechizingForm(FlaskForm):
    # 1. Información Personal
    Person = FormField(PersonForm, 'Datos Personales del Catequizando')
    
    # 2. Información Adicional
    IsLegitimate = BooleanField('¿Es Hijo(a) Legítimo(a)?', default=False)
    SiblingsNumber = IntegerField('Número de Hermanos', validators=[DataRequired(), NumberRange(min=0)])
    ChildNumber = IntegerField('Lugar que Ocupa entre los Hermanos', validators=[DataRequired(), NumberRange(min=1)])
    DataSheetInformation = TextAreaField('Observaciones Adicionales', validators=[Optional()])
    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)
    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)

    # 3. Información Escolar
    School = FormField(SchoolForm, label='Información Scolar')
    Class = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=str)
    
    # 4. Información Familiar
    Parent = FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2)
    Godparent = FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=1, max_entries=2)

    # 5. Información Estado de Salud
    HealthInformation = FormField(HealthInformationForm, 'Información de Salud')

    Submit = SubmitField('Registrar Catequizando')
    
    def __init__(self, *args, **kwargs):
        super(CatechizingForm, self).__init__(*args, **kwargs)
        priest_dto = dal.get_parish_priest_by_id(session["id"])
        if priest_dto and priest_dto.Parish:
            classes = dal.get_classes_by_parish_id(priest_dto.Parish.id)
            self.Class.choices = [(c.id, f"{c.Level.Name}: {c.Schedule.DayOfTheWeek if c.Schedule else '' } ( {c.Schedule.StartHour} - {c.Schedule.EndHour}) ") for c in classes]

class ClassForm(FlaskForm):
    ClassPeriod = SelectField('Periodo de Clases', [validators.DataRequired()], coerce=str)
    Level = SelectField('Nivel de Catecismo', [validators.DataRequired()], coerce=str)
    Catechist = SelectField('Catequista Encargado', [validators.DataRequired()], coerce=str)
    SupportPerson = SelectField('Persona de Soporte', [validators.Optional()], coerce=str)
    Schedule = FormField(ScheduleForm, label='Horario')
    Submit = SubmitField('Registrar Clase')

    def __init__(self, *args, **kwargs):
        from app import dal
        super(ClassForm, self).__init__(*args, **kwargs)
        priest_dto = dal.get_dto_by_user(session.get("username"))
        parish_id = None
        if priest_dto and hasattr(priest_dto, 'Parish') and priest_dto.Parish:
            parish_id = priest_dto.Parish.id

        if parish_id:
            # Poblar los selects
            periods = dal.get_all_periods()
            levels = dal.get_all_levels()
            catechists = dal.get_catechists_by_parish_id(parish_id, include=["Person"])
            support_persons = dal.get_support_persons_by_parish_id(parish_id, include=["Person"])

            self.ClassPeriod.choices = [('', '---')] + [(p.id, str(p)) for p in periods]
            self.Level.choices = [('', '---')] + [(lvl.id, lvl.Name) for lvl in levels]
            self.Catechist.choices = [('', '---')] + [(c.id, f"{c.Person.FirstName} {c.Person.FirstSurname}") for c in catechists]
            self.SupportPerson.choices = [('', '---'), (None, 'No Asignado')] + [(sp.id, f"{sp.Person.FirstName} {sp.Person.FirstSurname}") for sp in support_persons]
            
            # Pasar el parish_id al subformulario de horario
            self.Schedule.form = ScheduleForm(parish_id=parish_id, **(kwargs.get('Schedule') or {}))

class CatechistForm(FlaskForm):
    User = FormField(UserForm, label='Datos de usuario')
    Person = FormField(PersonForm, label='Datos del catequista')
    Submit = SubmitField('Registrar catequista')

class SupportPersonForm(FlaskForm):
    Person = FormField(PersonForm, label='Datos de la persona de soporte')
    Submit = SubmitField('Registrar persona de soporte')

# --- Update forms ---

class HealthInformationUpdateForm(Form):
    ImportantAspects = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
    Allergy = FieldList(StringField('Alergia', [validators.Length(max=100)]), 'Alergias', min_entries=0)
    BloodType = HiddenField(SelectField('Tipo de Sangre', validators=[DataRequired()], choices=[]))

    EmergencyContact = SelectField('Contacto de Emergencia', [validators.Optional()], coerce=str)
    RegisterNewContact = BooleanField('Registrar un nuevo contacto de emergencia', default=False)
    NewEmergencyContact = FormField(PersonForm, label='Datos del Nuevo Contacto')

    def __init__(self, *args, **kwargs):
        super(HealthInformationUpdateForm, self).__init__(*args, **kwargs)
        self.BloodType.choices = [(item.Type, item.Type) for item in dal.get_all_blood_types()]
        self.EmergencyContact.choices = [('', '--- Seleccione de la lista o registre uno nuevo ---')]

class CatechizingUpdateForm(FlaskForm):
    # 1. Información Personal
    Person = FormField(PersonUpdateForm, 'Datos Personales del Catequizando')
    DataSheetInformation = TextAreaField('Observaciones Adicionales (Ficha)', validators=[Optional()])
    
    # 2. Información Adicional
    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)
    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)
    
    # 3. Información Escolar
    School = FormField(SchoolForm, 'Información Escolar')   
    Class = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=str)
    
    # 4. Información Estado de Salud
    HealthInformation = FormField(HealthInformationUpdateForm, 'Información de Salud')
    
    # 5. Información que no se puede editar
    IsLegitimate = HiddenField()
    SiblingsNumber = HiddenField()
    ChildNumber = HiddenField()
    Parent = HiddenField()
    Godparent = HiddenField()
    
    Submit = SubmitField('Actualizar Catequizando')
    
    def __init__(self, *args, **kwargs):
            super(CatechizingUpdateForm, self).__init__(*args, **kwargs)

            priest_dto = dal.get_parish_priest_by_id(session["id"])
            if priest_dto and priest_dto.Parish:
                classes = dal.get_classes_by_parish_id(priest_dto.Parish.id)
                self.Class.choices = [(c.id, f"{c.Level.Name}: {c.Schedule.DayOfTheWeek if c.Schedule else '' } ( {c.Schedule.StartHour} - {c.Schedule.EndHour} ) ") for c in classes]

class ParishPriestForm(FlaskForm):
    User = FormField(UserForm, label='Datos de usuario')
    Person = FormField(PersonForm, label='Datos personales')
    Parish = SelectField('Parroquia', coerce=str, choices=[])
    Submit = SubmitField('Registrar')

    def __init__(self, *args, **kwargs):
        super(ParishPriestForm, self).__init__(*args, **kwargs)
        self.Parish.choices = [(parish.id, parish.Name) for parish in dal.get_all_parishes()]


# # Otra versión HealthUpdateForm
# class HealthInformationUpdateForm(Form):
#     ImportantAspects = TextAreaField('Aspectos Importantes de Salud', validators=[Optional()])
#     Allergy = FieldList(StringField('Alergia', [validators.Length(max=100)]), 'Alergias', min_entries=0)
    
#     # CORRECCIÓN CRÍTICA: Decidimos que NO se puede editar en este form, así que solo usamos HiddenField.
#     # Si se quisiera editar, se usaría SelectField() en su lugar.
#     BloodType = HiddenField()

#     # Mantenemos la lógica para actualizar/cambiar el contacto de emergencia.
#     EmergencyContact = SelectField('Contacto de Emergencia', [validators.Optional()], coerce=str)
#     RegisterNewContact = BooleanField('Registrar un nuevo contacto de emergencia', default=False)
#     NewEmergencyContact = FormField(PersonForm, label='Datos del Nuevo Contacto')