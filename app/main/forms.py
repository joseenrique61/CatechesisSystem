from wtforms import Form, HiddenField, StringField, validators, FormField, DateField, RadioField, SubmitField, SelectField, FieldList
from wtforms.fields import EmailField
from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf import FlaskForm
from app import dal
from app.main.data.mapper import Mappable
from datetime import datetime

class LocationForm(Form):
    Country: str = StringField('País', [validators.Length(min=1, max=100)])
    Province: str = StringField('Provincia', [validators.Length(min=1, max=100)])
    State: str = StringField('Estado', [validators.Length(min=1, max=100)])
    
class AddressForm(Form):
    MainStreet: str = StringField('Calle principal', [validators.Length(min=1, max=100)])
    Number: str = StringField('Número', [validators.Length(min=1, max=10)])
    SecondStreet: str = StringField('Calle secundaria', [validators.Length(min=1, max=100)])
    Location: 'LocationForm' = FormField(LocationForm, label='Ubicación')

class PhoneNumberTypeForm(Form):
    PhoneNumberType = SelectField('Tipo de teléfono')

    def __init__(self, *args, **kwargs):
        super(PhoneNumberTypeForm, self).__init__(*args, **kwargs)
        self.PhoneNumberType.choices = [phone_type.PhoneNumberType for phone_type in dal.get_all_phone_number_types()]
    
class PhoneNumberForm(Form):
    PhoneNumber = StringField('Teléfono', [validators.Length(min=1, max=15)])
    PhoneNumberType = FormField(PhoneNumberTypeForm, label="Tipo de teléfono")

class PersonForm(Form):
    FirstName = StringField('Primer nombre', [validators.Length(min=1, max=100)])
    MiddleName = StringField('Segundo nombre', [validators.Length(min=1, max=100)])
    FirstSurname = StringField('Primer apellido', [validators.Length(min=1, max=100)])
    SecondSurname = StringField('Segundo Apellido', [validators.Length(min=1, max=100)])
    BirthDate = DateField('Fecha de nacimiento', format='%Y-%m-%d', validators=[validators.DataRequired()])
    BirthLocation = FormField(LocationForm, label='Lugar de nacimiento')
    DNI = StringField('Cédula', [validators.Length(min=1, max=10)])
    Gender = RadioField('Género', choices=[('M', 'Masculino'), ('F', 'Femenino')], default="M")
    Address = FormField(AddressForm, label='Dirección de vivienda')
    PhoneNumber = FormField(PhoneNumberForm, label="Número de teléfono")
    EmailAddress = EmailField('Correo electrónico', [validators.Length(min=1, max=100)])

class ClassroomForm(Form):
    ClassroomName = StringField("Nombre del aula", [validators.Length(min=1, max=5)])

class ParishForm(FlaskForm):
    Name = StringField('Nombre de la parroquia', [validators.Length(min=1, max=100)])
    LogoImage = FileField('Logo', render_kw={'accept': 'image/png, image/jpeg, image/jpg'}, validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])
    Address = FormField(AddressForm, label='Dirección')
    Classroom = FieldList(FormField(ClassroomForm), min_entries=1, label='Aulas')
    Submit = SubmitField('Registrar')


# --- Update forms ---

class UpdateFormBase(Form, Mappable):
    pass

class PersonUpdateForm(UpdateFormBase):
    FirstName: str = HiddenField(StringField('Primer nombre', [validators.Length(min=1, max=100)]))
    MiddleName: str = HiddenField(StringField('Segundo nombre', [validators.Length(min=1, max=100)]))
    FirstSurname: str = HiddenField(StringField('Primer apellido', [validators.Length(min=1, max=100)]))
    SecondSurname: str = HiddenField(StringField('Segundo Apellido', [validators.Length(min=1, max=100)]))
    # BirthDate = HiddenField("", validators=[validators.DataRequired()])
    BirthLocation: 'LocationForm' = HiddenField(FormField(LocationForm, label='Lugar de nacimiento'))
    DNI: str = HiddenField(StringField('Cédula', [validators.Length(min=1, max=10)]))
    Gender: str = HiddenField(RadioField('Género', choices=[('M', 'Masculino'), ('F', 'Femenino')]))
    Address: 'AddressForm' = FormField(AddressForm, label='Dirección de vivienda')
    PhoneNumber: str = FormField(PhoneNumberForm, label="Número de teléfono")
    EmailAddress: str = EmailField('Correo electrónico', [validators.Length(min=1, max=100)])