from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import dal
from app.auth.forms import LoginForm
from app.main.data.dtos.base_dtos import UserDTO, ParishPriestDTO, CatechistDTO, AdministratorDTO

bp = Blueprint('auth', __name__) # No necesita url_prefix aquí, se define al registrar

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'role' in session:
        match session['role']:
            case "ParishPriest":
                return redirect(url_for("parish_priest.dashboard"))
            case "Admin":
                return redirect(url_for("admin.dashboard"))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = UserDTO.from_other_obj(form, custom_var_path="data")

        if not dal.check_user_login(user):
            flash("Usuario y/o contraseña incorrectos", "danger")
            return render_template('auth/login.html', form=form, title='Iniciar Sesión')

        # Inicio de sesión exitoso
        session.clear()
        
        user_type = dal.get_dto_by_user(user.Username)
        if type(user_type) is ParishPriestDTO:
            user_id = user_type.IDParishPriest
            role = "ParishPriest" 
        elif type(user_type) is CatechistDTO:
            user_id = user_type.IDCatechist
            role = "Catechist"
        elif type(user_type) is AdministratorDTO:
            user_id = user.IDUser
            role = "Admin"

        session['id'] = user_id
        session['role'] = role
        session['username'] = user.Username

        print(session)
        
        flash(f'Bienvenido {user.Username}!', 'success')
        return redirect(url_for('main.dashboard')) # Ir al dashboard después de login

    return render_template('auth/login.html', form=form, title='Iniciar Sesión')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))