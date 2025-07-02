from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.authentication import login_required
from app.main.forms import *
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.forms import ParishForm
from app import dal
from app.main.data.dtos.base_dtos import *

bp = Blueprint('admin', __name__)

@bp.route('/dashboard', methods=['GET'])
@login_required("Admin")
def dashboard():
    
    parishes=dal.get_all_parishes()
    parish_priests=dal.get_all_parish_priests()
    catechists=dal.get_all_catechists()
    
    return render_template("admin/dashboard.html", 
                           title="Dashboard del Administrador", 
                           parishes=parishes,
                           parish_priests=parish_priests,
                           catechists=catechists
                           )

@bp.route('/parish/create', methods=['GET', 'POST'])
@login_required("Admin")
def register_parish():
    form = ParishForm()
    if form.validate_on_submit():
        # Construir DTOs desde los datos del formulario
        location_dto = LocationDTO(**form.Address.Location.data)
        
        address_dto = AddressDTO(
            MainStreet=form.Address.MainStreet.data,
            Number=form.Address.Number.data,
            SecondStreet=form.Address.Number.data, 
            Location=location_dto
        )
        # classrooms_dto = [ClassroomDTO(**c) for c in form.Classroom.data] # La DAL no espera esto aún

        parish_dto = ParishDTO(
            Name=form.Name.data,
            Address=address_dto,
            LogoImage=form.LogoImage.data,
            IsMainParish=False, # O manejarlo con un campo en el form
            Classroom=[] # El registro de aulas se puede manejar por separado
        )
        try:
            dal.register_parish(parish_dto)
            flash('Parroquia registrada con éxito.', 'success')
            return redirect(url_for('main.admin_dashboard')) # Asumiendo un dashboard de admin
        except Exception as e:
            flash(f'Error al registrar la parroquia: {e}', 'danger')
            
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)


@bp.route('/parish_priest/create', methods=['GET', 'POST'])
@login_required("Admin")
def register_parish_priest():
    form = ParishPriestForm()
    if form.validate_on_submit():
        # Construir DTOs anidados
        loc_dto = LocationDTO(**form.Person.Address.Location.data)
        addr_dto = AddressDTO(**form.Person.Address.data, Location=loc_dto)
        phone_type_dto = dal.get_phone_number_type_by_id(form.Person.PhoneNumber.PhoneNumberType.data)
        phone_dto = PhoneNumberDTO(**form.Person.PhoneNumber.data, PhoneNumberType=phone_type_dto)
        person_dto = PersonDTO(**form.Person.data, Address=addr_dto, PhoneNumber=phone_dto)

        user_dto = UserDTO(**form.User.data, Role="ParishPriest")
        parish_dto = dal.get_parish_by_id(form.Parish.data)

        priest_dto = ParishPriestDTO(Person=person_dto, User=user_dto, Parish=parish_dto)
        
        try:
            dal.register_parish_priest(priest_dto)
            flash('Párroco registrado con éxito.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            flash(f'Error al registrar párroco: {e}', 'danger')

    return render_template('admin/register_parish_priest.html', title='Registrar Párroco', form=form)

@bp.route('/catechist/create', methods=['GET', 'POST'])
@login_required("Admin")
def register_catechist():
    form = CatechistForm() # Usando el formulario corregido
    if form.validate_on_submit():
        # Lógica similar a la de registrar párroco para construir DTOs de Persona y Usuario
        loc_dto = LocationDTO(**form.Person.Address.Location.data)
        addr_dto = AddressDTO(**form.Person.Address.data, Location=loc_dto)
        phone_type_dto = dal.get_phone_number_type_by_id(form.Person.PhoneNumber.PhoneNumberType.data)
        phone_dto = PhoneNumberDTO(**form.Person.PhoneNumber.data, PhoneNumberType=phone_type_dto)
        person_dto = PersonDTO(**form.Person.data, Address=addr_dto, PhoneNumber=phone_dto)
        user_dto = UserDTO(**form.User.data, Role="Catechist")
        
        # Obtener la parroquia desde el nuevo campo del formulario
        parish_dto = dal.get_parish_by_id(form.Parish.data)

        catechist_dto = CatechistDTO(Person=person_dto, User=user_dto, Parish=parish_dto)
        try:
            dal.register_catechist(catechist_dto)
            flash('Catequista registrado con éxito.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            flash(f'Error al registrar catequista: {e}', 'danger')

    return render_template('admin/register_catechist.html', title='Registrar Catequista', form=form)
