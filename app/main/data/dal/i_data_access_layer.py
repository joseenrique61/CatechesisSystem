from abc import ABC, abstractmethod
from app.main.data.dtos.base_dtos import *

class IDataAccessLayer(ABC):

    # --- Parish Methods ---
    @abstractmethod
    def register_parish(self, parish_data: ParishDTO) -> ParishDTO:
        pass

    @abstractmethod
    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        pass

    @abstractmethod
    def get_all_parishes(self, include: list[str] = []) -> List[ParishDTO]:
        pass

    @abstractmethod
    def update_parish(self, parish_id: int, parish_data: ParishDTO) -> Optional[ParishDTO]:
        pass

    @abstractmethod
    def delete_parish(self, parish_id: int) -> bool: # Retorna True si se eliminó
        pass

    # --- Parish Priest Methods ---
    @abstractmethod
    def register_parish_priest(self, priest_data: ParishPriestDTO) -> ParishPriestDTO:
        pass

    @abstractmethod
    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_parish_priests_by_parish(self, parish_id: int) -> List[ParishPriestDTO]:
        pass

    @abstractmethod
    def get_all_parish_priests(self) -> List[ParishPriestDTO]:
        pass

    @abstractmethod
    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestDTO) -> Optional[ParishPriestDTO]:
        pass

    @abstractmethod
    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    @abstractmethod
    def register_catechist(self, catechist_data: CatechistDTO) -> CatechistDTO:
        pass

    @abstractmethod
    def get_catechist_by_id(self, catechist_id: int) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_all_catechists(self, include: list[str] = []) -> List[CatechistDTO]:
        pass

    @abstractmethod
    def update_catechist(self, catechist_id: int, catechist_data: CatechistDTO) -> Optional[CatechistDTO]:
        pass

    @abstractmethod
    def delete_catechist(self, catechist_id: int) -> bool:
        pass

    # --- Catechizing Methods ---
    @abstractmethod
    def register_catechizing(self, catechizing_data: CatechizingDTO) -> CatechizingDTO:
        pass

    @abstractmethod
    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_catechizings_by_class(self, class_id: int) -> List[CatechizingDTO]:
        pass

    @abstractmethod
    def get_catechizings_by_parish(self, parish_id: int, include: list[str] = []) -> List[CatechizingDTO]:
        pass

    @abstractmethod
    def get_all_catechizings(self, include: list[str] = []) -> List[CatechizingDTO]:
        pass

    @abstractmethod
    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingDTO) -> Optional[CatechizingDTO]:
        pass

    @abstractmethod
    def delete_catechizing(self, catechizing_id: int) -> bool:
        pass

    # --- Métodos auxiliares (podrían ser necesarios) ---
    @abstractmethod
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        pass

    @abstractmethod
    def get_role(self, role: str) -> Optional[RoleDTO]:
        pass

    @abstractmethod
    def get_blood_type_by_id(self, blood_type_id: int) -> Optional[BloodTypeDTO]:
        pass

    @abstractmethod
    def get_all_blood_types(self) -> List[BloodTypeDTO]:
        pass
    
    @abstractmethod
    def get_phone_number_type_by_id(self, phone_number_type_id: int) -> Optional[PhoneNumberTypeDTO]:
        pass
    
    @abstractmethod
    def get_all_phone_number_types(self) -> List[PhoneNumberTypeDTO]:
        pass
    
    @abstractmethod
    def get_level_by_name(self, level: str) -> Optional[LevelDTO]:
        pass

    @abstractmethod
    def get_class_by_id(self, class_id: int) -> Optional[ClassDTO]:
        pass

    @abstractmethod
    def get_all_periods(self) -> List[ClassPeriodDTO]:
        pass

    @abstractmethod
    def get_all_levels(self) -> List[LevelDTO]:
        pass

    @abstractmethod
    def get_all_catechists(self) -> List[CatechistDTO]:
        pass

    @abstractmethod
    def get_all_support_person(self, include: list[str] = []) -> List[SupportPersonDTO]:
        pass

    @abstractmethod
    def get_all_day_of_the_week(self) -> List[DayOfTheWeekDTO]:
        pass

    @abstractmethod
    def get_classroom_in_parish(self, parish_id: int) -> List[ClassroomDTO]:
        pass

    @abstractmethod
    def get_class_period_by_id(self, period_id: int) -> Optional[ClassPeriodDTO]:
        pass

    @abstractmethod
    def register_support_person(self, support_person_data: SupportPersonDTO) -> SupportPersonDTO:
        pass

    @abstractmethod
    def get_classes_by_parish_id(self, parish_id: int, include: list[str] = []) -> List[ClassDTO]:
        pass

    @abstractmethod
    def check_user_login(self, user_data: UserDTO) -> bool:
        pass

    @abstractmethod
    def get_dto_by_user(self, user_id: int):
        pass