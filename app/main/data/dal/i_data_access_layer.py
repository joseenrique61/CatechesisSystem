from abc import ABC, abstractmethod
from app.main.data.dtos.base_dtos import *
from app.main.data.dtos.create_dtos import *

class IDataAccessLayer(ABC):

    # --- Parish Methods ---
    @abstractmethod
    def register_parish(self, parish_data: ParishCreateDTO) -> ParishDTO:
        pass

    @abstractmethod
    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        pass

    @abstractmethod
    def get_all_parishes(self, skip: int = 0, limit: int = 100) -> List[ParishDTO]:
        pass

    @abstractmethod
    def update_parish(self, parish_id: int, parish_data: ParishUpdateDTO) -> Optional[ParishDTO]:
        pass

    @abstractmethod
    def delete_parish(self, parish_id: int) -> bool: # Retorna True si se eliminó
        pass

    # --- Parish Priest Methods ---
    @abstractmethod
    def register_parish_priest(self, priest_data: ParishPriestCreateDTO) -> ParishPriestDTO:
        pass

    @abstractmethod
    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_parish_priests_by_parish(self, parish_id: int, skip: int = 0, limit: int = 100) -> List[ParishPriestDTO]:
        pass

    @abstractmethod
    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestUpdateDTO) -> Optional[ParishPriestDTO]:
        pass

    @abstractmethod
    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    @abstractmethod
    def register_catechist(self, catechist_data: CatechistCreateDTO) -> CatechistDTO:
        pass

    @abstractmethod
    def get_catechist_by_id(self, catechist_id: int) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_all_catechists(self, skip: int = 0, limit: int = 100) -> List[CatechistDTO]:
        pass

    @abstractmethod
    def update_catechist(self, catechist_id: int, catechist_data: CatechistUpdateDTO) -> Optional[CatechistDTO]:
        pass

    @abstractmethod
    def delete_catechist(self, catechist_id: int) -> bool:
        pass

    # --- Catechizing Methods ---
    @abstractmethod
    def register_catechizing(self, catechizing_data: CatechizingCreateDTO) -> CatechizingDTO:
        pass

    @abstractmethod
    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        pass # ID se refiere a Person.IDPerson

    @abstractmethod
    def get_catechizings_by_class(self, class_id: int, skip: int = 0, limit: int = 100) -> List[CatechizingDTO]:
        pass

    @abstractmethod
    def get_all_catechizings(self, skip: int = 0, limit: int = 100) -> List[CatechizingDTO]:
        pass

    @abstractmethod
    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingUpdateDTO) -> Optional[CatechizingDTO]:
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