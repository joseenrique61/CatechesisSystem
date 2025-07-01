from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.authentication import login_required
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.forms import CatechizingForm, CatechizingUpdateForm, ClassForm, SupportPersonForm
from app.main.data.dtos.base_dtos import CatechizingDTO, ClassDTO, SupportPersonDTO
from app.parish_priest.helpers import calculate_age
from app import dal

bp = Blueprint('parish_priest', __name__)

@bp.route("/dashboard", methods=["GET"])
@login_required("ParishPriest")
def dashboard():
    
    priest_dto = dal.get_parish_priest_by_id(session["id"])
    
    if not priest_dto or not priest_dto.Parish:
        flash("No se pudo cargar la información del párroco o su parroquia.", "danger")
        return redirect(url_for('main.index'))
    
    current_parish_id = priest_dto.Parish.id
    
    parish_classes = dal.get_classes_by_parish_id(
        current_parish_id, 
        include=["SupportPerson.Person","Catechist.Person","Level","ClassPeriod","Schedule.ClassRoom"]
    )

    support_persons_with_levels = {}

    for p_class in parish_classes:
        # Nos aseguramos de que la clase tenga una persona de soporte asignada
        if p_class.SupportPerson and p_class.SupportPerson.id:
            support_person_id = p_class.SupportPerson.id

            # Si es la primera vez que vemos a esta persona, la añadimos al diccionario
            if support_person_id not in support_persons_with_levels:
                support_persons_with_levels[support_person_id] = {
                    'person_data': p_class.SupportPerson, # El DTO completo de SupportPerson
                    'levels': [] # Una lista para guardar los nombres de los niveles
                }
            
            # Añadimos el nombre del nivel de la clase actual a la lista de la persona
            if p_class.Level and p_class.Level.Name:
                support_persons_with_levels[support_person_id]['levels'].append(p_class.Level.Name)

    # --- FIN DE LA LÓGICA DE AGRUPACIÓN ---

    # ... (el resto de tus llamadas a la DAL para catechizings, catechists, etc.) ...
    catechizings = dal.get_catechizings_by_parish(
        current_parish_id,
        include=["Person","Class", "Class.Level"]
    )

    catechists = dal.get_catechists_by_parish_id(
        current_parish_id,
        include=["User", "Person"]
    )
    
    # Pasamos la nueva estructura de datos a la plantilla
    return render_template(
        "parish_priest/dashboard.html",
        title="Dashboard del párroco",
        catechizings=catechizings,
        parish_classes=parish_classes,
        support_persons_data=support_persons_with_levels, 
        catechists=catechists,
        calculate_age=calculate_age
    )
    
    # parish_classes = dal.get_classes_by_parish_id(current_parish_id, include=["Catechist.Person", "Level", "Schedule.Classroom","ClassPeriod","Class.Catechist","SupportPerson.Person"])
    # catechizings = dal.get_catechizings_by_parish(current_parish_id, include=["Person","Class", "Class.Level"])
    
    # catechists = dal.get_catechists_by_parish_id(current_parish_id,include=["User", "Person"])
    # # support_persons = dal.get_support_persons_by_parish_id(current_parish_id,include=["Person"])
       
    # return render_template("parish_priest/dashboard.html",
    #                        title="Dashboard del párroco", 
    #                        catechizings=catechizings,
    #                        parish_classes=parish_classes,
    #                        catechists=catechists, 
    #                     #    support_persons=support_persons,
    #                        calculate_age=calculate_age)


@bp.route('/catechizing/create', methods=['GET', 'POST'])
@login_required("ParishPriest")
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
@login_required("ParishPriest")
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
@login_required("ParishPriest")
def delete_catechizing(id):
    dal.delete_catechizing(id)
    return redirect(url_for("parish_priest.dashboard"))

@bp.route('/class/create', methods=['GET', 'POST'])
@login_required("ParishPriest")
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
@login_required("ParishPriest")
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