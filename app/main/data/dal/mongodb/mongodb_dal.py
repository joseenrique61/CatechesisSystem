from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from flask_mongoengine import MongoEngine

from app.main.data.dtos.base_dtos import *

class MongoDBDAL(IDataAccessLayer):
    def __init__(self, db: MongoEngine):
        self.db = db
        
    # --- Parish Methods ---
    def register_parish(self, parish_data: ParishDTO) -> ParishDTO:
        pass

    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        pass

    def get_all_parishes(self, include: list[str] = []) -> List[ParishDTO]:
        pass

    def update_parish(self, parish_id: int, parish_data: ParishDTO) -> Optional[ParishDTO]:
        pass

    def delete_parish(self, parish_id: int) -> bool: # Retorna True si se eliminó
        pass

    # --- Parish Priest Methods ---
    def register_parish_priest(self, priest_data: ParishPriestDTO) -> ParishPriestDTO:
        pass

    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_parish_priests_by_parish(self, parish_id: int) -> List[ParishPriestDTO]:
        pass

    def get_all_parish_priests(self) -> List[ParishPriestDTO]:
        pass

    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        pass

    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        pass

    def get_catechist_by_id(self, catechist_id: int, include: list[str] = []) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_all_catechists(self, include: list[str] = []) -> List[CatechistDTO]:
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

    def get_catechizings_by_parish(self, parish_id: int, include: list[str] = []) -> List[CatechizingDTO]:
        pass

    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        pass

    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        pass

    def delete_catechizing(self, catechizing_id: int) -> bool:
        pass

    # --- Métodos auxiliares (podrían ser necesarios) ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        pass

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        pass

    def get_role(self, role: str) -> Optional[RoleDTO]:
        pass

    def get_blood_type_by_id(self, blood_type_id: int) -> Optional[BloodTypeDTO]:
        pass

    def get_all_blood_types(self) -> List[BloodTypeDTO]:
        pass
    
    def get_phone_number_type_by_id(self, phone_number_type_id: int) -> Optional[PhoneNumberTypeDTO]:
        pass
    
    def get_all_phone_number_types(self) -> List[PhoneNumberTypeDTO]:
        pass
    
    def get_level_by_name(self, level: str) -> Optional[LevelDTO]:
        pass

    def get_class_by_id(self, class_id: int) -> Optional[ClassDTO]:
        pass

    def get_all_periods(self) -> List[ClassPeriodDTO]:
        pass

    def get_all_levels(self) -> List[LevelDTO]:
        pass

    def get_all_catechists(self) -> List[CatechistDTO]:
        pass

    def get_all_support_person(self, include: list[str] = []) -> List[SupportPersonDTO]:
        pass

    def get_all_day_of_the_week(self) -> List[DayOfTheWeekDTO]:
        pass

    def get_classroom_in_parish(self, parish_id: int) -> List[ClassroomDTO]:
        pass

    def get_class_period_by_id(self, period_id: int) -> Optional[ClassPeriodDTO]:
        pass

    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        pass

    def get_classes_by_parish_id(self, parish_id: int, include: list[str] = []) -> List[ClassDTO]:
        pass

    def check_user_login(self, user_data: UserDTO) -> bool:
        pass

    def get_dto_by_user(self, user_id: int):
        pass