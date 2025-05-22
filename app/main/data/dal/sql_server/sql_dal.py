from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from sqlalchemy.orm import Session
from typing import Optional
from app.main.data.dal.sql_server.sql_alchemy_adder import DBManager
from app.main.data.dtos.base_dtos import *
from app.main.data.dal.sql_server.sql_models import *
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
            parish = Parish.from_other_obj(parish_data, exclude=["Classroom.Parish.Classroom"])
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
        return [ParishDTO.from_other_obj(parish) for parish in self.db.query(Parish).all()]

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
            parish_priest = ParishPriest.from_other_obj(priest_data)
            parish_priest, success, _ = DBManager.get_or_create(self.db, parish_priest)
            
            parish_priest_dto = ParishPriestDTO.from_other_obj(parish_priest)
            self.db.commit()
            return parish_priest_dto, success
        except:
            raise

    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_parish_priests_by_parish(self, parish_id: int) -> List[ParishPriestDTO]:
        pass

    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        pass

    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        pass

    def get_catechist_by_id(self, catechist_id: int) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_all_catechists(self) -> List[CatechistDTO]:
        pass

    def update_catechist(self, catechist_id: int, catechist_data: CatechistDTO) -> Optional[CatechistDTO]:
        pass

    def delete_catechist(self, catechist_id: int) -> bool:
        pass

    # --- Catechizing Methods ---
    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        pass

    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_catechizings_by_class(self, class_id: int) -> List[CatechizingDTO]:
        pass

    def get_all_catechizings(self) -> List[CatechizingDTO]:
        pass

    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        pass

    def delete_catechizing(self, catechizing_id: int) -> bool:
        pass

    # --- Métodos auxiliares (podrían ser necesarios) ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        person_from_db = self.db.query(Person).filter_by(DNI=dni).first()
        return PersonDTO.from_other_obj(person_from_db)

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        pass