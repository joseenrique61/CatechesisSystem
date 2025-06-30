# routes.py (CORREGIDO)

from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import dal
from app.auth.authentication import login_required
from app.auth.forms import LoginForm
from app.main.data.dtos.base_dtos import UserDTO, ParishPriestDTO, CatechistDTO, AdministratorDTO

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'role' in session:
        # Redirige si ya hay una sesión activa
        role = session['role']
        if role == "ParishPriest":
            return redirect(url_for("parish_priest.dashboard"))
        elif role == "Admin":
            return redirect(url_for("admin.dashboard"))
        elif role == "Catechist":
            return redirect(url_for("catechist.dashboard"))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        login_user_dto = UserDTO(
            Username=form.Username.data, 
            Password=form.Password.data,
            Role="temp" # Proporciona un valor temporal para pasar la validación de Pydantic
        )
        
        if not dal.check_user_login(login_user_dto):
            flash("Usuario y/o contraseña incorrectos", "danger")
            return render_template('auth/login.html', form=form, title='Iniciar Sesión')

        # --- Inicio de sesión exitoso ---
        session.clear()
        
        # Obtenemos el DTO completo con todos los datos desde la BD
        user_profile_dto = dal.get_dto_by_user(login_user_dto.Username)
        
        # Verificamos que se haya encontrado un perfil
        if not user_profile_dto:
            flash("Error al cargar el perfil de usuario. Por favor, contacte al administrador.", "danger")
            return redirect(url_for('auth.login'))

        # Asignamos el rol y los datos a la sesión
        user_data_from_db = user_profile_dto.User
        
        role = ""
        
        if isinstance(user_profile_dto, ParishPriestDTO):
            role = "ParishPriest" 
        elif isinstance(user_profile_dto, CatechistDTO):
            role = "Catechist"
        elif isinstance(user_profile_dto, AdministratorDTO):
            role = "Admin"
        
        if not role:
            flash("El usuario no tiene un rol asignado.", "danger")
            return redirect(url_for('auth.login'))

        session['id'] = user_data_from_db.id
        session['role'] = role
        session['username'] = user_data_from_db.Username
        
        flash(f'Bienvenido {user_data_from_db.Username}!', 'success')
        # Redirigimos al dashboard correspondiente según el rol
        # return redirect(url_for(f'{role.lower()}.dashboard'))
        return redirect(url_for('main.dashboard')) # Ir al dashboard después de login

    return render_template('auth/login.html', form=form, title='Iniciar Sesión')

@bp.route('/logout')
@login_required()
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))