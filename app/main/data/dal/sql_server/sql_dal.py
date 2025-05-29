from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import Optional
from app.main.data.dal.sql_server.sql_alchemy_adder import DBManager
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.sql_server.sql_models import *
from app.main.data.duplicate_column_exception import DuplicateColumnException
from app.main.data.image_manager import delete_image, upload_image

class SQLAlchemyDAL(IDataAccessLayer):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_role(self, role: str) -> Optional[RoleDTO]:
        return RoleDTO(Role=self.db.query(Role).filter_by(Role=role).first().Role)
    
    def get_phone_number_type_by_id(self, phone_number_type_id: int) -> Optional[PhoneNumberTypeDTO]:
        phone_number_type = self.db.query(PhoneNumberType).filter_by(IDPhoneNumberType=phone_number_type_id).first()
        return PhoneNumberTypeDTO(
            IDPhoneNumberType=phone_number_type.IDPhoneNumberType,
            PhoneNumberType=phone_number_type.PhoneNumberType
        )
    
    def get_all_phone_number_types(self) -> list[PhoneNumberTypeDTO]:
        """
        Obtiene todos los tipos de números de teléfono disponibles en la base de datos.

        :return: Una lista de PhoneNumberTypeDTO.
        """
        phone_number_types = self.db.query(PhoneNumberType).all()
        return [PhoneNumberTypeDTO(IDPhoneNumberType=phone_type.IDPhoneNumberType, PhoneNumberType=phone_type.PhoneNumberType) for phone_type in phone_number_types]
    
    def get_blood_type_by_id(self, blood_type_id: int) -> Optional[BloodTypeDTO]:
        """
        Obtiene un tipo de sangre por su ID.
        :param blood_type_id: ID del tipo de sangre.
        :return: Un objeto BloodTypeDTO.
        """
        blood_type = self.db.query(BloodType).filter_by(IDBloodType=blood_type_id).first()
        return BloodTypeDTO(
            IDBloodType=blood_type.IDBloodType,
            BloodType=blood_type.BloodType
        )
    
    def get_class_by_id(self, class_id: int) -> Optional[ClassDTO]:
        """
        Obtiene una clase por su ID.
        :param class_id: ID de la clase.
        :return: Un objeto ClassDTO.
        """
        return ClassDTO.from_other_obj(self.db.query(Class).filter_by(IDClass=class_id).first())

    def get_level_by_id(self, level_id):
        return LevelDTO.from_other_obj(self.db.query(Level).filter_by(IDLevel=level_id).first())
    
    def get_level_by_name(self, level):
        return LevelDTO.from_other_obj(self.db.query(Level).filter_by(Level=level).first())
    
    def get_all_periods(self) -> List[ClassPeriodDTO]:
        return [ClassPeriodDTO.from_other_obj(class_period) for class_period in self.db.query(ClassPeriod).order_by(desc(ClassPeriod.IDClassPeriod)).all()]

    def get_all_levels(self) -> List[LevelDTO]:
        return [LevelDTO.from_other_obj(level) for level in self.db.query(Level).order_by(asc(Level.IDLevel)).all()]

    def get_all_catechists(self) -> List[CatechistDTO]:
        return [CatechistDTO.from_other_obj(catechist) for catechist in self.db.query(Catechist).all()]

    def get_all_support_person(self) -> List[SupportPersonDTO]:
        return [SupportPersonDTO.from_other_obj(support_person) for support_person in self.db.query(SupportPerson).all()]

    def get_all_day_of_the_week(self) -> List[DayOfTheWeekDTO]:
        return [DayOfTheWeekDTO.from_other_obj(day_of_the_week) for day_of_the_week in self.db.query(DayOfTheWeek).order_by(asc(DayOfTheWeek.IDDayOfTheWeek)).all()]

    def get_classroom_in_parish(self, parish_id: int) -> List[ClassroomDTO]:
        return [ClassroomDTO.from_other_obj(classroom) for classroom in self.db.query(Classroom).filter_by(IDParish=parish_id).all()]

    # --- Parish Methods ---
    def register_parish(self, parish_data: ParishDTO) -> tuple[ParishDTO, bool]:
        """
        Registra una nueva parroquia en la base de datos.
        
        :param parish_data: Datos de la parroquia a registrar.
        :return: El objeto ParishDTO creado y un bool indicando si se creó.
        """
        try:
            logo_path = upload_image(parish_data.LogoImage)
            
            parish_data.Logo = logo_path
            parish = Parish.from_other_obj(parish_data, exclude=["Classroom.Parish.Classroom"], include=["Classroom"])
            parish, success, _ = DBManager.get_or_create(self.db, parish)
            
            parish_dto = ParishDTO.from_other_obj(parish)
            self.db.commit()

            if not success:
                image_deleted = delete_image(logo_path)
                if not image_deleted:
                    raise Exception("Error al eliminar la imagen del logo tras un fallo en la creación de la parroquia.")
            return parish_dto, success
        except:
            delete_image(logo_path)
            raise

    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        return ParishDTO.from_other_obj(self.db.query(Parish).filter_by(IDParish=parish_id).first())

    def get_all_parishes(self) -> List[ParishDTO]:
        return [ParishDTO.from_other_obj(parish, exclude=["Address.Location.Person"]) for parish in self.db.query(Parish).all()]

    def update_parish(self, parish_id: int, parish_data: ParishDTO) -> Optional[ParishDTO]:
        pass

    def delete_parish(self, parish_id: int) -> bool: # Retorna True si se eliminó
        pass

    # --- Parish Priest Methods ---
    def register_parish_priest(self, priest_data: ParishPriestDTO) -> tuple[ParishPriestDTO, bool]:
        """
        Registra un nuevo sacerdote parroquial en la base de datos.

        :param priest_data: Datos del sacerdote parroquial a registrar.
        :return: Una tupla con el objeto ParishPriestDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            priest_data.User.Role.Role = "ParishPriest"
            parish_priest = ParishPriest.from_other_obj(priest_data)
            parish_priest, success, _ = DBManager.get_or_create(self.db, parish_priest, ignore_duplicate_error_for=["Parish"])
            
            parish_priest_dto = ParishPriestDTO.from_other_obj(parish_priest)
            self.db.commit()
            return parish_priest_dto, success
        except:
            raise

    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        return ParishPriestDTO.from_other_obj(self.db.query(ParishPriest).filter_by(IDParishPriest=priest_id).one_or_none())

    def get_parish_priests_by_parish(self, parish_id: int) -> List[ParishPriestDTO]:
        pass

    def get_all_parish_priests(self) -> List[ParishPriestDTO]:
        return [ParishPriestDTO.from_other_obj(parish_priest) for parish_priest in self.db.query(ParishPriest).all()]

    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        pass

    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        try:
            catechist_data.User.Role.Role = "Catechist"
            catechist = Catechist.from_other_obj(catechist_data)
            catechist, success, _ = DBManager.get_or_create(self.db, catechist)
            
            catechist_dto = CatechistDTO.from_other_obj(catechist)
            self.db.commit()
            return catechist_dto, success
        except:
            raise

    def get_catechist_by_id(self, catechist_id: int) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_all_catechists(self, include: list[str] = []) -> List[CatechistDTO]:
        return [CatechistDTO.from_other_obj(catechist, include=include) for catechist in self.db.query(Catechist).all()]

    def update_catechist(self, catechist_id: int, catechist_data: CatechistDTO) -> Optional[CatechistDTO]:
        pass

    def delete_catechist(self, catechist_id: int) -> bool:
        pass

    # --- Catechizing Methods ---
    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        try:
            catechizing = Catechizing.from_other_obj(catechizing_data, include=["Parent", "Godparent", "HealthInformation.Allergy"])

            new_parents = []
            for parent in catechizing.Parent:
                filter_conditions = [{"DNI": parent.Person.DNI}, {"FirstName": parent.Person.FirstName, "MiddleName": parent.Person.MiddleName, "FirstSurname": parent.Person.FirstSurname, "SecondSurname": parent.Person.SecondSurname}]
                for filter_condition in filter_conditions:
                    if (person := self.db.query(Person).filter_by(**filter_condition).one_or_none()):
                        parent_temp = self.db.query(Parent).filter_by(IDParent=person.IDPerson).one_or_none()
                        break
                    else:
                        parent_temp = parent
                new_parents.append(parent_temp)
            catechizing.Parent = new_parents

            new_godParents = []
            for godParent in catechizing.Godparent:
                filter_conditions = [{"DNI": godParent.Person.DNI}, {"FirstName": godParent.Person.FirstName, "MiddleName": godParent.Person.MiddleName, "FirstSurname": godParent.Person.FirstSurname, "SecondSurname": godParent.Person.SecondSurname}]
                for filter_condition in filter_conditions:
                    if (person := self.db.query(Person).filter_by(**filter_condition).one_or_none()):
                        godparent_temp = self.db.query(Godparent).filter_by(IDGodparent=person.IDPerson).one_or_none()
                        break
                    else:
                        godparent_temp = godParent
                new_godParents.append(godparent_temp)
            catechizing.Godparent = new_godParents
            
            catechizing, success, _ = DBManager.get_or_create(self.db, catechizing, ignore_duplicate_error_for=["Parent", "Godparent", "Parent.Person", "Godparent.Person", "HealthInformation.EmergencyContact"])

            for parent in catechizing.Parent:
                for godparent in catechizing.Godparent:
                    if parent.IDParent == godparent.IDGodparent:
                        raise DuplicateColumnException("Parent", {})
            
            catechizing_dto = CatechizingDTO.from_other_obj(catechizing)
            self.db.commit()
            return catechizing_dto, success
        except:
            raise

    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        return CatechizingDTO.from_other_obj(self.db.query(Catechizing).filter_by(IDCatechizing=catechizing_id).one_or_none(), include=["Parent", "Godparent", "Person.Address", "Person.Address.Location", "Person.PhoneNumber", "Person.PhoneNumberType", "SchoolClassYear", "SchoolClassYear.School", "SchoolClassYear.School.Address", "SchoolClassYear.School.Address.Location", "HealthInformation.Allergy", "HealthInformation.EmergencyContact", "HealthInformation.EmergencyContact.BirthLocation", "HealthInformation.EmergencyContact.Address", "HealthInformation.EmergencyContact.Address.Location", "HealthInformation.EmergencyContact.PhoneNumber", "HealthInformation.EmergencyContact.PhoneNumberType"])

    def get_catechizings_by_class(self, class_id: int) -> List[CatechizingDTO]:
        pass

    def get_catechizings_by_parish(self, parish_id: int, include: list[str] = []) -> List[CatechizingDTO]:
        cursor = self.db.execute(text("SET NOCOUNT ON; EXEC [ClassInformation].[sp_CatechizingsInParish] @IDParish = :id; SET NOCOUNT OFF"), {"id": parish_id})
        catechizing_ids = cursor.fetchall()
        results = []
        for row in catechizing_ids:
            results.append(CatechizingDTO.from_other_obj(self.db.query(Catechizing).filter_by(IDCatechizing=row.IDCatechizing).one_or_none(), include=include))
        return results

    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        return [CatechizingDTO.from_other_obj(catechizing, include=include) for catechizing in self.db.query(Catechizing).all()]

    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        try:
            catechizing_from_db = self.db.query(Catechizing).filter_by(IDCatechizing=catechizing_id).one_or_none()

            catechizing_from_db.Class = self.db.query(Class).filter_by(IDClass=catechizing_data.IDClass).one_or_none()
            catechizing_from_db.SiblingsNumber = catechizing_data.SiblingsNumber
            catechizing_from_db.PayedLevelCourse = catechizing_data.PayedLevelCourse
            catechizing_from_db.Person.EmailAddress = catechizing_data.Person.EmailAddress

            healthInformation = HealthInformation.from_other_obj(catechizing_data.HealthInformation, include=["Allergy"])
            healthInformation_from_db = self.db.query(HealthInformation).filter_by(IDCatechizing=catechizing_id).one_or_none()
            healthInformation_from_db.Allergy = [DBManager.get_or_create(self.db, allergy, exclude=["HealthInformation"])[0] for allergy in healthInformation.Allergy]
            self.db.flush()

            healthInformation_from_db.EmergencyContact, _, _ = DBManager.get_or_create(self.db, healthInformation.EmergencyContact, ignore_duplicate_error_for=[""], exclude=["HealthInformation"])
            self.db.flush()

            healthInformation_from_db.ImportantAspects = healthInformation.ImportantAspects
            self.db.flush()

            dataSheet_from_db = self.db.query(DataSheet).filter_by(IDCatechizing=catechizing_id).one_or_none()
            dataSheet_from_db.DataSheetInformation = catechizing_data.DataSheet.DataSheetInformation
            
            address = Address.from_other_obj(catechizing_data.Person.Address)
            address, _, _ = DBManager.get_or_create(self.db, address)

            catechizing_from_db.Person.Address = address
            
            phoneNumber = PhoneNumber.from_other_obj(catechizing_data.Person.PhoneNumber)
            phoneNumber, _, _ = DBManager.get_or_create(self.db, phoneNumber)

            catechizing_from_db.Person.PhoneNumber = phoneNumber

            schoolClassYear = SchoolClassYear.from_other_obj(catechizing_data.SchoolClassYear)
            schoolClassYear, _, _ = DBManager.get_or_create(self.db, schoolClassYear)

            catechizing_from_db.SchoolClassYear = schoolClassYear

            self.db.flush()
            self.db.commit()

            return CatechizingDTO.from_other_obj(catechizing_from_db), True
        except:
            raise

    def delete_catechizing(self, catechizing_id: int) -> bool:
        catechizing = self.db.query(Catechizing).filter_by(IDCatechizing=catechizing_id).one_or_none()
        self.db.delete(catechizing)
        self.db.commit()
        return True

    # --- Métodos de support person ---
    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        try:
            support_person = SupportPerson.from_other_obj(support_person_data)
            support_person, success, _ = DBManager.get_or_create(self.db, support_person)
            
            support_person_dto = SupportPersonDTO.from_other_obj(support_person)
            self.db.commit()
            return support_person_dto, success
        except:
            raise

    # --- Métodos de class ---
    def register_class(self, class_data: ClassDTO) -> CatechistDTO:
        try:
            class_obj = Class.from_other_obj(class_data, include=["Schedule"])
            class_obj, success, _ = DBManager.get_or_create(self.db, class_obj)
            
            catechist_dto = ClassDTO.from_other_obj(class_obj)
            self.db.commit()
            return catechist_dto, success
        except:
            raise
        

    # --- Métodos auxiliares (podrían ser necesarios) ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        person_from_db = self.db.query(Person).filter_by(DNI=dni).first()
        return PersonDTO.from_other_obj(person_from_db)

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        pass

    def get_class_period_by_id(self, period_id: int) -> Optional[ClassPeriodDTO]:
        return ClassPeriodDTO.from_other_obj(self.db.query(ClassPeriod).filter_by(IDClassPeriod=period_id).one_or_none())
    
    def get_classes_by_parish_id(self, parish_id: int) -> List[ClassDTO]:
        cursor = self.db.execute(text("SET NOCOUNT ON; EXEC [ClassInformation].[sp_ClassesInParish] @IDParish = :id; SET NOCOUNT OFF"), {"id": parish_id})
        class_ids = cursor.fetchall()
        results = []
        for row in class_ids:
            results.append(ClassDTO.from_other_obj(self.db.query(Class).filter_by(IDClass=row.IDClass).one_or_none(), include=["Schedule", "Schedule.DayOfTheWeek"]))
        return results

    def get_all_blood_types(self) -> List[BloodTypeDTO]:
        return [BloodTypeDTO.from_other_obj(blood_type) for blood_type in self.db.query(BloodType).all()]