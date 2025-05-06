from wtforms import Form, StringField, SubmitField, validators, FormField, SelectField, PasswordField
from flask_wtf import FlaskForm
from app.main.forms import PersonForm
from app.main.models import Parish

class UserForm(FlaskForm):
    Username = StringField('Nombre de usuario', [validators.Length(min=1, max=100)])
    Password = PasswordField('Contraseña', [
            validators.DataRequired(),
            validators.Length(min=1, max=100),
            validators.EqualTo('ConfirmPassword', message='Las contraseñas no coinciden')
        ])
    ConfirmPassword = PasswordField('Confirmar contraseña', [validators.Length(min=1, max=100)])

class ParishPriestForm(FlaskForm):
    User = FormField(UserForm, label='Datos de usuario')
    Person = FormField(PersonForm, label='Datos personales')
    Parish = SelectField('Parroquia', coerce=int, choices=[])
    Submit = SubmitField('Registrar')

    def __init__(self, *args, **kwargs):
        super(ParishPriestForm, self).__init__(*args, **kwargs)
        self.Parish.choices = [(parish.IDParish, parish.Name) for parish in Parish.query.all()]