from wtforms import FieldList, IntegerField, StringField, DateField, SelectField, BooleanField, FormField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf import FlaskForm
from app.main.forms import PersonForm

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

    # IDClass: ID de la clase existente. Esto sería un SelectField
    IDClass = SelectField('Clase Asignada', validators=[DataRequired()], choices=[], coerce=int)

    PayedLevelCourse = BooleanField('¿Curso de Nivel Pagado?', default=False)

    Parents = FieldList(FormField(ParentForm), 'Padres/Tutores', min_entries=1, max_entries=2) # Al menos un padre/tutor
    Godparents = FieldList(FormField(GodparentForm), 'Padrinos/Madrinas', min_entries=0, max_entries=2) # Padrinos pueden ser opcionales inicialmente

    HealthInformation = FormField(HealthInformationForm, 'Información de Salud')

    # DataSheetCreateDTO se representa como un solo campo de texto
    DataSheetInformation = TextAreaField('Información Adicional (Ficha)', validators=[Optional()])

    # ParticularClass = FormField(ParticularClassForm, 'Clase Particular (Opcional)', validators=[Optional()])
    HasParticularClass = BooleanField('¿Tomó clases particulares?', default=False)

    # Podrías añadir un botón de envío aquí o en la plantilla
    Submit = SubmitField('Registrar Catequizando')