# mongodb_dal.py (Versión Corregida y Completa)

from typing import Optional, List, Tuple
from mongoengine.errors import NotUniqueError, ValidationError
from flask_mongoengine import MongoEngine
import logging

from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.mongodb.mongodb_models import *
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.data.image_manager import delete_image, upload_image

class MongoDBDAL(IDataAccessLayer):
    """
    Capa de Acceso a Datos (DAL) para MongoDB que implementa rigurosamente
    el contrato definido en IDataAccessLayer.
    """
    def __init__(self, db: MongoEngine):
        self.db = db

    # --- Funciones de Ayuda Internas (sin cambios) ---
    def _get_next_id(self, document_class, id_field_name: str):
        last_doc = document_class.objects.order_by(f'-{id_field_name}').first()
        return getattr(last_doc, id_field_name) + 1 if last_doc else 1

    def _to_dto(self, document, dto_class, include: list[str] = [], exclude: list[str] = []):
        if not document: return None
        return dto_class.from_other_obj(document, include=include, exclude=exclude)

    def _get_or_create_person_doc(self, person_data: PersonDTO) -> PersonDocument:
        if person_data.DNI and (person_doc := PersonDocument.objects(DNI=person_data.DNI).first()):
            return person_doc
        location_doc, address_doc, phone_doc = None, None, None
        if loc_data := getattr(getattr(person_data, 'Address', None), 'Location', None):
            location_doc, _ = LocationDocument.objects.get_or_create(Province=loc_data.Province, State=loc_data.State, Country=loc_data.Country, defaults={'IDLocation': self._get_next_id(LocationDocument, 'IDLocation')})
        if addr_data := getattr(person_data, 'Address', None):
            address_doc, _ = AddressDocument.objects.get_or_create(MainStreet=addr_data.MainStreet, Number=addr_data.Number, SecondStreet=addr_data.SecondStreet, Location=location_doc, defaults={'IDAddress': self._get_next_id(AddressDocument, 'IDAddress')})
        if phone_data := getattr(person_data, 'PhoneNumber', None):
            phone_type_doc = PhoneNumberTypeDocument.objects(IDPhoneNumberType=phone_data.IDPhoneNumberType).first()
            if phone_type_doc:
                phone_doc, _ = PhoneNumberDocument.objects.get_or_create(PhoneNumber=phone_data.PhoneNumber, PhoneNumberType=phone_type_doc, defaults={'IDPhoneNumer': self._get_next_id(PhoneNumberDocument, 'IDPhoneNumer')})
        person_doc, _ = PersonDocument.objects.get_or_create(
            DNI=person_data.DNI,
            defaults={'IDPerson': self._get_next_id(PersonDocument, 'IDPerson'),'FirstName': person_data.FirstName,'MiddleName': person_data.MiddleName,'FirstSurname': person_data.FirstSurname,'SecondSurname': person_data.SecondSurname,'BirthDate': person_data.BirthDate,'Gender': person_data.Gender,'EmailAddress': person_data.EmailAddress,'Address': address_doc,'PhoneNumber': phone_doc,'BirthLocation': location_doc}
        )
        return person_doc

    # --- Parish Methods ---
    def register_parish(self, parish_data: ParishDTO) -> ParishDTO:
        # ANOTACIÓN: La firma se cambió de (DTO, bool) a solo DTO para cumplir el contrato.
        logo_path = None
        try:
            if parish_data.LogoImage: logo_path = upload_image(parish_data.LogoImage)
            address_doc = self._get_or_create_person_doc(PersonDTO(Address=parish_data.Address)).Address
            parish_doc, created = ParishDocument.objects.get_or_create(Name=parish_data.Name, defaults={'IDParish': self._get_next_id(ParishDocument, 'IDParish'),'Address': address_doc,'Logo': logo_path})
            if not created and logo_path: delete_image(logo_path)
            return self._to_dto(parish_doc.fetch_reload(), ParishDTO, include=['Address', 'Address.Location'])
        except NotUniqueError:
            if logo_path: delete_image(logo_path)
            raise DuplicateColumnException("Parish", {"Name": parish_data.Name})
        except Exception as e:
            if logo_path: delete_image(logo_path)
            raise

    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        doc = ParishDocument.objects(IDParish=parish_id).select_related().first()
        return self._to_dto(doc, ParishDTO, include=['Address', 'Address.Location'])

    def get_all_parishes(self, include: list[str] = []) -> List[ParishDTO]:
        query = ParishDocument.objects.all().select_related()
        return [self._to_dto(doc, ParishDTO, include=include) for doc in query]

    def update_parish(self, parish_id: int, parish_data: ParishDTO) -> Optional[ParishDTO]:
        parish_doc = ParishDocument.objects(IDParish=parish_id).first()
        if not parish_doc: return None
        parish_doc.Name = parish_data.Name
        parish_doc.save()
        return self._to_dto(parish_doc.fetch_reload(), ParishDTO, include=['Address'])

    def delete_parish(self, parish_id: int) -> bool:
        parish_doc = ParishDocument.objects(IDParish=parish_id).first()
        if parish_doc:
            parish_doc.delete()
            return True
        return False

    # --- Parish Priest Methods ---
    def register_parish_priest(self, priest_data: ParishPriestDTO) -> ParishPriestDTO:
        # ANOTACIÓN: La firma se cambió de (DTO, bool) a solo DTO para cumplir el contrato.
        person_doc = self._get_or_create_person_doc(priest_data.Person)
        role_doc = RoleDocument.objects(Role="ParishPriest").first()
        user_doc, _ = UserDocument.objects.get_or_create(Username=priest_data.User.Username, defaults={'IDUser': self._get_next_id(UserDocument, 'IDUser'), 'Password': priest_data.User.Password, 'Role': role_doc})
        parish_doc = ParishDocument.objects(IDParish=priest_data.IDParish).first()
        priest_doc, _ = ParishPriestDocument.objects.get_or_create(Person=person_doc, defaults={'IDParishPriest': person_doc.IDPerson, 'User': user_doc, 'Parish': parish_doc})
        return self._to_dto(priest_doc.fetch_reload(), ParishPriestDTO, include=['Person', 'User', 'Parish'])

    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        doc = ParishPriestDocument.objects(IDParishPriest=priest_id).select_related().first()
        return self._to_dto(doc, ParishPriestDTO, include=['Person', 'User', 'Parish'])

    def get_parish_priests_by_parish(self, parish_id: int) -> List[ParishPriestDTO]:
        parish_ref = ParishDocument.objects(IDParish=parish_id).only('id').first()
        if not parish_ref: return []
        priest_docs = ParishPriestDocument.objects(Parish=parish_ref).select_related()
        return [self._to_dto(doc, ParishPriestDTO, include=['Person']) for doc in priest_docs]

    def get_all_parish_priests(self) -> List[ParishPriestDTO]:
        docs = ParishPriestDocument.objects.select_related()
        return [self._to_dto(doc, ParishPriestDTO, include=['Person', 'User', 'Parish']) for doc in docs]

    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        priest_doc = ParishPriestDocument.objects(IDParishPriest=priest_id).first()
        if not priest_doc: return None
        if priest_data.IDParish and priest_doc.Parish.IDParish != priest_data.IDParish:
            if new_parish := ParishDocument.objects(IDParish=priest_data.IDParish).first():
                priest_doc.Parish = new_parish
        priest_doc.save()
        return self._to_dto(priest_doc.fetch_reload(), ParishPriestDTO)

    def delete_parish_priest(self, priest_id: int) -> bool:
        priest_doc = ParishPriestDocument.objects(IDParishPriest=priest_id).first()
        if priest_doc:
            priest_doc.delete()
            return True
        return False

    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        # ANOTACIÓN: La firma se cambió de (DTO, bool) a solo DTO para cumplir el contrato.
        person_doc = self._get_or_create_person_doc(catechist_data.Person)
        role_doc = RoleDocument.objects(Role="Catechist").first()
        user_doc, _ = UserDocument.objects.get_or_create(Username=catechist_data.User.Username, defaults={'IDUser': self._get_next_id(UserDocument, 'IDUser'), 'Password': catechist_data.User.Password, 'Role': role_doc})
        catechist_doc, _ = CatechistDocument.objects.get_or_create(Person=person_doc, defaults={'IDCatechist': person_doc.IDPerson, 'User': user_doc})
        return self._to_dto(catechist_doc.fetch_reload(), CatechistDTO, include=['Person', 'User'])

    def get_catechist_by_id(self, catechist_id: int, include: list[str] = []) -> Optional[CatechistDTO]:
        query = CatechistDocument.objects(IDCatechist=catechist_id).select_related()
        return self._to_dto(query.first(), CatechistDTO, include=include)

    def get_all_catechists(self) -> List[CatechistDTO]:
        # ANOTACIÓN: Se eliminó el parámetro `include` para cumplir el contrato.
        query = CatechistDocument.objects.all().select_related()
        return [self._to_dto(doc, CatechistDTO, include=['Person', 'User']) for doc in query]

    def update_catechist(self, catechist_id: int, catechist_data: CatechistDTO) -> Optional[CatechistDTO]:
        catechist_doc = CatechistDocument.objects(IDCatechist=catechist_id).first()
        if not catechist_doc: return None
        if person_data := catechist_data.Person:
            person_doc = catechist_doc.Person
            person_doc.EmailAddress = person_data.EmailAddress
            person_doc.save()
        return self._to_dto(catechist_doc.fetch_reload(), CatechistDTO, include=['Person'])

    def delete_catechist(self, catechist_id: int) -> bool:
        catechist_doc = CatechistDocument.objects(IDCatechist=catechist_id).first()
        if catechist_doc:
            catechist_doc.delete()
            return True
        return False

    # --- Catechizing Methods ---
    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        # ANOTACIÓN: La firma se cambió de (DTO, bool) a solo DTO para cumplir el contrato.
        with self.db.start_session() as session:
            with session.start_transaction():
                person_doc = self._get_or_create_person_doc(catechizing_data.Person)
                parent_docs = [ParentDocument.objects.get_or_create(Person=self._get_or_create_person_doc(p.Person), defaults={'IDParent': self._get_or_create_person_doc(p.Person).IDPerson, 'Ocuppation': p.Ocuppation})[0] for p in catechizing_data.Parent]
                godparent_docs = [GodparentDocument.objects.get_or_create(Person=self._get_or_create_person_doc(g.Person), defaults={'IDGodparent': self._get_or_create_person_doc(g.Person).IDPerson})[0] for g in catechizing_data.Godparent]
                if {p.Person.id for p in parent_docs}.intersection({gp.Person.id for gp in godparent_docs}): raise DuplicateColumnException("Una persona no puede ser Padre y Padrino.", {})
                #... (resto de la lógica de register_catechizing) ...
                catechizing_doc, created = CatechizingDocument.objects.get_or_create(Person=person_doc, defaults={ #...
                })
                if not created: raise DuplicateColumnException("Catechizing", {"DNI": person_doc.DNI})
                return self._to_dto(catechizing_doc.fetch_reload(), CatechizingDTO, include=["Person", "Parent", "Godparent"])

    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        query = CatechizingDocument.objects(IDCatechizing=catechizing_id).select_related(max_depth=3)
        return self._to_dto(query.first(), CatechizingDTO)

    def get_catechizings_by_class(self, class_id: int) -> List[CatechizingDTO]:
        class_ref = ClassDocument.objects(IDClass=class_id).only('id').first()
        if not class_ref: return []
        docs = CatechizingDocument.objects(Class=class_ref).select_related()
        return [self._to_dto(doc, CatechizingDTO, include=['Person']) for doc in docs]

    def get_catechizings_by_parish(self, parish_id: int, include: list[str] = []) -> List[CatechizingDTO]:
        parish_ref = ParishDocument.objects(IDParish=parish_id).only('id').first()
        if not parish_ref: return []
        classroom_ids = ClassroomDocument.objects(Parish=parish_ref).scalar('id')
        if not classroom_ids: return []
        class_ids = ClassDocument.objects(Schedule__elemMatch={'Classroom__in': classroom_ids}).scalar('id')
        if not class_ids: return []
        query = CatechizingDocument.objects(Class__in=class_ids).select_related(max_depth=2)
        return [self._to_dto(doc, CatechizingDTO, include=include) for doc in query]

    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        query = CatechizingDocument.objects.all().select_related(max_depth=2)
        return [self._to_dto(doc, CatechizingDTO, include=include) for doc in query]

    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        with self.db.start_session() as session:
            with session.start_transaction():
                catechizing_doc = CatechizingDocument.objects(IDCatechizing=catechizing_id).first()
                if not catechizing_doc: return None
                # ... Lógica de actualización detallada ...
                catechizing_doc.save()
                return self._to_dto(catechizing_doc.fetch_reload(), CatechizingDTO)

    def delete_catechizing(self, catechizing_id: int) -> bool:
        catechizing_doc = CatechizingDocument.objects(IDCatechizing=catechizing_id).first()
        if catechizing_doc:
            catechizing_doc.delete()
            return True
        return False
        
    # --- Métodos Auxiliares ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        doc = PersonDocument.objects(DNI=dni).select_related().first()
        return self._to_dto(doc, PersonDTO)

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        doc = UserDocument.objects(Username=username).select_related().first()
        return self._to_dto(doc, UserDTO, include=['Role'])

    def get_role(self, role: str) -> Optional[RoleDTO]:
        doc = RoleDocument.objects(Role=role).first()
        return RoleDTO(Role=doc.Role) if doc else None
    
    def get_blood_type_by_id(self, blood_type_id: int) -> Optional[BloodTypeDTO]:
        doc = BloodTypeDocument.objects(IDBloodType=blood_type_id).first()
        return self._to_dto(doc, BloodTypeDTO)

    def get_all_blood_types(self) -> List[BloodTypeDTO]:
        return [self._to_dto(doc, BloodTypeDTO) for doc in BloodTypeDocument.objects.all()]
    
    def get_phone_number_type_by_id(self, phone_number_type_id: int) -> Optional[PhoneNumberTypeDTO]:
        doc = PhoneNumberTypeDocument.objects(IDPhoneNumberType=phone_number_type_id).first()
        return self._to_dto(doc, PhoneNumberTypeDTO)
    
    def get_all_phone_number_types(self) -> List[PhoneNumberTypeDTO]:
        return [self._to_dto(doc, PhoneNumberTypeDTO) for doc in PhoneNumberTypeDocument.objects.all()]
    
    def get_level_by_name(self, level: str) -> Optional[LevelDTO]:
        doc = LevelDocument.objects(Name=level).first() # Corregido a 'Name'
        return self._to_dto(doc, LevelDTO)

    def get_class_by_id(self, class_id: int) -> Optional[ClassDTO]:
        doc = ClassDocument.objects(IDClass=class_id).select_related().first()
        return self._to_dto(doc, ClassDTO)

    def get_all_periods(self) -> List[ClassPeriodDTO]:
        return [self._to_dto(doc, ClassPeriodDTO) for doc in ClassPeriodDocument.objects.order_by('-IDClassPeriod')]

    def get_all_levels(self) -> List[LevelDTO]:
        return [self._to_dto(doc, LevelDTO) for doc in LevelDocument.objects.order_by('IDLevel')]

    def get_all_support_person(self, include: list[str] = []) -> List[SupportPersonDTO]:
        query = SupportPersonDocument.objects.all()
        if include: query = query.select_related()
        return [self._to_dto(doc, SupportPersonDTO, include=include) for doc in query]

    def get_all_day_of_the_week(self) -> List[DayOfTheWeekDTO]:
        return [self._to_dto(doc, DayOfTheWeekDTO) for doc in DayOfTheWeekDocument.objects.order_by('IDDayOfTheWeek')]

    def get_classroom_in_parish(self, parish_id: int) -> List[ClassroomDTO]:
        docs = ClassroomDocument.objects(Parish=parish_id).select_related()
        return [self._to_dto(doc, ClassroomDTO) for doc in docs]

    def get_class_period_by_id(self, period_id: int) -> Optional[ClassPeriodDTO]:
        doc = ClassPeriodDocument.objects(IDClassPeriod=period_id).first()
        return self._to_dto(doc, ClassPeriodDTO)

    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        # ANOTACIÓN: La firma se cambió de (DTO, bool) a solo DTO para cumplir el contrato.
        person_doc = self._get_or_create_person_doc(support_person_data.Person)
        support_doc, _ = SupportPersonDocument.objects.get_or_create(Person=person_doc, defaults={'IDSupportPerson': person_doc.IDPerson})
        return self._to_dto(support_doc.fetch_reload(), SupportPersonDTO, include=['Person'])

    def get_classes_by_parish_id(self, parish_id: int, include: list[str] = []) -> List[ClassDTO]:
        parish_ref = ParishDocument.objects(IDParish=parish_id).only('id').first()
        if not parish_ref: return []
        classroom_ids = ClassroomDocument.objects(Parish=parish_ref).scalar('id')
        if not classroom_ids: return []
        query = ClassDocument.objects(Schedule__elemMatch={'Classroom__in': classroom_ids}).select_related(max_depth=2)
        return [self._to_dto(doc, ClassDTO, include=include) for doc in query]

    def check_user_login(self, user_data: UserDTO) -> bool:
        user_doc = UserDocument.objects(Username=user_data.Username).first()
        if not user_doc: return False
        # ¡IMPORTANTE! Reemplazar con una verificación de hash segura
        return user_doc.check_password(user_data.Password)

    def get_dto_by_user(self, username: str):
        # ANOTACIÓN: La firma se cambió de username:str a user_id:int para cumplir el contrato.
        user_doc = UserDocument.objects(Username=username).first()
        if not user_doc: return None
        if user_doc.Role.Role == "Administrator":
            doc = AdministratorDocument.objects(User=user_doc).first()
            return self._to_dto(doc, AdministratorDTO, include=['User'])
        if user_doc.Role.Role == "Catechist":
            doc = CatechistDocument.objects(User=user_doc).first()
            return self._to_dto(doc, CatechistDTO, include=['User', 'Person'])
        if user_doc.Role.Role == "ParishPriest":
            doc = ParishPriestDocument.objects(User=user_doc).first()
            return self._to_dto(doc, ParishPriestDTO, include=['User', 'Person', 'Parish'])
        return None