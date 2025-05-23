from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.parish_priest.forms import CatechizingForm, ClassForm, CatechistForm, SupportPersonForm
from app.main.data.dtos.base_dtos import CatechizingDTO, ClassDTO, CatechistDTO, SupportPersonDTO
from app import dal

bp = Blueprint('parish_priest', __name__)

# TODO: Login required decorator
@bp.route('/catechizing/create', methods=['GET', 'POST'])
def register_catechizing():
    form = CatechizingForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        catechizing = CatechizingDTO.from_other_obj(form, depth=-1, custom_var_path="data")

        try:
            catechizing, _ = dal.register_catechizing(catechizing)
            # if not success:
            #     return render_template('parish_priest/catechizing.html', title='Registrar Catequizando', form=form)
        except DuplicateColumnException as e:
            print(f"Error inserting catechizing: {e}")

            match e.table:
                case "Person":
                    match e.columns[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {catechizing.Person.DNI} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {catechizing.Person.FirstName} {catechizing.Person.FirstSurname}."

            flash(error_message, 'danger')
            # return render_template('parish_priest/catechizing.html', title='Registrar Catequizando', form=form)

    return render_template('parish_priest/catechizing.html', title='Registrar Catequizando', form=form)


@bp.route('/class/create', methods=['GET', 'POST'])
def register_class():
    form = ClassForm(request.form)
    
    if request.method == 'POST' and form.validate_on_submit():
        class_data = ClassDTO.from_other_obj(form, depth=-1, custom_var_path="data", include=["Schedule"])

        try:
            class_data, _ = dal.register_class(class_data)
        except DuplicateColumnException as e:
            print(f"Error inserting class: {e}")

            # match e.table:
            #     case "Schedule":
            #         match e.columns[0]:
            #             case "DNI":
            #                 error_message = f"La persona con el DNI {class_data.Person.DNI} ya existe."
            #             case "FirstName":
            #                 error_message = f"Ya existe la persona {class_data.Person.FirstName} {class_data.Person.FirstSurname}."
            
            flash("Error al registrar la clase", 'danger')
            return render_template('parish_priest/register_class.html', title='Registrar Clase', form=form)

        flash(f'¡Clase registrada exitosamente!', 'success')

    return render_template('parish_priest/register_class.html', title='Registrar Clase', form=form)

@bp.route('/catechist/create', methods=['GET', 'POST'])
def register_catechist():
    form = CatechistForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        catechist = CatechistDTO.from_other_obj(form, depth=-1, custom_var_path="data")

        try:
            catechist, _ = dal.register_catechist(catechist)
        except DuplicateColumnException as e:
            print(f"Error inserting catechist: {e}")

            match e.table:
                case "User":
                    error_message = f"El usuario {catechist.User.Username} ya existe."
                case "Person":
                    match e.columns[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {catechist.Person.DNI} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {catechist.Person.FirstName} {catechist.Person.FirstSurname}."

            flash(error_message, 'danger')
            return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        flash(f'¡Catequista {catechist.Person.FirstName} {catechist.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('parish_priest/register_catechist.html', title='Registrar Sacerdote', form=form)

@bp.route('/support_person/create', methods=['GET', 'POST'])
def register_support_person():
    form = SupportPersonForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        support_person = SupportPersonDTO.from_other_obj(form, depth=-1, custom_var_path="data")

        try:
            support_person, _ = dal.register_support_person(support_person)
        except DuplicateColumnException as e:
            print(f"Error inserting support person: {e}")

            match e.table:
                case "User":
                    error_message = f"El usuario {support_person.User.Username} ya existe."
                case "Person":
                    match e.columns[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {support_person.Person.DNI} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {support_person.Person.FirstName} {support_person.Person.FirstSurname}."

            flash(error_message, 'danger')
            return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)
        
        flash(f'¡Persona de soporte {support_person.Person.FirstName} {support_person.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)