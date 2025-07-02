from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.auth.authentication import login_required
from app.main.forms import *
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.mongodb.mongodb_models import *
from app.main.helpers import *
from app import dal
from flask import request

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
        include=["SupportPerson.Person","Catechist.Person","Level","ClassPeriod","Schedule.Classroom"]
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

@bp.route('/catechizing/create', methods=['GET', 'POST'])
@login_required("ParishPriest")
def register_catechizing():
    form = CatechizingForm()
    
    if request.method == 'POST':
        # --- 1. PRE-POBLAR CAMPO DE ALERGIAS ---
        # Buscamos cuántas alergias se enviaron en el formulario
        allergy_count = 0
        while f'HealthInformation-Allergy-{allergy_count}' in request.form:
            allergy_count += 1
        
        # Eliminamos las entradas por defecto (si min_entries era 0, no hay ninguna)
        while len(form.HealthInformation.Allergy) > 0:
            form.HealthInformation.Allergy.pop_entry()
            
        # Añadimos tantas entradas vacías como datos de alergia se recibieron
        for _ in range(allergy_count):
            form.HealthInformation.Allergy.append_entry()

        # --- 2. PRE-POBLAR OPCIONES DE CONTACTO DE EMERGENCIA ---
        emergency_choices = [('', '--- Seleccione de la lista o registre uno nuevo ---')]
        
        parent_count = 0
        while f'Parent-{parent_count}-Person-FirstName' in request.form:
            first_name = request.form.get(f'Parent-{parent_count}-Person-FirstName', '')
            last_name = request.form.get(f'Parent-{parent_count}-Person-FirstSurname', '')
            if first_name or last_name:
                emergency_choices.append((f"parent-{parent_count}", f"{first_name} {last_name} (Padre/Tutor)".strip()))
            parent_count += 1
            
        if not form.HealthInformation.RegisterNewContact.data:
            for field in form.HealthInformation.NewEmergencyContact:
                # Hacemos una copia de la lista de validadores y la modificamos
                field.validators = [v for v in field.validators if not isinstance(v, (validators.DataRequired, validators.InputRequired))]
                field.validators.insert(0, validators.Optional())
        else:
            # Si el checkbox SÍ está marcado, nos aseguramos de que los campos clave sean requeridos.
            # Esto sobreescribe cualquier 'Optional' que pudiera haber.
            form.HealthInformation.NewEmergencyContact.FirstName.validators = [validators.DataRequired(), validators.Length(min=1, max=100)]
            form.HealthInformation.NewEmergencyContact.FirstSurname.validators = [validators.DataRequired(), validators.Length(min=1, max=100)]
            form.HealthInformation.NewEmergencyContact.EmailAddress.validators = [validators.DataRequired(), validators.Email()]

        godparent_count = 0
        while f'Godparent-{godparent_count}-Person-FirstName' in request.form:
            first_name = request.form.get(f'Godparent-{godparent_count}-Person-FirstName', '')
            last_name = request.form.get(f'Godparent-{godparent_count}-Person-FirstSurname', '')
            if first_name or last_name:
                emergency_choices.append((f"godparent-{godparent_count}", f"{first_name} {last_name} (Padrino/Madrina)".strip()))
            godparent_count += 1
        
        form.HealthInformation.EmergencyContact.choices = emergency_choices
    
    if form.validate_on_submit():
        try:
            # --- 1. Construir el DTO del Catequizando (Persona) ---
            catechizing_person_dto = build_person_dto_from_form(form.Person)

            # --- 2. Construir los DTOs para las listas (Padres y Padrinos) ---
            parents_dto_list = []
            for parent_form in form.Parent:
                parent_person_dto = build_person_dto_from_form(parent_form.Person)
                parents_dto_list.append(
                    ParentDTO(Person=parent_person_dto, Ocuppation=parent_form.Ocuppation.data)
                )

            godparents_dto_list = []
            for godparent_form in form.Godparent:
                godparent_person_dto = build_person_dto_from_form(godparent_form.Person)
                godparents_dto_list.append(GodparentDTO(Person=godparent_person_dto))
                
            # --- 3. Construir DTO de Información de Salud ---
            
            # Esta lógica ahora es más simple gracias a la validación en el formulario
            health_info_form = form.HealthInformation
            emergency_contact_dto = None  # Empezamos con el DTO vacío

            if health_info_form.RegisterNewContact.data:
                # Si se registra un nuevo contacto, simplemente construimos su DTO.        
                emergency_contact_dto = build_person_dto_from_form(health_info_form.NewEmergencyContact)
            
            elif health_info_form.EmergencyContact.data:
                # Si se selecciona de la lista, obtenemos sus datos del formulario.
                contact_value = health_info_form.EmergencyContact.data
                try:
                    person_type, index_str = contact_value.split('-')
                    index = int(index_str)
                    source_person_form = None
                    if person_type == 'parent':
                        source_person_form = form.Parent.entries[index].Person
                    elif person_type == 'godparent':
                        source_person_form = form.Godparent.entries[index].Person
                    
                    if source_person_form:
                        # Construimos el DTO a partir de los datos del formulario.
                        emergency_contact_dto = build_person_dto_from_form(source_person_form)
                except (ValueError, IndexError):
                    flash(f"Valor de contacto de emergencia inválido: {contact_value}", "warning")
            
            # Ahora, creamos el HealthInformationDTO, pasándole el DTO completo de la persona.
            health_dto = HealthInformationDTO(
                ImportantAspects=health_info_form.ImportantAspects.data,
                BloodType=health_info_form.BloodType.data,
                Allergy=health_info_form.Allergy.data,
                EmergencyContact=emergency_contact_dto # Pasamos el PersonDTO completo
            )

            sacraments_dto_list = []
            sacrament_ids_from_form = form.Sacrament.data
            if sacrament_ids_from_form:
                # Obtenemos los documentos completos desde la DAL
                all_sacraments_in_db = {str(s.id): s for s in dal.get_all_sacraments()}
                for sac_id in sacrament_ids_from_form:
                    # Buscamos el DTO completo en el diccionario que creamos
                    if sac_id in all_sacraments_in_db:
                        # Añadimos el DTO completo (con id y Name) a nuestra lista
                        sacraments_dto_list.append(all_sacraments_in_db[sac_id])
            
            # --- 4. Construir DTOs simples y de referencia ---
            school_dto = SchoolDTO(**form.School.data)
            class_dto = ClassDTO(id=form.Class.data)
            

            # --- 5. Ensamblar el DTO principal de Catequizando ---
            catechizing_dto = CatechizingDTO(
                Person=catechizing_person_dto,
                IsLegitimate=form.IsLegitimate.data,
                SiblingsNumber=form.SiblingsNumber.data,
                ChildNumber=form.ChildNumber.data,
                PayedLevelCourse=form.PayedLevelCourse.data,
                DataSheetInformation=form.DataSheetInformation.data,
                Class=class_dto,
                School=school_dto,
                HealthInformation=health_dto,
                Parent=parents_dto_list,
                Godparent=godparents_dto_list,
                Sacrament=sacraments_dto_list,
                LevelCertificate=[],
                AttendedClass=[],
                ParticularClass=[]
            )

            # --- 6. Llamar a la DAL para registrar ---
            dal.register_catechizing(catechizing_dto)
            flash('Catequizando registrado con éxito.', 'success')
            return redirect(url_for('parish_priest.dashboard')) # O a la lista de catequizandos

        except Exception as e:
            # Captura cualquier error durante la construcción del DTO o la llamada a la DAL.
            flash(f'Error al registrar catequizando: {e}', 'danger')
            
    return render_template('parish_priest/register_catechizing.html', title='Registrar Catequizando', form=form)

@bp.route('/catechizing/update/<string:catechizing_id>', methods=['GET', 'POST'])
@login_required('ParishPriest')
def update_catechizing(catechizing_id):
    # En la solicitud GET, necesitamos todos los datos anidados para poblar el formulario.
    # El include es crucial para que `obj=catechizing` funcione correctamente.
    includes_for_form = [
        "Person.Address.Location", 
        "Person.PhoneNumber.PhoneNumberType", 
        "Class.Level", 
        "HealthInformation.EmergencyContact"
    ]
    
    catechizing = dal.get_catechizing_by_id(catechizing_id, include=includes_for_form)
    
    if not catechizing:
        flash('Catequizando no encontrado.', 'danger')
        return redirect(url_for('parish_priest.parish_dashboard'))
    
    form = CatechizingUpdateForm(obj=catechizing)
    
    if form.validate_on_submit():
        try:
            # --- 1. Construir el DTO de Persona actualizado ---
            person_update_form = form.Person
            loc_dto = LocationDTO(**person_update_form.Address.Location.data)
            addr_dto = AddressDTO(**person_update_form.Address.data, Location=loc_dto)
            
            # El PhoneNumberType solo se actualiza si se envía un ID válido.
            phone_type_id = getattr(person_update_form.PhoneNumber.PhoneNumberType, 'data', None)
            phone_type_dto = dal.get_phone_number_type_by_id(phone_type_id) if phone_type_id else None
            
            phone_dto = PhoneNumberDTO(
                **person_update_form.PhoneNumber.data, 
                PhoneNumberType=phone_type_dto
            )

            person_dto = PersonDTO(
                Address=addr_dto, 
                PhoneNumber=phone_dto, 
                EmailAddress=person_update_form.EmailAddress.data
            )

            # --- 2. Construir DTO de Información de Salud actualizado ---
            health_update_form = form.HealthInformation
            emergency_contact_dto = None
            if health_update_form.RegisterNewContact.data:
                # Si se registra un nuevo contacto...
                # 1. Construir un DTO de persona con los datos del subformulario.
                new_contact_person_dto = build_person_dto_from_form(health_update_form.NewEmergencyContact)
                emergency_contact_person_doc = dal._get_or_create_person(new_contact_person_dto)
                emergency_contact_dto = new_contact_person_dto

            elif health_update_form.EmergencyContact.data:
                # Si se seleccionó uno existente, obtener su documento.
                emergency_contact_person_doc = PersonDocument.objects.with_id(health_update_form.EmergencyContact.data)
                emergency_contact_dto = dal._get_or_create_person(emergency_contact_person_doc)
            
            health_dto = HealthInformationDTO(
                ImportantAspects=health_update_form.ImportantAspects.data,
                Allergy=health_update_form.Allergy.data,
                EmergencyContact=emergency_contact_dto,
                # Pasamos el BloodType desde el campo oculto del formulario original.
                BloodType=catechizing.HealthInformation.BloodType 
            )

            # --- 3. Construir DTOs simples y de referencia actualizados ---
            school_dto = SchoolDTO(**form.School.data)
            class_dto = ClassDTO(id=form.Class.data)

            # --- 4. Ensamblar el DTO principal de actualización ---
            # Campos no editables como SiblingsNumber no se incluyen en el DTO de actualización.
            # La DAL se encargará de no modificarlos.
            updated_catechizing_dto = CatechizingDTO(
                Person=person_dto,
                PayedLevelCourse=form.PayedLevelCourse.data,
                DataSheetInformation=form.DataSheetInformation.data,
                School=school_dto,
                Class=class_dto,
                HealthInformation=health_dto,
            )

            # --- 5. Llamar a la DAL para actualizar ---
            dal.update_catechizing(catechizing_id, updated_catechizing_dto)
            flash('Información del catequizando actualizada con éxito.', 'success')
            return redirect(url_for('parish_priest.view_catechizing', catechizing_id=catechizing_id)) # Asumiendo una ruta para ver detalles
        
        except Exception as e:
            flash(f'Error al actualizar la información: {e}', 'danger')
            
    return render_template('parish_priest/update_catechizing.html', title='Actualizar Catequizando', form=form, catechizing_id=catechizing_id)

@bp.route('/catechizing/delete/<string:catechizing_id>', methods=['POST'])
@login_required('ParishPriest')
def delete_catechizing(catechizing_id):
    try:
        success = dal.delete_catechizing(catechizing_id)
        if success:
            flash('Catequizando eliminado con éxito.', 'success')
        else:
            flash('No se pudo eliminar al catequizando o no fue encontrado.', 'warning')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'danger')
    return redirect(url_for('parish_priest.dashboard')) # Redirigir a la lista de catequizandos

@bp.route('/class/create', methods=['GET', 'POST'])
@login_required("ParishPriest")
def register_class():
    form = ClassForm()
    if form.validate_on_submit():
        try:
            # Construir DTOs para las referencias
            period_dto = ClassPeriodDTO(id=form.ClassPeriod.data)
            level_dto = LevelDTO(id=form.Level.data)
            catechist_dto = CatechistDTO(id=form.Catechist.data)
            support_person_dto = SupportPersonDTO(id=form.SupportPerson.data) if form.SupportPerson.data else None
            
            # Construir DTO anidado para el horario
            classroom_dto = ClassroomDTO(id=form.Schedule.Classroom.data)
            schedule_dto = ScheduleDTO(
                **form.Schedule.data,
                StartHour=form.Schedule.StartHour.data.strftime('%H:%M'), # Convertir Time a string
                EndHour=form.Schedule.EndHour.data.strftime('%H:%M'),   # Convertir Time a string
                Classroom=classroom_dto
            )

            # Construir el DTO principal de la clase
            class_dto = ClassDTO(
                ClassPeriod=period_dto,
                Level=level_dto,
                Catechist=catechist_dto,
                SupportPerson=support_person_dto,
                Schedule=schedule_dto
            )

            dal.register_class(class_dto)
            flash('Clase registrada con éxito.', 'success')
            return redirect(url_for('parish_priest.dashboard'))
        except Exception as e:
            flash(f'Error al registrar la clase: {e}', 'danger')

    return render_template('parish_priest/register_class.html', title='Registrar Clase', form=form)

@bp.route('/support_person/create', methods=['GET', 'POST'])
@login_required("ParishPriest")
def register_support_person():
    form = SupportPersonForm()
    if form.validate_on_submit():
        try:
            # Obtener la parroquia del párroco en sesión
            priest_dto = dal.get_dto_by_user(session.get('username'))
            if not priest_dto or not priest_dto.Parish:
                flash('Error: No se pudo determinar tu parroquia.', 'danger')
                return redirect(url_for('parish_priest.dashboard'))

            # Construir DTOs... (similar a los otros registros de persona)
            loc_dto = LocationDTO(**form.Person.Address.Location.data)
            addr_dto = AddressDTO(**form.Person.Address.data, Location=loc_dto)
            phone_type_dto = dal.get_phone_number_type_by_id(form.Person.PhoneNumber.PhoneNumberType.data)
            phone_dto = PhoneNumberDTO(**form.Person.PhoneNumber.data, PhoneNumberType=phone_type_dto)
            person_dto = PersonDTO(**form.Person.data, Address=addr_dto, PhoneNumber=phone_dto)
            
            support_person_dto = SupportPersonDTO(Person=person_dto, Parish=priest_dto.Parish)
            
            dal.register_support_person(support_person_dto)
            flash('Persona de soporte registrada con éxito.', 'success')
            return redirect(url_for('parish_priest.dashboard'))
        except Exception as e:
            flash(f'Error al registrar persona de soporte: {e}', 'danger')

    return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)



            # health_info_form = form.HealthInformation
            # emergency_contact_dto = None
            # if health_info_form.RegisterNewContact.data:
            #     # Si se registra un nuevo contacto, construirlo desde el subformulario.
            #     emergency_contact_dto = build_person_dto_from_form(health_info_form.NewEmergencyContact)
            # elif health_info_form.EmergencyContact.data:
            #     # Si se seleccionó uno existente, crear un DTO solo con el ID.
            #     emergency_contact_dto = PersonDTO(id=health_info_form.EmergencyContact.data)