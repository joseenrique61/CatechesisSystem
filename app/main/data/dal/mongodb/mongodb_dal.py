# mongodb_dal.py (VERSIÓN FINAL COMPLETA Y REFACTORIZADA)

from typing import Optional, List
from mongoengine.errors import NotUniqueError, DoesNotExist
from flask_mongoengine import MongoEngine
import logging

from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.mongodb.mongodb_models import *
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.data.image_manager import delete_image, upload_image

class MongoDBDAL(IDataAccessLayer):
    """
    Capa de Acceso a Datos (DAL) para MongoDB completamente refactorizada para usar
    ObjectIds y referencias directas de MongoEngine, implementando rigurosamente
    el contrato de IDataAccessLayer.
    """
    def __init__(self, db: MongoEngine):
        self.db = db

    # --- Funciones de Ayuda Internas ---

    # def _to_dto(self, document, dto_class, include: list[str] = [], exclude: list[str] = []):
    #     if not document:
    #         return None
    #     return dto_class.from_other_obj(document, include=include + ['id'], exclude=exclude)
    
    def _to_dto(self, document, dto_class, include: list[str] = [], exclude: list[str] = []):
        if not document:
            return None
        # Esta es la forma más simple de manejar la conversión
        # dto_instance = dto_class.from_orm(document)
        dto_instance =  dto_class.from_other_obj(document, include=include + ['id'], exclude=exclude)
        dto_instance.id = str(document.id)
        return dto_instance

    def _get_or_create_person(self, person_data: PersonDTO) -> PersonDocument:
        if person_data.DNI and (doc := PersonDocument.objects(DNI=person_data.DNI).first()):
            return doc
        if person_data.EmailAddress and (doc := PersonDocument.objects(EmailAddress=person_data.EmailAddress).first()):
            return doc

        address_doc = None
        if addr_data := person_data.Address:
            # CORRECCIÓN AQUÍ: Usamos .model_dump() en lugar de .to_dict()
            location_doc = LocationDocument(**addr_data.Location.model_dump()) if addr_data.Location else None
            address_doc = AddressDocument(MainStreet=addr_data.MainStreet, Number=addr_data.Number, SecondStreet=addr_data.SecondStreet, Location=location_doc)
        
        phone_doc = None
        if phone_data := person_data.PhoneNumber:
            # Asegurarse de que el PhoneNumberType y su id existen antes de buscar
            phone_type_doc = None
            if phone_data.PhoneNumberType and phone_data.PhoneNumberType.id:
                phone_type_doc = PhoneNumberTypeDocument.objects(id=phone_data.PhoneNumberType.id).first()
            phone_doc = PhoneNumberDocument(PhoneNumber=phone_data.PhoneNumber, PhoneNumberType=phone_type_doc)

        birth_location_doc = None
        if birth_loc_data := person_data.BirthLocation:
            # CORRECCIÓN AQUÍ: Usamos .model_dump() en lugar de .to_dict()
            birth_location_doc = LocationDocument(**birth_loc_data.model_dump())

        new_person = PersonDocument(
            FirstName=person_data.FirstName, MiddleName=person_data.MiddleName,
            FirstSurname=person_data.FirstSurname, SecondSurname=person_data.SecondSurname,
            BirthDate=person_data.BirthDate, DNI=person_data.DNI, Gender=person_data.Gender,
            EmailAddress=person_data.EmailAddress, Address=address_doc,
            PhoneNumber=phone_doc, BirthLocation=birth_location_doc
        ).save()
        
        return new_person
    
    def _get_or_create_parent(self, parent_dto: ParentDTO) -> ParentDocument:
        """Crea la Persona y luego el rol de Padre/Tutor, o lo devuelve si ya existe."""
        if not parent_dto or not parent_dto.Person: return None
        
        person_doc = self._get_or_create_person(parent_dto.Person)
        
        # Evita crear roles duplicados para la misma persona
        parent_doc = ParentDocument.objects(Person=person_doc).first()
        if parent_doc:
            return parent_doc
            
        new_parent_doc = ParentDocument(
            Person=person_doc,
            Ocuppation=parent_dto.Ocuppation
        ).save()
        return new_parent_doc

    def _get_or_create_godparent(self, godparent_dto: GodparentDTO) -> GodparentDocument:
        """Crea la Persona y luego el rol de Padrino/Madrina, o lo devuelve si ya existe."""
        if not godparent_dto or not godparent_dto.Person: return None
            
        person_doc = self._get_or_create_person(godparent_dto.Person)

        godparent_doc = GodparentDocument.objects(Person=person_doc).first()
        if godparent_doc:
            return godparent_doc

        new_godparent_doc = GodparentDocument(Person=person_doc).save()
        return new_godparent_doc

    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        # PASO 1: Crear la persona principal del catequizando.
        person_doc = self._get_or_create_person(catechizing_data.Person)

        # PASO 2: Iterar y crear los documentos de Padres/Tutores.
        parent_docs = [self._get_or_create_parent(p) for p in catechizing_data.Parent if p]
        
        # PASO 3: Iterar y crear los documentos de Padrinos/Madrinas.
        godparent_docs = [self._get_or_create_godparent(g) for g in catechizing_data.Godparent if g]

        # PASO 4: Obtener las referencias a otros documentos existentes.
        class_doc = ClassDocument.objects(id=catechizing_data.Class.id).first() if catechizing_data.Class else None
        # Los sacramentos ya existen, solo los enlazamos.
        
        sacrament_ids = [s.id for s in catechizing_data.Sacrament if s.id]
        sacrament_docs = list(SacramentDocument.objects(id__in=sacrament_ids))
        
        # PASO 5: Construir los documentos embebidos.
        school_doc = SchoolEmbedded(**catechizing_data.School.model_dump()) if catechizing_data.School else None
        
        health_info_doc = None
        if health_data := catechizing_data.HealthInformation:
            contact_person_doc = None
            # Si se proporcionó un contacto de emergencia...
            if health_data.EmergencyContact:
                # ...usamos nuestro método helper para buscarlo o crearlo en la BDD.
                contact_person_doc = self._get_or_create_person(health_data.EmergencyContact)
            
            # Ahora creamos el documento embebido con la referencia correcta.
            health_info_doc = HealthInformationEmbedded(
                ImportantAspects=health_data.ImportantAspects,
                BloodType=health_data.BloodType,
                EmergencyContact=contact_person_doc, # Pasamos el documento de MongoEngine
                Allergy=health_data.Allergy
            )

        baptismal_cert_doc = None
        if bapt_cert_data := catechizing_data.BaptismalCertificate:
            priest_doc = ParishPriestDocument.objects(id=bapt_cert_data.ParishPriest.id).first() if bapt_cert_data.ParishPriest else None
            book_doc = BaptismalBookEmbedded(**bapt_cert_data.BaptismalBook.model_dump()) if bapt_cert_data.BaptismalBook else None
            baptismal_cert_doc = BaptismalCertificateDocument(
                IssueDate=bapt_cert_data.IssueDate,
                ParishPriest=priest_doc,
                BaptismalBook=book_doc
            )

        # PASO 6: Ensamblar y guardar el documento principal de Catequizando con las referencias correctas.
        catechizing_doc = CatechizingDocument(
            Person=person_doc,
            Class=class_doc,
            IsLegitimate=catechizing_data.IsLegitimate,
            SiblingsNumber=catechizing_data.SiblingsNumber,
            ChildNumber=catechizing_data.ChildNumber,
            PayedLevelCourse=catechizing_data.PayedLevelCourse,
            School=school_doc,
            DataSheetInformation=catechizing_data.DataSheetInformation,
            HealthInformation=health_info_doc,
            BaptismalCertificate=baptismal_cert_doc,
            Parent=parent_docs,         # <--- Lista de ParentDocuments creados
            Godparent=godparent_docs,   # <--- Lista de GodparentDocuments creados
            Sacrament=sacrament_docs,
            # Las listas vacías se inicializan así por defecto
            LevelCertificate=[],
            AttendedClass=[],
            ParticularClass=[]
        ).save()
        
        return self._to_dto(catechizing_doc, CatechizingDTO)
    
    # --- Parish Methods ---
    def register_parish(self, parish_data: ParishDTO) -> ParishDTO:
        # (Implementación ya proporcionada en la respuesta anterior, se mantiene igual)
        logo_path = None
        try:
            if parish_data.LogoImage: logo_path = upload_image(parish_data.LogoImage)
            address_doc = None
            if addr_data := parish_data.Address:
                location_doc = LocationDocument(**addr_data.Location.to_dict())
                address_doc = AddressDocument(MainStreet=addr_data.MainStreet, Number=addr_data.Number, SecondStreet=addr_data.SecondStreet, Location=location_doc)
            
            parish_doc, created = ParishDocument.objects.get_or_create(Name=parish_data.Name, defaults={'Address': address_doc, 'Logo': logo_path})
                    
            if not created and logo_path: delete_image(logo_path)
            return self._to_dto(parish_doc, ParishDTO, include=['Address.Location'])
        except NotUniqueError:
            if logo_path: delete_image(logo_path)
            raise DuplicateColumnException("Parish", {"Name": parish_data.Name})
        except Exception:
            if logo_path: delete_image(logo_path)
            raise

    def get_parish_by_id(self, parish_id: str) -> Optional[ParishDTO]:
        doc = ParishDocument.objects(id=parish_id).first()
        return self._to_dto(doc, ParishDTO, include=['Address.Location'])

    def get_all_parishes(self, include: list[str] = []) -> List[ParishDTO]:
        return [self._to_dto(doc, ParishDTO, include) for doc in ParishDocument.objects.all()]

    def update_parish(self, parish_id: str, parish_data: ParishDTO) -> Optional[ParishDTO]:
        parish_doc = ParishDocument.objects(id=parish_id).first()
        
        if not parish_doc: return None

        # Creación de documento address, para ingresarlo en el campo Address de Parish
        address_doc = None
        if addr_data := parish_data.Address:
            location_doc = LocationDocument(**addr_data.Location.to_dict())
            address_doc = AddressDocument(MainStreet=addr_data.MainStreet, Number=addr_data.Number, SecondStreet=addr_data.SecondStreet, Location=location_doc)
        
        parish_doc.Logo = parish_data.Logo
        parish_doc.Name = parish_data.Name
        parish_doc.Address = address_doc

        parish_doc.save()
        return self._to_dto(parish_doc, ParishDTO)

    def delete_parish(self, parish_id: str) -> bool:
        result = ParishDocument.objects(id=parish_id).delete()
        return result > 0

    # --- Parish Priest Methods ---
    def register_parish_priest(self, priest_data: ParishPriestDTO) -> ParishPriestDTO:
        person_doc = self._get_or_create_person(priest_data.Person)
        parish_doc = ParishDocument.objects(id=priest_data.Parish.id).first()
        if not parish_doc: raise ValueError("Parish not found")

        user_doc = UserDocument(Username=priest_data.User.Username,Role="ParishPriest")
        user_doc.set_password(priest_data.User.Password)
        user_doc.save()

        priest_doc = ParishPriestDocument(Person=person_doc, User=user_doc, Parish=parish_doc).save()
        return self._to_dto(priest_doc, ParishPriestDTO)

    def get_parish_priest_by_id(self, user_id: str) -> Optional[ParishPriestDTO]:
        doc = ParishPriestDocument.objects(User=user_id).first()
        return self._to_dto(doc, ParishPriestDTO)

    ## Revisar si funciona adecuadamente
    def get_parish_priests_by_parish(self, parish_id: str) -> List[ParishPriestDTO]:
        priest_docs = ParishPriestDocument.objects(Parish=parish_id).select_related()
        return [self._to_dto(doc, ParishPriestDTO) for doc in priest_docs]

    def get_all_parish_priests(self) -> List[ParishPriestDTO]:
        return [self._to_dto(doc, ParishPriestDTO) for doc in ParishPriestDocument.objects.all()]

    # --- REVISAR
    def update_parish_priest(self, priest_id: str, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        priest_doc = ParishPriestDocument.objects(id=priest_id).first()

        if not priest_doc: return None
        if priest_data.Parish and priest_doc.Parish.id != priest_data.Parish.id:
            new_parish = ParishDocument.objects(id=priest_data.Parish.id).first()
            if new_parish: priest_doc.Parish = new_parish
        priest_doc.save()

        return self._to_dto(priest_doc, ParishPriestDTO)

    def delete_parish_priest(self, priest_id: str) -> bool:
        result = ParishPriestDocument.objects(id=priest_id).delete()
        return result > 0

    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        person_doc = self._get_or_create_person(catechist_data.Person)
        parish_doc = self.get_parish_by_id(catechist_data.Parish)

        user_doc = UserDocument(Username=catechist_data.User.Username, Role="Catechist")
        user_doc.set_password(catechist_data.User.Password)
        user_doc.save()

        # PROBAR
        catechist_doc = CatechistDocument(Person=person_doc, User=user_doc, Parish=parish_doc).save()
        return self._to_dto(catechist_doc, CatechistDTO)

    def get_catechist_by_id(self, catechist_id: str, include: list[str] = []) -> Optional[CatechistDTO]:
        doc = CatechistDocument.objects(id=catechist_id).first()
        return self._to_dto(doc, CatechistDTO, include)

    def get_all_catechists(self, include: list[str] = []) -> List[CatechistDTO]:
        return [self._to_dto(doc, CatechistDTO, include) for doc in CatechistDocument.objects.all()]
    
    # Probar
    def update_catechist(self, catechist_id: str, catechist_data: CatechistDTO) -> Optional[CatechistDTO]:
        # La lógica de actualización puede ser tan simple o compleja como necesites.
        # Por ejemplo, actualizar el email de la persona asociada.
        catechist_doc = CatechistDocument.objects(id=catechist_id).first()
        if not catechist_doc: return None
        
        if person_dto := catechist_data.Person:
            person_doc = catechist_doc.Person
            if person_dto.EmailAddress:
                person_doc.EmailAddress = person_dto.EmailAddress
                catechist_doc.Person = person_doc
            person_doc.save()

        if parish_dto := catechist_data.Parish:
            if parish_dto.id and catechist_doc.Parish.id != parish_dto.id:
                try:
                    new_parish_doc = self.get_parish_by_id(parish_id=parish_dto.id)
                    catechist_doc.Parish = new_parish_doc
                except:
                    logging.warning(f"Se intentó asignar una parroquia inexistente (ID: {parish_dto.id}) al catequista {catechist_id}")

        catechist_doc.save()
        
        return self._to_dto(catechist_doc.fetch_reload(), CatechistDTO)

    def delete_catechist(self, catechist_id: str) -> bool:
        result = CatechistDocument.objects(id=catechist_id).delete()
        return result > 0

    def get_catechizing_by_id(self, catechizing_id: str, include: list[str] = []) -> Optional[CatechizingDTO]:
        doc = CatechizingDocument.objects(id=catechizing_id).first()
        return self._to_dto(doc, CatechizingDTO, include)

    def get_catechizings_by_class(self, class_id: str) -> List[CatechizingDTO]:
        docs = CatechizingDocument.objects(Class=class_id).select_related()
        return [self._to_dto(doc, CatechizingDTO) for doc in docs]

    def get_all_sacraments(self) -> List[SacramentDTO]:
        return [self._to_dto(doc, SacramentDTO) for doc in SacramentDocument.objects.all()]

    # Revisar
    def get_catechizings_by_parish(self, parish_id: str, include: list[str] = []) -> List[CatechizingDTO]:
        try:
            parish = ParishDocument.objects.get(id=parish_id)
            
            classrooms = parish.Classroom

            if not classrooms:
                return []
            
            classes = ClassDocument.objects(Schedule__Classroom__in=classrooms).select_related()
            
            if not classes:
                return []
            
            docs = CatechizingDocument.objects(Class__in=classes).select_related(max_depth=2)

            if not docs:
                return[]
            
            return [self._to_dto(doc, CatechizingDTO, include) for doc in docs]
        except DoesNotExist:
            # Si la parroquia con el ID proporcionado no existe, devolvemos una lista vacía.
            logging.warning(f"Se buscaron aulas para una parroquia inexistente con ID: {parish_id}")
            return []
        
    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        return [self._to_dto(doc, CatechizingDTO, include) for doc in CatechizingDocument.objects.all()]

    def update_catechizing(self, catechizing_id: str, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        """
        Actualiza un documento Catequizing.
        CORREGIDO: Maneja DTOs parciales para no sobrescribir datos no deseados.
        """
        try:
            doc_to_update = CatechizingDocument.objects.get(id=catechizing_id)
        except DoesNotExist:
            logging.error(f"Se intentó actualizar un catequizando inexistente con ID: {catechizing_id}")
            return None

        # --- 2. Actualizar campos simples y directos (con verificación) ---
        
        if catechizing_data.PayedLevelCourse is not None:
            doc_to_update.PayedLevelCourse = catechizing_data.PayedLevelCourse
            
        if catechizing_data.DataSheetInformation is not None:
            doc_to_update.DataSheetInformation = catechizing_data.DataSheetInformation


        # --- 3. Actualizar el documento referenciado 'Person' ---
        if person_dto := catechizing_data.Person:
            person_doc = doc_to_update.Person
            if person_doc:
                if person_dto.EmailAddress:
                    person_doc.EmailAddress = person_dto.EmailAddress
                
                if addr_dto := person_dto.Address:
                    loc_dto = addr_dto.Location
                    location_doc = LocationDocument(Province=loc_dto.Province, State=loc_dto.State, Country=loc_dto.Country)
                    person_doc.Address = AddressDocument(MainStreet=addr_dto.MainStreet, Number=addr_dto.Number, SecondStreet=addr_dto.SecondStreet, Location=location_doc)
                
                if phone_dto := person_dto.PhoneNumber:
                    phone_type_doc = None
                    if phone_dto.PhoneNumberType and phone_dto.PhoneNumberType.id:
                        phone_type_doc = PhoneNumberTypeDocument.objects(id=phone_dto.PhoneNumberType.id).first()
                    person_doc.PhoneNumber = PhoneNumberDocument(PhoneNumber=phone_dto.PhoneNumber, PhoneNumberType=phone_type_doc)
                
                person_doc.save()

        # --- 4. Actualizar la referencia a 'Class' ---
        if class_dto := catechizing_data.Class:
            if class_dto.id and (not doc_to_update.Class or doc_to_update.Class.id != class_dto.id):
                try:
                    new_class_doc = ClassDocument.objects.get(id=class_dto.id)
                    doc_to_update.Class = new_class_doc
                except DoesNotExist:
                    logging.warning(f"Se intentó asignar una clase inexistente (ID: {class_dto.id}) al catequizando {catechizing_id}")

        # --- 5. Actualizar documentos embebidos ---
        if school_dto := catechizing_data.School:
            doc_to_update.School = SchoolEmbedded(
                SchoolYear=school_dto.SchoolYear,
                SchoolName=school_dto.SchoolName
            )
            
        if health_dto := catechizing_data.HealthInformation:
            emergency_contact_doc = None
            if health_dto.EmergencyContact and health_dto.EmergencyContact.id:
                emergency_contact_doc = PersonDocument.objects.with_id(health_dto.EmergencyContact.id)
                if not emergency_contact_doc:
                    pass
                
            doc_to_update.HealthInformation = HealthInformationEmbedded(
                ImportantAspects=health_dto.ImportantAspects,
                BloodType=health_dto.BloodType,
                Allergy=health_dto.Allergy,
                EmergencyContact=emergency_contact_doc
            )

        # --- 6. Guardar el documento Catechizing principal ---
        try:
            doc_to_update.save()
        except Exception as e:
            logging.error(f"Error al guardar las actualizaciones para el catequizando {catechizing_id}: {e}")
            return None

        # --- 7. Devolver el DTO con los datos actualizados ---
        final_doc = doc_to_update.fetch_reload()
        return self._to_dto(final_doc, CatechizingDTO, include=[
            "Person.Address.Location", 
            "Person.PhoneNumber.PhoneNumberType", 
            "Class.Level", "Class.Schedule",
            "HealthInformation.EmergencyContact"
        ])

    def delete_catechizing(self, catechizing_id: str) -> bool:
        result = CatechizingDocument.objects(id=catechizing_id).delete()
        return result > 0

    # --- Métodos Auxiliares ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        doc = PersonDocument.objects(DNI=dni).first()
        return self._to_dto(doc, PersonDTO)

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        doc = UserDocument.objects(Username=username).select_related().first()
        return self._to_dto(doc, UserDTO)
    
    def get_role(self, role: str) -> str:
        user_role = UserDocument.objects(Role=role).first()
        return user_role if user_role else None
    
    def get_all_phone_number_types(self) -> List[PhoneNumberTypeDTO]:
        return [self._to_dto(doc, PhoneNumberTypeDTO) for doc in PhoneNumberTypeDocument.objects.all()]

    def get_level_by_name(self, level_name: str) -> Optional[LevelDTO]:
        doc = LevelDocument.objects(Name=level_name).first()
        return self._to_dto(doc, LevelDTO)

    def get_class_by_id(self, class_id: str) -> Optional[ClassDTO]:
        doc = ClassDocument.objects(id=class_id).select_related().first()
        return self._to_dto(doc, ClassDTO)
    
    def register_class(self, class_data: ClassDTO) -> ClassDTO:
        """
        Registra una nueva clase en la base de datos.
        """
        try:
            # 1. Obtener los documentos de referencia a partir de los IDs en el DTO
            class_period_doc = ClassPeriodDocument.objects.get(id=class_data.ClassPeriod.id)
            level_doc = LevelDocument.objects.get(id=class_data.Level.id)
            catechist_doc = CatechistDocument.objects.get(id=class_data.Catechist.id)
            support_person_doc = SupportPersonDocument.objects.get(id=class_data.SupportPerson.id) if class_data.SupportPerson else None
            classroom_doc = ClassroomDocument.objects.get(id=class_data.Schedule.Classroom.id)

            # 2. Construir el documento embebido del horario
            schedule_embedded = ScheduleEmbedded(
                DayOfTheWeek=class_data.Schedule.DayOfTheWeek,
                StartHour=class_data.Schedule.StartHour,
                EndHour=class_data.Schedule.EndHour,
                Classroom=classroom_doc
            )

            # 3. Crear y guardar el documento principal de la clase
            new_class_doc = ClassDocument(
                ClassPeriod=class_period_doc,
                Level=level_doc,
                Catechist=catechist_doc,
                SupportPerson=support_person_doc,
                Schedule=schedule_embedded
            ).save()

            return self._to_dto(new_class_doc, ClassDTO)
        except DoesNotExist as e:
            logging.error(f"Error de referencia al registrar clase: un ID proporcionado no existe. Detalles: {e}")
            raise ValueError(f"No se pudo registrar la clase. Referencia no encontrada: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al registrar clase: {e}")
            raise

    def get_all_periods(self) -> List[ClassPeriodDTO]:
        return [self._to_dto(doc, ClassPeriodDTO) for doc in ClassPeriodDocument.objects.order_by('-EndDate')]

    def get_all_levels(self) -> List[LevelDTO]:
        return [self._to_dto(doc, LevelDTO) for doc in LevelDocument.objects.order_by('MinAge')]

    def get_all_support_persons(self, include: list[str] = []) -> List[SupportPersonDTO]:
        return [self._to_dto(doc, SupportPersonDTO, include) for doc in SupportPersonDocument.objects.all()]

    def get_classrooms_by_parish(self, parish_id: str) -> List[ClassroomDTO]:
        """
        Obtiene una lista de todas las aulas asociadas directamente a una parroquia específica.
        Esta implementación se basa en el nuevo esquema donde Parish contiene una lista de referencias a Classroom.
        """
        try:
            # 1. Buscamos la parroquia específica por su ID.
            parish_doc = ParishDocument.objects.get(id=parish_id)

            # 2. Accedemos directamente a la lista de referencias.
            # MongoEngine carga los documentos Classroom completos automáticamente.
            classroom_docs = parish_doc.Classroom

            # Si la parroquia no tiene aulas, devolvemos una lista vacía.
            if not classroom_docs:
                return []

            # 3. Convertimos cada documento de aula en un DTO.
            # No es necesario un 'include' complejo aquí, ya que el ClassroomDTO es simple.
            return [self._to_dto(doc, ClassroomDTO) for doc in classroom_docs]

        except DoesNotExist:
            # Si la parroquia con el ID proporcionado no existe, devolvemos una lista vacía.
            logging.warning(f"Se buscaron aulas para una parroquia inexistente con ID: {parish_id}")
            return []
        
    def get_class_period_by_id(self, period_id: str) -> Optional[ClassPeriodDTO]:
        doc = ClassPeriodDocument.objects(id=period_id).first()
        return self._to_dto(doc, ClassPeriodDTO)

    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        person_doc = self._get_or_create_person(support_person_data.Person)
        support_doc = SupportPersonDocument(Person=person_doc).save()
        return self._to_dto(support_doc, SupportPersonDTO)

    def get_classes_by_parish_id(self, parish_id: str, include: list[str] = []) -> List[ClassDTO]:
        """
        Obtiene todas las clases de una parroquia específica basándose en la nueva
        estructura de modelos, donde Parish contiene la lista de sus Classrooms.
        """
        try:
            # 1. Buscamos el documento de la parroquia por su ID para empezar.
            parish_doc = ParishDocument.objects.get(id=parish_id)

            # 2. Obtenemos la lista de documentos de aulas directamente desde la parroquia.
            # MongoEngine se encarga de cargar los objetos ClassroomDocument completos.
            classrooms_in_parish = parish_doc.Classroom

            # Si la parroquia no tiene aulas registradas, devolvemos una lista vacía.
            if not classrooms_in_parish:
                return []

            # 3. Buscamos todas las clases cuyo campo 'Schedule.ClassRoom' esté en nuestra lista de aulas.
            docs = ClassDocument.objects(Schedule__Classroom__in=classrooms_in_parish).select_related(max_depth=3)
            
            return [self._to_dto(doc, ClassDTO, include) for doc in docs]

        except DoesNotExist:
            logging.warning(f"Se buscaron clases para una parroquia inexistente con ID: {parish_id}")
            return [] # Si no se encuentra la parroquia, no hay clases que devolver.
        except Exception as e:
            logging.error(f"Error al obtener clases por parish_id '{parish_id}': {e}")
            return []
    
    def get_classes_by_catechist_id(self, catechist_id: str, include: list[str] = []) -> List[ClassDTO]:
        """
        Obtiene todas las clases asignadas a un catequista específico.
        """
        try:
            # coincide con el ID del catequista proporcionado.
            docs = ClassDocument.objects(Catechist=catechist_id).select_related(max_depth=3)
            return [self._to_dto(doc, ClassDTO, include) for doc in docs]
        except Exception as e:
            logging.error(f"Error al obtener clases para el catequista {catechist_id}: {e}")
            return []
    
    def get_catechists_by_parish_id(self, parish_id: str, include: list[str] = []) -> List[CatechistDTO]:
        docs = CatechistDocument.objects(Parish=parish_id).select_related()
        return [self._to_dto(doc, CatechistDTO, include) for doc in docs]
    
    def get_support_persons_by_parish_id(self, parish_id: str, include: list[str] = []) -> List[SupportPersonDTO]:
        docs = SupportPersonDocument.objects(Parish=parish_id).select_related()
        return [self._to_dto(doc, SupportPersonDTO, include) for doc in docs]

    def check_user_login(self, user_data: UserDTO) -> bool:
        user_doc = UserDocument.objects(Username=user_data.Username).first()
        if not user_doc:
            return False
        return user_doc.check_password(user_data.Password)

    def get_dto_by_user(self, username: str):
        try:
            # user_doc = UserDocument.objects.get(Username=username).select_related()
            user_doc = UserDocument.objects.get(Username=username)
        except DoesNotExist:
            return None
        
        role = user_doc.Role
        doc = None
        dto_class = None

        try:
            if role == "Administrator":
                doc = AdministratorDocument.objects.get(User=user_doc)
                dto_class = AdministratorDTO
            elif role == "Catechist":
                doc = CatechistDocument.objects.get(User=user_doc)
                dto_class = CatechistDTO
            elif role == "ParishPriest":
                doc = ParishPriestDocument.objects.get(User=user_doc)
                dto_class = ParishPriestDTO
            else:
                return None
        except DoesNotExist:
            logging.error(f"Inconsistencia de datos: El usuario '{username}' tiene el rol '{role}' pero no se encontró el documento de rol correspondiente.")
            return None        

        return self._to_dto(doc, dto_class, include=['User', 'Role'])
    
    # def get_blood_type_by_id(self, blood_type_id: int) -> Optional[BloodTypeDTO]:
    #     logging.warning("Llamada a un método no aplicable (get_blood_type_by_id). BloodType es un documento embebido.")
    #     return None

    def get_all_blood_types(self) -> List[BloodTypeDTO]:
        types = [
            "O+",
            "O-",
            "A+",
            "A-",
            "AB",
        ]
        return [BloodTypeDTO(Type=type) for type in types]

    def get_phone_number_type_by_id(self, phone_number_type_id: str) -> Optional[PhoneNumberTypeDTO]:
        try:
            doc = PhoneNumberTypeDocument.objects(id=phone_number_type_id).first()
            return self._to_dto(doc, PhoneNumberTypeDTO)
        except Exception as e:
            logging.error(f"Error al obtener tipo de teléfono por ID '{phone_number_type_id}': {e}")
            return None

    def get_all_day_of_the_week(self) -> List[DayOfTheWeekDTO]:
        days = [
            "Lunes", "Martes", "Miércoles", "Jueves", 
            "Viernes", "Sábado", "Domingo"
        ]
        return [DayOfTheWeekDTO(Day=day) for day in days]