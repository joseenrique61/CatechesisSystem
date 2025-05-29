from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.parish_priest.forms import CatechizingForm, CatechizingUpdateForm, ClassForm, SupportPersonForm
from app.main.data.dtos.base_dtos import CatechizingDTO, ClassDTO, SupportPersonDTO
from app.parish_priest.helpers import calculate_age
from app import dal

bp = Blueprint('parish_priest', __name__)

# TODO: Login required decorator
@bp.route("/dashboard", methods=["GET"])
def dashboard():
    parish_classes = dal.get_classes_by_parish_id(dal.get_parish_priest_by_id(2).IDParish, include=["Catechist.Person", "Catechizing", "Catechizing.Person", "Schedule.Classroom"])
    return render_template("parish_priest/dashboard.html",
                           title="Dashboard del párroco", 
                           catechizings=dal.get_catechizings_by_parish(dal.get_parish_priest_by_id(2).IDParish, 
                                                                       include=["Class", "Class.Level"]), 
                           parish_classes=parish_classes,
                           catechists=dal.get_all_catechists(include=["Class", "Class.Level"]), 
                           support_persons=dal.get_all_support_person(include=["Class", "Class.Level"]),
                           calculate_age=calculate_age)


@bp.route('/catechizing/create', methods=['GET', 'POST'])
def register_catechizing():
    form = CatechizingForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        catechizing = CatechizingDTO.from_other_obj(form, depth=-1, custom_var_path="data", include=["Parent", "Godparent", "HealthInformation.Allergy"])

        try:
            catechizing, _ = dal.register_catechizing(catechizing)
        except DuplicateColumnException as e:
            print(f"Error inserting catechizing: {e}")

            match e.table:
                case "Parent":
                    error_message = "Se ha ingresado el mismo nombre y/o DNI de un padre del catequizando en un padrino."
                case "Person":
                    match list(e.values.keys())[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {e.values['DNI']} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {e.values['FirstName']} {e.values['FirstSurname']}."

            flash(error_message, 'danger')
            return render_template('parish_priest/register_catechizing.html', title='Registrar Catequizando', form=form)

        flash(f'¡Catequizando {catechizing.Person.FirstName} {catechizing.Person.FirstSurname} registrado exitosamente!', 'success')
        return redirect(url_for("parish_priest.dashboard"))

    return render_template('parish_priest/register_catechizing.html', title='Registrar Catequizando', form=form)

@bp.route('/catechizing/update/<id>', methods=['GET', 'POST'])
def update_catechizing(id: int):
    if request.method == "GET":
        catechizing_temp = dal.get_catechizing_by_id(id)
        form = CatechizingUpdateForm(obj=catechizing_temp)
    else:
        form = CatechizingUpdateForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        catechizing = CatechizingDTO.from_other_obj(form, depth=-1, custom_var_path="data", exclude=["Person.BirthLocation", "Person.BirthDate", "Parent", "Godparent"], include=["Parent", "Godparent", "HealthInformation.Allergy"])

        try:
            catechizing, _ = dal.update_catechizing(id, catechizing)
        except DuplicateColumnException as e:
            print(f"Error inserting catechizing: {e}")

            match e.table:
                case "Parent":
                    error_message = "Se ha ingresado el mismo nombre y/o DNI de un padre del catequizando en un padrino."
                case "Person":
                    match list(e.values.keys())[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {e.values['DNI']} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {e.values['FirstName']} {e.values['FirstSurname']}."

            flash(error_message, 'danger')
            return render_template('parish_priest/update_catechizing.html', title='Actualizar Catequizando', form=form)

        flash(f'¡Catequizando {catechizing.Person.FirstName} {catechizing.Person.FirstSurname} actualizado exitosamente!', 'success')
        return redirect(url_for("parish_priest.dashboard"))

    return render_template('parish_priest/update_catechizing.html', title='Actualizar Catequizando', form=form)

@bp.route('/catechizing/delete/<id>', methods=['POST'])
def delete_catechizing(id):
    dal.delete_catechizing(id)
    return redirect(url_for("parish_priest.dashboard"))

@bp.route('/class/create', methods=['GET', 'POST'])
def register_class():
    form = ClassForm(request.form)
    
    if request.method == 'POST' and form.validate_on_submit():
        class_data = ClassDTO.from_other_obj(form, depth=-1, custom_var_path="data", include=["Schedule"])

        try:
            class_data, _ = dal.register_class(class_data)
        except DuplicateColumnException as e:
            print(f"Error inserting class: {e}")

            flash("Error al registrar la clase", 'danger')
            return render_template('parish_priest/register_class.html', title='Registrar Clase', form=form)

        flash(f'¡Clase registrada exitosamente!', 'success')
        return redirect(url_for("parish_priest.dashboard"))

    return render_template('parish_priest/register_class.html', title='Registrar Clase', form=form)

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
                    error_message = f"El usuario {e.values['Username']} ya existe."
                case "Person":
                    match list(e.values.keys())[0]:
                        case "DNI":
                            error_message = f"La persona con el DNI {e.values['DNI']} ya existe."
                        case "FirstName":
                            error_message = f"Ya existe la persona {e.values['FirstName']} {e.values['FirstSurname']}."

            flash(error_message, 'danger')
            return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)
        
        flash(f'¡Persona de soporte {support_person.Person.FirstName} {support_person.Person.FirstSurname} registrado exitosamente!', 'success')
        return redirect(url_for("parish_priest.dashboard"))

    return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)