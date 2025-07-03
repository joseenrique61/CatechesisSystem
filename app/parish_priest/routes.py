from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.auth.authentication import login_required
from app.main.forms import *
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.mongodb.mongodb_models import *
from app.main.helpers import *
from app.main.services.pdf_service import PDFService
from app import dal
from flask import Response, request 

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

    all_support_person = dal.get_all_support_persons()
    all_sacraments = dal.get_all_sacraments();
    
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
        else:
            for support_person in all_support_person:
                support_person_id = support_person.id
                
                if support_person_id not in support_persons_with_levels:
                    support_persons_with_levels[support_person_id] = {
                        'person_data': support_person, # El DTO completo de SupportPerson
                        'levels': []
                    }
                    
                    support_persons_with_levels[support_person_id]['levels'].append("No tiene clases asignadas")

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
        all_sacraments=all_sacraments,
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
    # Obtenemos el catequizando con todos sus datos anidados
    catechizing = dal.get_catechizing_by_id(catechizing_id, include=[
        "Person.Address.Location", "Person.PhoneNumber.PhoneNumberType", 
        "Class.Level", "School", "HealthInformation.EmergencyContact", "Sacrament",
        "Parent.Person", "Godparent.Person"
    ])
    if not catechizing:
        flash('Catequizando no encontrado.', 'danger')
        return redirect(url_for('parish_priest.dashboard'))
    
    # Creamos el formulario. En GET, WTForms lo poblará con `obj=catechizing`.
    # Gracias al PersonUpdateForm corregido, TODOS los campos se poblarán.
    form = CatechizingUpdateForm(obj=catechizing)
    
    # --- LÓGICA DE PRE-PROCESAMIENTO PARA CAMPOS DINÁMICOS ---
    if request.method == 'GET':
        # Pre-poblar sacramentos
        form.Sacrament.data = [s.id for s in catechizing.Sacrament]
        
        # Pre-poblar y pre-seleccionar contacto de emergencia
        contact_choices = []
        for i, p in enumerate(catechizing.Parent):
            if p.Person: contact_choices.append((f"parent-{i}", f"{p.Person.FirstName} {p.Person.FirstSurname} (Padre/Tutor)"))
        for i, g in enumerate(catechizing.Godparent):
            if g.Person: contact_choices.append((f"godparent-{i}", f"{g.Person.FirstName} {g.Person.FirstSurname} (Padrino/Madrina)"))
        form.HealthInformation.EmergencyContact.choices = [('', '--- Seleccione ---')] + contact_choices
        
        if catechizing.HealthInformation and catechizing.HealthInformation.EmergencyContact:
            current_contact_id = catechizing.HealthInformation.EmergencyContact.id
            found_value = None
            for i, p in enumerate(catechizing.Parent):
                if p.Person and p.Person.id == current_contact_id: found_value = f"parent-{i}"; break
            if not found_value:
                for i, g in enumerate(catechizing.Godparent):
                    if g.Person and g.Person.id == current_contact_id: found_value = f"godparent-{i}"; break
            if found_value: form.HealthInformation.EmergencyContact.data = found_value

    if form.validate_on_submit():
        try:
            # --- ¡LÓGICA DE CONSTRUCCIÓN DE DTO SIMPLIFICADA! ---
            
            # 1. Usamos el helper directamente sobre form.Person, que ahora tiene todos los datos.
            person_dto = build_person_dto_from_form(form.Person)

            # 2. Lógica de Health Information (similar a la de 'create')
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

            # 3. Construir DTOs de referencia
            school_dto = SchoolDTO(**form.School.data)
            class_dto = ClassDTO(id=form.Class.data)
            all_sacraments_in_db = {str(s.id): s for s in dal.get_all_sacraments()}
            sacraments_dto_list = [all_sacraments_in_db[sac_id] for sac_id in form.Sacrament.data if sac_id in all_sacraments_in_db]

            # 4. Ensamblar DTO de actualización
            updated_dto = CatechizingDTO(
                Person=person_dto,
                PayedLevelCourse=form.PayedLevelCourse.data,
                DataSheetInformation=form.DataSheetInformation.data,
                School=school_dto,
                Class=class_dto,
                HealthInformation=health_dto,
                Sacrament=sacraments_dto_list,
                IsLegitimate=catechizing.IsLegitimate,
                SiblingsNumber=catechizing.SiblingsNumber,
                ChildNumber=catechizing.ChildNumber
            )

            dal.update_catechizing(catechizing_id, updated_dto)
            flash('Información del catequizando actualizada con éxito.', 'success')
            return redirect(url_for('parish_priest.dashboard'))
        
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
    priest_dto = dal.get_parish_priest_by_id(session["id"])
    
    if not priest_dto or not priest_dto.Parish:
        flash("No se pudo cargar la información del párroco o su parroquia.", "danger")
        return redirect(url_for('main.index'))
    
    current_parish_id = priest_dto.Parish.id
       
    form = ClassForm(current_parish_id)
    if form.validate_on_submit():
        try:
            # 1. Construir DTOs para las referencias a partir de los IDs del formulario
            period_dto = dal.get_class_period_by_id(form.ClassPeriod.data)
            level_dto = dal.get_level_by_id(form.Level.data)
            catechist_dto = dal.get_catechist_by_id(form.Catechist.data)
            support_person_dto = dal.get_support_person_by_id(form.SupportPerson.data) if form.SupportPerson.data else None
            
            # --- 2. CONSTRUIR EL SCHEDULEDTO DE FORMA EXPLÍCITA ---
            schedule_form = form.Schedule # Alias para el subformulario
            classroom_dto = dal.get_classroom_by_id(schedule_form.Classroom.data)

            schedule_dto = ScheduleDTO(
                DayOfTheWeek=schedule_form.DayOfTheWeek.data,
                StartHour=schedule_form.StartHour.data.strftime('%H:%M'),
                EndHour=schedule_form.EndHour.data.strftime('%H:%M'),
                Classroom=classroom_dto
            )

            # --- 3. CONSTRUIR EL CLASSDTO PRINCIPAL ---
            class_dto = ClassDTO(
                ClassPeriod=period_dto,
                Level=level_dto,
                Catechist=catechist_dto,
                SupportPerson=support_person_dto,
                Schedule=schedule_dto
            )
            
            # --- 4. LLAMAR A LA DAL ---
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
            # 1. Obtener la parroquia del párroco en sesión
            priest_dto = dal.get_dto_by_user(session.get('username'))
            if not priest_dto or not priest_dto.Parish:
                flash('Error: No se pudo determinar tu parroquia.', 'danger')
                return redirect(url_for('parish_priest.dashboard'))

            # 2. Construir el DTO de la persona usando el helper
            person_dto = build_person_dto_from_form(form.Person)
            
            # 3. Construir el DTO de SupportPerson
            support_person_dto = SupportPersonDTO(
                Person=person_dto, 
                Parish=priest_dto.Parish
            )
            
            dal.register_support_person(support_person_dto)
            flash('Persona de soporte registrada con éxito.', 'success')
            return redirect(url_for('parish_priest.dashboard'))
            
        except Exception as e:
            flash(f'Error al registrar persona de soporte: {e}', 'danger')

    return render_template('parish_priest/register_support_person.html', title='Registrar Persona de Soporte', form=form)

@bp.route('/catechizing/<string:catechizing_id>/certificate')
@login_required("ParishPriest")
def generate_certificate(catechizing_id):
    # 1. Obtener los datos...
    catechizing = dal.get_catechizing_by_id(catechizing_id, include=[
        "Person", "Class.Level", "Class.Catechist.Parish"
    ])
    if not catechizing:
        flash("Catequizando no encontrado.", "danger")
        return redirect(url_for('parish_priest.dashboard'))
    
    priest_dto = dal.get_parish_priest_by_id(session["id"])
    if not priest_dto or not priest_dto.Parish:
        flash("No se pudo cargar la información del párroco o su parroquia.", "danger")
        return redirect(url_for('main.index'))
    
    parish_dto = priest_dto.Parish

    # 2. Generar el PDF
    pdf_service = PDFService()
    pdf_bytes = pdf_service.generate_catechizing_certificate(catechizing, parish_dto)

    # --- CINTURÓN DE SEGURIDAD ---
    if not pdf_bytes:
        # Si llegamos aquí, es porque la función de PDF retornó None.
        # Mostramos un error claro en lugar de dejar que la app crashee.
        print("ERROR CRÍTICO: La función de PDF retornó 'None'. Revisar la llamada a pdf.output().")
        flash("Error interno del servidor al generar el certificado.", "danger")
        return redirect(url_for('parish_priest.dashboard'))

    # 3. Preparar nombre de archivo
    full_name_file = f"certificado_{catechizing.Person.FirstName}_{catechizing.Person.FirstSurname}".replace(" ", "_")

    # 4. Crear y devolver la respuesta para descargar
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename={full_name_file}.pdf'}
    )


@bp.route('/report/catechizings', methods=['POST'])
@login_required("ParishPriest")
def generate_report():
    # 1. Obtener los datos de la parroquia y el filtro del formulario
    priest_dto = dal.get_dto_by_user(session.get('username'))
    sacrament_id_filter = request.form.get('sacrament_filter') # Obtiene el ID del sacramento del select
    
    current_parish_id = priest_dto.Parish.id
    catechizings_list = dal.get_catechizings_by_parish(
        current_parish_id,
        include=["Person", "Class.Level", "Sacrament"]
    )
    
    # 2. Filtrar los catequizandos si se aplicó un filtro de sacramento
    report_title_filter = "Todos"
    if sacrament_id_filter:
        filtered_list = []
        for c in catechizings_list:
            if any(s.id == sacrament_id_filter for s in c.Sacrament):
                filtered_list.append(c)
        catechizings_list = filtered_list
        
        # Obtener el nombre del sacramento para el título del reporte
        sacrament_obj = dal.get_sacrament_by_id(sacrament_id_filter) # Necesitarás este método en la DAL
        if sacrament_obj:
            report_title_filter = sacrament_obj.Name

    # 4. Generar el PDF
    pdf_service = PDFService()
    pdf_bytes = pdf_service.generate_parish_report(catechizings_list, sacrament_filter=report_title_filter)

    return Response(pdf_bytes,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline;filename=reporte_catequizandos.pdf'})