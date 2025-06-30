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

    def _to_dto(self, document, dto_class, include: list[str] = [], exclude: list[str] = []):
        if not document:
            return None
        return dto_class.from_other_obj(document, include=include + ['id'], exclude=exclude)

    def _get_or_create_person(self, person_data: PersonDTO) -> PersonDocument:
        if person_data.DNI and (doc := PersonDocument.objects(DNI=person_data.DNI).first()):
            return doc
        if person_data.EmailAddress and (doc := PersonDocument.objects(EmailAddress=person_data.EmailAddress).first()):
            return doc

        address_doc = None
        if addr_data := person_data.Address:
            location_doc = LocationDocument(**addr_data.Location.to_dict()) if addr_data.Location else None
            address_doc = AddressDocument(MainStreet=addr_data.MainStreet, Number=addr_data.Number, SecondStreet=addr_data.SecondStreet, Location=location_doc)
        
        phone_doc = None
        if phone_data := person_data.PhoneNumber:
            phone_type_doc = PhoneNumberTypeDocument.objects(id=phone_data.PhoneNumberType.id).first()
            phone_doc = PhoneNumberDocument(PhoneNumber=phone_data.PhoneNumber, PhoneNumberType=phone_type_doc)

        birth_location_doc = None
        if birth_loc_data := person_data.BirthLocation:
            birth_location_doc = LocationDocument(**birth_loc_data.to_dict())

        new_person = PersonDocument(
            FirstName=person_data.FirstName, MiddleName=person_data.MiddleName,
            FirstSurname=person_data.FirstSurname, SecondSurname=person_data.SecondSurname,
            BirthDate=person_data.BirthDate, DNI=person_data.DNI, Gender=person_data.Gender,
            EmailAddress=person_data.EmailAddress, Address=address_doc,
            PhoneNumber=phone_doc, BirthLocation=birth_location_doc
        ).save()
        
        return new_person

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

    # --- Catechizing Methods ---
    # def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
    #     person_doc = self._get_or_create_person(catechizing_data.Person)
        
    #     # Obtener los objetos de referencia
    #     class_doc = ClassDocument.objects(id=catechizing_data.Class.id).first()
    #     parent_docs = [ParentDocument.objects(id=p.id).first() for p in catechizing_data.Parent]
    #     godparent_docs = [GodparentDocument.objects(id=g.id).first() for g in catechizing_data.Godparent]
    #     sacrament_docs = [SacramentDocument.objects(id=s.id).first() for s in catechizing_data.Sacrament]
        
    #     # Construir documentos embebidos
    #     school_doc = SchoolEmbedded(**catechizing_data.SchoolClassYear.to_dict(exclude={'id'}))
    #     health_info_doc = HealthInformationEmbedded(**catechizing_data.HealthInformation.to_dict(exclude={'id'}))
    #     data_shet_doc = DataSheetEmbedded(**catechizing_data.DataSheet.to_dict(exclude={'id'}))
    #     baptismal_certificate_doc = BaptismalCertificateDocument(**catechizing_data.BaptismalCertificate.to_dict(exclude={'id'}))
        
    #     level_certificate_list = [LevelCertificateDocument(**catechizing_data.LevelCertificate.to_dict(exclude={'id'}))]
    #     particular_class_list = [ParticularClassEmbedded(**catechizing_data.ParticularClass.to_dict(exclude={'id'}))]
    #     attended_class_list = [AttendedClassEmbedded(**catechizing_data.AttendedClass.to_dict(exclude={'id'}))]
        
        
    #     catechizing_doc = CatechizingDocument(
    #         Person=person_doc,
    #         Class=class_doc,
    #         Parent=parent_docs,
    #         Godparent=godparent_docs,
    #         Sacrament=sacrament_docs,
    #         IsLegitimate=catechizing_data.IsLegitimate,
    #         SiblingsNumber=catechizing_data.SiblingsNumber,
    #         ChildNumber=catechizing_data.ChildNumber,
    #         PayedLevelCourse=catechizing_data.PayedLevelCourse,
    #         SchoolClassYear=school_doc,
    #         DataSheet=data_shet_doc,
    #         HealthInformation=health_info_doc,
    #         BaptismalCertificate=baptismal_certificate_doc,
    #         ParticularClass=particular_class_list,
    #         AttendedClass=attended_class_list,
    #         LevelCertificate=level_certificate_list
    #     ).save()
        
    #     return self._to_dto(catechizing_doc, CatechizingDTO)

    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        person_doc = self._get_or_create_person(catechizing_data.Person)
        
        # Obtener los objetos de referencia principales
        class_doc = ClassDocument.objects(id=catechizing_data.Class.id).first() if catechizing_data.Class else None
        parent_docs = [ParentDocument.objects(id=p.id).first() for p in catechizing_data.Parent if p.id]
        godparent_docs = [GodparentDocument.objects(id=g.id).first() for g in catechizing_data.Godparent if g.id]
        sacrament_docs = [SacramentDocument.objects(id=s.id).first() for s in catechizing_data.Sacrament if s.id]
        level_certificate_docs = [ClassDocument.objects(id=c.id).first() for c in catechizing_data.LevelCertificate if c.id]

        # --- Construir documentos embebidos con la nueva estructura ---

        # CAMBIO: School ahora es un objeto simple
        school_doc = None
        if school_data := catechizing_data.School:
            school_doc = SchoolEmbedded(**school_data.model_dump())
            
        # CAMBIO: HealthInformation simplificado
        health_info_doc = None
        if health_data := catechizing_data.HealthInformation:
            contact_person_doc = PersonDocument.objects(id=health_data.EmergencyContact.id).first() if health_data.EmergencyContact else None
            health_info_doc = HealthInformationEmbedded(
                ImportantAspects=health_data.ImportantAspects,
                BloodType=health_data.BloodType,
                EmergencyContact=contact_person_doc,
                Allergy=health_data.Allergy  # Se pasa la lista de strings directamente
            )

        # CAMBIO: BaptismalCertificate con estructura aplanada
        baptismal_cert_doc = None
        if bapt_cert_data := catechizing_data.BaptismalCertificate:
            priest_doc = ParishPriestDocument.objects(id=bapt_cert_data.ParishPriest.id).first() if bapt_cert_data.ParishPriest else None
            book_doc = BaptismalBookEmbedded(**bapt_cert_data.BaptismalBook.model_dump()) if bapt_cert_data.BaptismalBook else None
            baptismal_cert_doc = BaptismalCertificateDocument(
                IssueDate=bapt_cert_data.IssueDate,
                ParishPriest=priest_doc,
                BaptismalBook=book_doc
            )
            
        # Construir listas de embebidos (sin cambios aquí)
        attended_class_list = [AttendedClassEmbedded(**ac.model_dump()) for ac in catechizing_data.AttendedClass]
        particular_class_list = [ParticularClassEmbedded(**pc.model_dump()) for pc in catechizing_data.ParticularClass]
        
        catechizing_doc = CatechizingDocument(
            Person=person_doc,
            Class=class_doc,
            IsLegitimate=catechizing_data.IsLegitimate,
            SiblingsNumber=catechizing_data.SiblingsNumber,
            ChildNumber=catechizing_data.ChildNumber,
            PayedLevelCourse=catechizing_data.PayedLevelCourse,
            School=school_doc,
            DataSheet=catechizing_data.DataSheet,
            HealthInformation=health_info_doc,
            BaptismalCertificate=baptismal_cert_doc,
            Parent=parent_docs,
            Godparent=godparent_docs,
            Sacrament=sacrament_docs,
            LevelCertificate=level_certificate_docs,
            AttendedClass=attended_class_list,
            ParticularClass=particular_class_list
        ).save()
        
        
        return self._to_dto(catechizing_doc, CatechizingDTO)

    def get_catechizing_by_id(self, catechizing_id: str) -> Optional[CatechizingDTO]:
        doc = CatechizingDocument.objects(id=catechizing_id).first()
        return self._to_dto(doc, CatechizingDTO)

    def get_catechizings_by_class(self, class_id: str) -> List[CatechizingDTO]:
        docs = CatechizingDocument.objects(Class=class_id).select_related()
        return [self._to_dto(doc, CatechizingDTO) for doc in docs]

    # Revisar
    def get_catechizings_by_parish(self, parish_id: str, include: list[str] = []) -> List[CatechizingDTO]:
        classrooms = ClassroomDocument.objects(Parish=parish_id).select_related()
        classes = ClassDocument.objects(Schedule__ClassRoom__in=classrooms).select_related()
        docs = CatechizingDocument.objects(Class__in=classes).select_related(max_depth=2)
        return [self._to_dto(doc, CatechizingDTO, include) for doc in docs]

    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        # return [self._to_dto(doc, CatechizingDTO, include) for doc in CatechizingDocument.objects.select_related()]
        return [self._to_dto(doc, CatechizingDTO, include) for doc in CatechizingDocument.objects.all()]

    # def update_catechizing(self, catechizing_id: str, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
    #     try:
    #         doc = CatechizingDocument.objects(id=catechizing_id).first()
            
    #         if not doc: return None
    #         doc.PayedLevelCourse = catechizing_data.PayedLevelCourse
            
    #         doc.save()
    #         doc.reload()
            
    #     except:
    #         raise
    #     finally:
    #         return self._to_dto(doc, CatechizingDTO)

    # mongodb_dal.py -> DENTRO DE LA CLASE MongoDBDAL

    def update_catechizing(self, catechizing_id: str, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        """
        Actualiza un documento Catequizing existente en la base de datos.
        Maneja la actualización de campos simples, embebidos y referenciados.
        """
        try:
            # 1. Obtener el documento original de la base de datos que se va a actualizar.
            doc_to_update = CatechizingDocument.objects.get(id=catechizing_id)
        except DoesNotExist:
            logging.error(f"Se intentó actualizar un catequizando inexistente con ID: {catechizing_id}")
            return None

        # --- 2. Actualizar campos simples y directos ---
        # Estos campos vienen directamente del formulario de actualización.
        doc_to_update.SiblingsNumber = catechizing_data.SiblingsNumber
        doc_to_update.PayedLevelCourse = catechizing_data.PayedLevelCourse
        doc_to_update.DataSheet = catechizing_data.DataSheet

        # --- 3. Actualizar el documento referenciado 'Person' ---
        # No cambiamos la referencia, sino los datos DENTRO del documento Person.
        if person_dto := catechizing_data.Person:
            person_doc = doc_to_update.Person
            if not person_doc: # Verificación de seguridad
                logging.error(f"Inconsistencia de datos: Catequizando {catechizing_id} no tiene Persona asociada.")
            else:
                person_doc.EmailAddress = person_dto.EmailAddress
                
                # Actualizar el documento embebido Address dentro de Person
                if addr_dto := person_dto.Address:
                    loc_dto = addr_dto.Location
                    location_doc = LocationDocument(Province=loc_dto.Province, State=loc_dto.State, Country=loc_dto.Country)
                    person_doc.Address = AddressDocument(MainStreet=addr_dto.MainStreet, Number=addr_dto.Number, SecondStreet=addr_dto.SecondStreet, Location=location_doc)
                
                # Actualizar el documento embebido PhoneNumber dentro de Person
                if phone_dto := person_dto.PhoneNumber:
                    phone_type_doc = PhoneNumberTypeDocument.objects(id=phone_dto.PhoneNumberType.id).first()
                    person_doc.PhoneNumber = PhoneNumberDocument(PhoneNumber=phone_dto.PhoneNumber, PhoneNumberType=phone_type_doc)
                
                # Guardamos el documento Person modificado
                person_doc.save()

        # --- 4. Actualizar la referencia a 'Class' ---
        # Aquí sí cambiamos a qué documento 'Class' apunta el catequizando.
        if class_dto := catechizing_data.Class:
            if class_dto.id and (not doc_to_update.Class or doc_to_update.Class.id != class_dto.id):
                try:
                    new_class_doc = ClassDocument.objects.get(id=class_dto.id)
                    doc_to_update.Class = new_class_doc
                except DoesNotExist:
                    logging.warning(f"Se intentó asignar una clase inexistente (ID: {class_dto.id}) al catequizando {catechizing_id}")

        # --- 5. Actualizar documentos embebidos ---
        
        # Actualizar School (antes SchoolClassYear)
        if school_dto := catechizing_data.School:
            doc_to_update.School = SchoolEmbedded(
                SchoolYear=school_dto.SchoolYear,
                SchoolName=school_dto.SchoolName
            )
            
        # Actualizar HealthInformation
        if health_dto := catechizing_data.HealthInformation:
            emergency_contact_doc = None
            if health_dto.EmergencyContact and health_dto.EmergencyContact.id:
                emergency_contact_doc = PersonDocument.objects(id=health_dto.EmergencyContact.id).first()
                
            doc_to_update.HealthInformation = HealthInformationEmbedded(
                ImportantAspects=health_dto.ImportantAspects,
                BloodType=health_dto.BloodType,
                Allergy=health_dto.Allergy, # Es una lista de strings, se asigna directamente
                EmergencyContact=emergency_contact_doc
            )

        # --- 6. Guardar el documento Catechizing principal ---
        # Este 'save' persiste todos los cambios realizados en doc_to_update (como el cambio de Class).
        try:
            doc_to_update.save()
        except Exception as e:
            logging.error(f"Error al guardar las actualizaciones para el catequizando {catechizing_id}: {e}")
            return None # O manejar el error de forma más específica

        # --- 7. Devolver el DTO con los datos actualizados ---
        # Usamos fetch_reload() para asegurar que obtenemos la versión más reciente de la BDD.
        # El 'include' es crucial para que el DTO devuelto venga con todos los datos anidados.
        final_doc = doc_to_update.fetch_reload()
        return self._to_dto(final_doc, CatechizingDTO, include=[
            "Person.Address.Location", 
            "Person.PhoneNumber.PhoneNumberType", 
            "Class.Level", 
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
        # Role es un EmbeddedDocument, no se puede consultar directamente. Se busca un usuario con ese rol.
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

    def get_all_periods(self) -> List[ClassPeriodDTO]:
        return [self._to_dto(doc, ClassPeriodDTO) for doc in ClassPeriodDocument.objects.order_by('-EndDate')]

    def get_all_levels(self) -> List[LevelDTO]:
        return [self._to_dto(doc, LevelDTO) for doc in LevelDocument.objects.order_by('MinAge')]

    def get_all_support_persons(self, include: list[str] = []) -> List[SupportPersonDTO]:
        return [self._to_dto(doc, SupportPersonDTO, include) for doc in SupportPersonDocument.objects.all()]

    def get_classroom_in_parish(self, parish_id: str) -> List[ClassroomDTO]:
        docs = ClassroomDocument.objects(Parish=parish_id)
        return [self._to_dto(doc, ClassroomDTO) for doc in docs]

    def get_class_period_by_id(self, period_id: str) -> Optional[ClassPeriodDTO]:
        doc = ClassPeriodDocument.objects(id=period_id).first()
        return self._to_dto(doc, ClassPeriodDTO)

    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        person_doc = self._get_or_create_person(support_person_data.Person)
        support_doc = SupportPersonDocument(Person=person_doc).save()
        return self._to_dto(support_doc, SupportPersonDTO)

    # def get_classes_by_parish_id(self, parish_id: str, include: list[str] = []) -> List[ClassDTO]:
    #     # classrooms = ClassroomDocument.objects(Parish=parish_id).select_related()
    #     docs = ClassDocument.objects(Schedule__Classroom__Parish=parish_id).select_related(max_depth=2)
    #     return [self._to_dto(doc, ClassDTO, include) for doc in docs]
    # mongodb_dal.py -> MÉTODO CORREGIDO

    def get_classes_by_parish_id(self, parish_id: str, include: list[str] = []) -> List[ClassDTO]:
        try:
            # Paso 1: Obtener todas las aulas que pertenecen a la parroquia.
            classrooms_in_parish = ClassroomDocument.objects(Parish=parish_id)
            
            if not classrooms_in_parish:
                return []

            docs = ClassDocument.objects(Schedule__ClassRoom__in=classrooms_in_parish).select_related(max_depth=3)
            
            return [self._to_dto(doc, ClassDTO, include) for doc in docs]
        except Exception as e:
            logging.error(f"Error al obtener clases por parish_id '{parish_id}': {e}")
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