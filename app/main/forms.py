from wtforms import Form, StringField, validators, FormField, DateField, RadioField, FileField, SubmitField, SelectField
from wtforms.fields import EmailField
from app.main.models import PhoneNumberType

class LocationForm(Form):
    Country = StringField('País', [validators.Length(min=1, max=100)])
    Province = StringField('Provincia', [validators.Length(min=1, max=100)])
    State = StringField('Estado', [validators.Length(min=1, max=100)])
    
class AddressForm(Form):
    MainStreet = StringField('Calle principal', [validators.Length(min=1, max=100)])
    Number = StringField('Número', [validators.Length(min=1, max=10)])
    SecondStreet = StringField('Calle secundaria', [validators.Length(min=1, max=100)])
    Location = FormField(LocationForm, label='Ubicación')

class PersonForm(Form):
    FirstName = StringField('Primer nombre', [validators.Length(min=1, max=100)])
    MiddleName = StringField('Segundo nombre', [validators.Length(min=1, max=100)])
    FirstSurname = StringField('Primer apellido', [validators.Length(min=1, max=100)])
    SecondSurname = StringField('Segundo Apellido', [validators.Length(min=1, max=100)])
    BirthDate = DateField('Fecha de nacimiento', format='%Y-%m-%d', validators=[validators.DataRequired()])
    BirthLocation = FormField(LocationForm, label='Lugar de nacimiento')
    DNI = StringField('Cédula', [validators.Length(min=1, max=10)])
    Gender = RadioField('Género', choices=[('M', 'Masculino'), ('F', 'Femenino')])
    Address = FormField(AddressForm, label='Dirección de vivienda')
    PhoneNumber = StringField('Teléfono', [validators.Length(min=1, max=15)])
    PhoneNumberType = SelectField('Tipo de teléfono')
    Email = EmailField('Correo electrónico', [validators.Length(min=1, max=100)])

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.PhoneNumberType.choices = [(phone_type.IDPhoneNumberType, phone_type.PhoneNumberType) for phone_type in PhoneNumberType.query.all()]

class ParishForm(Form):
    Name = StringField('Nombre de la parroquia', [validators.Length(min=1, max=100)])
    Logo = FileField('Logo')
    Address = FormField(AddressForm, label='Dirección')
    Submit = SubmitField('Registrar')