from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.authentication import login_required
from app.main.forms import *
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.forms import ParishForm
from app.main.helpers import *
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
        
        classrooms_dto = [ClassroomDTO(**c) for c in form.Classroom.data] 
        
        parish_dto = ParishDTO(
            Name=form.Name.data,
            Address=address_dto,
            LogoImage=form.LogoImage.data,
            Classroom=classrooms_dto,
            IsMainParish=False # O manejarlo con un campo en el form
        )
        
        try:
            dal.register_parish(parish_dto)
            flash('Parroquia registrada con éxito.', 'success')
            return redirect(url_for('admin.dashboard')) # Asumiendo un dashboard de admin
        except Exception as e:
            flash(f'Error al registrar la parroquia: {e}', 'danger')
            
    return render_template('admin/register_parish.html', title='Registrar Parroquia', form=form)


@bp.route('/parish-priest/create', methods=['GET', 'POST'])
@login_required("Admin")
def register_parish_priest():
    form = ParishPriestForm()
    if form.validate_on_submit():
        try:
            # --- VERIFICACIÓN AÑADIDA ---
            parish_dto = dal.get_parish_by_id(form.Parish.data)
            if not parish_dto:
                # Esto evita un error en la DAL si la parroquia no se encuentra.
                flash(f"Error: La parroquia seleccionada no existe.", "danger")
                return render_template('admin/register_parish_priest.html', title='Registrar Párroco', form=form)

            priest_person_dto = build_person_dto_from_form(form.Person)
            user_dto = UserDTO(**form.User.data, Role="ParishPriest")

            priest_dto = ParishPriestDTO(
                Person=priest_person_dto, 
                User=user_dto, 
                Parish=parish_dto
            )
            
            dal.register_parish_priest(priest_dto)
            flash('Párroco registrado con éxito.', 'success')
            return redirect(url_for('admin.dashboard')) # Asegúrate de que este endpoint sea correcto

        except Exception as e:
            # Es bueno loguear el error completo para depuración
            flash(f'Error inesperado al registrar párroco: {e}', 'danger')

    return render_template('admin/register_parish_priest.html', title='Registrar Párroco', form=form)

@bp.route('/catechist/create', methods=['GET', 'POST'])
@login_required("Admin")
def register_catechist():
    form = CatechistForm()
    if form.validate_on_submit():
        try:
            # --- VERIFICACIÓN AÑADIDA ---
            parish_dto = dal.get_parish_by_id(form.Parish.data)
            if not parish_dto:
                flash(f"Error: La parroquia seleccionada no existe.", "danger")
                return render_template('admin/register_catechist.html', title='Registrar Catequista', form=form)

            catechist_person_dto = build_person_dto_from_form(form.Person)
            user_dto = UserDTO(**form.User.data, Role="Catechist")

            catechist_dto = CatechistDTO(
                Person=catechist_person_dto, 
                User=user_dto, 
                Parish=parish_dto
            )

            dal.register_catechist(catechist_dto)
            flash('Catequista registrado con éxito.', 'success')
            return redirect(url_for('admin.dashboard')) # Asegúrate de que este endpoint sea correcto

        except Exception as e:
            flash(f'Error inesperado al registrar catequista: {e}', 'danger')

    return render_template('admin/register_catechist.html', title='Registrar Catequista', form=form)