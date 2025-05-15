from app.main.data.dal.i_data_access_layer import IDataAccessLayer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.main.data.dtos.base_dtos import *
from app.main.data.dtos.create_dtos import *
from app.main.data.dal.sql_server.sql_models import *

class SQLAlchemyDAL(IDataAccessLayer):
    def __init__(self, db_session: Session):
        self.db = db_session

    def _get_or_create(self, model_instance, unique_constraints: list[list[str]]) -> tuple[object, bool, Optional[list[str]]]:
        """
        Tries to get an existing instance from the DB based on unique constraints,
        or creates a new one.

        :param model_instance: A new, transient model instance with data.
        :param unique_constraints: A list of lists of attribute names.
                                   Each inner list represents a unique constraint.
                                   Example: [['Username'], ['Email']]
        :return: (instance, created_bool, conflicting_constraint_attrs_list_or_None)
                 - instance: The persisted instance (either existing or newly created).
                 - created_bool: True if a new instance was created, False if an existing one was found.
                 - conflicting_constraint_attrs_list_or_None: If an existing instance was found by query,
                   this is the list of attributes that matched. If created, or if found via IntegrityError fallback,
                   this might be None or determined differently.
        """
        model_class = type(model_instance)

        # 1. Try to find an existing instance by querying unique constraints
        for constraint_attrs in unique_constraints:
            filter_conditions = {}
            valid_constraint = True
            for attr_name in constraint_attrs:
                if hasattr(model_instance, attr_name):
                    filter_conditions[attr_name] = getattr(model_instance, attr_name)
                else:
                    # Esto no debería ocurrir si los atributos son correctos
                    valid_constraint = False
                    break
            
            if not valid_constraint or not filter_conditions:
                continue # Pasa al siguiente conjunto de restricciones si este es inválido

            existing_instance = self.db.query(model_class).filter_by(**filter_conditions).one_or_none()
            if existing_instance:
                # Desvincular la instancia propuesta si no es la que vamos a usar,
                # para evitar problemas de sesión si se añadió accidentalmente antes.
                if model_instance in self.db:
                    self.db.expunge(model_instance)
                return existing_instance, False, constraint_attrs

        # 2. If not found, try to add the new instance
        try:
            # Asegurarse de que la instancia está asociada a la sesión actual
            # Si venía de otra sesión o fue creada sin sesión.
            # Si ya está en la sesión y es 'dirty', está bien.
            # Si es 'transient', se añadirá.
            # Si es 'detached', se necesita un merge o un add.
            # Por simplicidad, si no está en la sesión, la añadimos.
            if model_instance not in self.db:
                 self.db.add(model_instance)
            else: # Si ya estaba, pero quizás de una operación fallida anterior, refrescarla
                pass # Dejarla como está si ya está 'dirty'

            self.db.flush() # Intenta la inserción
            return model_instance, True, None
        except IntegrityError:
            self.db.rollback()
            # 3. Fallback: If IntegrityError occurs (e.g., due to a race condition),
            #    query again to get the conflicting instance.
            #    Esta parte es más compleja porque el IntegrityError no te dice QUÉ restricción falló.
            #    Podríamos re-intentar las búsquedas, o simplemente asumir que uno de los constraints falló.
            #    Para una implementación más simple del fallback, podrías solo re-intentar la primera búsqueda
            #    o una búsqueda combinada si es posible.
            
            # Re-intentar la búsqueda es más seguro tras un rollback.
            for constraint_attrs in unique_constraints:
                filter_conditions = {}
                # ... (repetir lógica de construcción de filter_conditions) ...
                for attr_name in constraint_attrs:
                    if hasattr(model_instance, attr_name):
                        filter_conditions[attr_name] = getattr(model_instance, attr_name)
                
                if not filter_conditions: continue

                conflicting_instance = self.db.query(model_class).filter_by(**filter_conditions).one_or_none()
                if conflicting_instance:
                    if model_instance in self.db: # Asegurarse que la instancia fallida no esté en la sesión
                        self.db.expunge(model_instance)
                    return conflicting_instance, False, constraint_attrs
            
            # Si llegamos aquí después de un IntegrityError y no encontramos el conflicto, algo raro pasó.
            # O la instancia original fue modificada entre el flush fallido y esta re-búsqueda.
            # Es importante desvincular la instancia original si no se va a usar.
            if model_instance in self.db.new: # si se quedó en el estado 'new' pero no se pudo hacer flush
                self.db.expunge(model_instance) # Quitarla de la sesión para evitar problemas

            raise # Re-lanzar IntegrityError si no se pudo resolver
        except Exception as e:
            self.db.rollback()
            raise e

    # --- General Methods ---
    def _get_or_create_user(self, user_data: UserCreateDTO) -> tuple[User, bool]:
        """
        Registra un nuevo usuario en la base de datos.

        :param user_data: Datos del usuario a registrar.
        :return: Una tupla con el objeto UserDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            user = User(
                Username=user_data.Username,
                Role=Role.query.filter_by(Role=user_data.Role.Role).first(),
            )
            user.set_password(user_data.Password)
            user, success, _ = self._get_or_create(user, [['Username']])
            return user, success
        except:
            raise

    def _get_or_create_location(self, location_data: LocationDTO) -> tuple[Location, bool]:
        """
        Registra una nueva ubicación en la base de datos.

        :param location_data: Datos de la ubicación a registrar.
        :return: Una tupla con el objeto LocationDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            location = Location(
                Country=location_data.Country,
                State=location_data.State,
                Province=location_data.Province,
            )
            location, success, _ = self._get_or_create(location, [['Country', 'State', 'Province']])
            return location, success
        except:
            raise
        
    
    def _get_or_create_address(self, address_data: AddressDTO) -> tuple[Address, bool, Optional[list[str]]]:
        """
        Registra una nueva dirección en la base de datos.

        :param address_data: Datos de la dirección a registrar.
        :return: Una tupla con el objeto AddressDTO creado un booleano indicando si fue creado o no, y una lista de errores ocurridos.
        """
        try:
            location, _ = self._get_or_create_location(address_data.Location)
            address = Address(
                MainStreet=address_data.MainStreet,
                Number=address_data.Number,
                SecondStreet=address_data.SecondStreet,
                Location=location,
            )
            address, success, _ = self._get_or_create(address, [['MainStreet', 'Number', 'SecondStreet']])
            return address, success
        except:
            raise

    def _get_or_create_phone_number(self, phone_number_data: PhoneNumberCreateDTO) -> tuple[PhoneNumber, bool]:
        """
        Registra un nuevo número de teléfono en la base de datos.

        :param phone_number_data: Datos del número de teléfono a registrar.
        :return: Una tupla con el objeto PhoneNumberDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            phone_number_type = db.session.query(PhoneNumberType).filter_by(IDPhoneNumberType=phone_number_data.Type).first()
            phone_number = PhoneNumber(
                PhoneNumber=phone_number_data.Number,
                PhoneNumberType=phone_number_type,
            )
            phone_number, success, _ = self._get_or_create(phone_number, [['Number']])
            return phone_number, success
        except:
            raise
    
    def _get_or_create_person(self, person_data: PersonCreateDTO) -> tuple[Person, bool]:
        """
        Registra una nueva persona en la base de datos.

        :param person_data: Datos de la persona a registrar.
        :return: Una tupla con el objeto PersonDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            location, _ = self._get_or_create_location(person_data.BirthLocation)
            address, _ = self._get_or_create_address(person_data.Address)
            phone_number, _ = self._get_or_create_phone_number(person_data.PhoneNumber)

            person = Person(
                FirstName=person_data.FirstName,
                MiddleName=person_data.MiddleName,
                FirstSurname=person_data.FirstSurname,
                SecondSurname=person_data.SecondSurname,
                BirthDate=person_data.BirthDate,
                BirthLocation=location,
                DNI=person_data.DNI,
                Gender=person_data.Gender,
                Address=address,
                PhoneNumber=phone_number,
                EmailAddress=person_data.EmailAddress,
            )
            person, success, _ = self._get_or_create(person, [['FirstName', 'MiddleName', 'FirstSurname', 'SecondSurname'], ['DNI']])
            return person, success
        except:
            raise

    
    def get_role(self, role: str) -> Optional[RoleDTO]:
        return RoleDTO(Role=self.db.query(Role).filter_by(Role=role).first().Role)
    
    # --- Parish Methods ---
    def register_parish(self, parish_data: ParishCreateDTO) -> ParishDTO:
        pass

    def get_parish_by_id(self, parish_id: int) -> Optional[ParishDTO]:
        pass

    def get_all_parishes(self, skip: int = 0, limit: int = 100) -> List[ParishDTO]:
        pass

    def update_parish(self, parish_id: int, parish_data: ParishUpdateDTO) -> Optional[ParishDTO]:
        pass

    def delete_parish(self, parish_id: int) -> bool: # Retorna True si se eliminó
        pass

    # --- Parish Priest Methods ---
    def register_parish_priest(self, priest_data: ParishPriestCreateDTO) -> tuple[ParishPriestDTO, bool]:
        """
        Registra un nuevo sacerdote parroquial en la base de datos.

        :param priest_data: Datos del sacerdote parroquial a registrar.
        :return: Una tupla con el objeto ParishPriestDTO creado y un booleano indicando si fue creado o no.
        """
        try:
            person, _ = self._get_or_create_person(priest_data.Person)
            user, user_created = self._get_or_create_user(priest_data.User)
            if not user_created:
                raise IntegrityError("El usuario ya existe y no se puede crear un nuevo sacerdote con el mismo usuario.")

            parish_priest = ParishPriest(
                Person=person,
                User=user,
                IDParish=priest_data.IDParish,
            )
            parish_priest, success, _ = self._get_or_create(parish_priest, [['IDParish', 'IDUser']])
            parish_priest_dto = ParishPriestDTO(
                IDParishPriest=parish_priest.IDParishPriest,
                User=UserReadDTO(
                    IDUser=parish_priest.User.IDUser,
                    Username=parish_priest.User.Username,
                    Role=RoleDTO(
                        IDRole=parish_priest.User.Role.IDRole,
                        Role=parish_priest.User.Role.Role
                    )
                ),
                Parish=ParishDTO(
                    IDParish=parish_priest.Parish.IDParish,
                    Name=parish_priest.Parish.Name,
                    Logo="blabla",
                    Address=AddressDTO(
                        IDAddress=parish_priest.Parish.Address.IDAddress,
                        MainStreet=parish_priest.Parish.Address.MainStreet,
                        Number=parish_priest.Parish.Address.Number,
                        SecondStreet=parish_priest.Parish.Address.SecondStreet,
                        Location=LocationDTO(
                            IDLocation=parish_priest.Parish.Address.Location.IDLocation,
                            Country=parish_priest.Parish.Address.Location.Country,
                            State=parish_priest.Parish.Address.Location.State,
                            Province=parish_priest.Parish.Address.Location.Province
                        ),
                    ),
                ),
                Person=PersonDTO(
                    IDPerson=parish_priest.Person.IDPerson,
                    FirstName=parish_priest.Person.FirstName,
                    MiddleName=parish_priest.Person.MiddleName,
                    FirstSurname=parish_priest.Person.FirstSurname,
                    SecondSurname=parish_priest.Person.SecondSurname,
                    BirthDate=parish_priest.Person.BirthDate,
                    BirthLocation=LocationDTO(
                        IDLocation=parish_priest.Person.BirthLocation.IDLocation,
                        Country=parish_priest.Person.BirthLocation.Country,
                        State=parish_priest.Person.BirthLocation.State,
                        Province=parish_priest.Person.BirthLocation.Province
                    ),
                    DNI=parish_priest.Person.DNI,
                    Gender=parish_priest.Person.Gender,
                    Address=AddressDTO(
                        IDAddress=parish_priest.Person.Address.IDAddress,
                        MainStreet=parish_priest.Person.Address.MainStreet,
                        Number=parish_priest.Person.Address.Number,
                        SecondStreet=parish_priest.Person.Address.SecondStreet,
                        Location=LocationDTO(
                            IDLocation=parish_priest.Person.Address.Location.IDLocation,
                            Country=parish_priest.Person.Address.Location.Country,
                            State=parish_priest.Person.Address.Location.State,
                            Province=parish_priest.Person.Address.Location.Province
                        ),
                    ),
                    PhoneNumber=PhoneNumberDTO(
                        IDPhoneNumer=parish_priest.Person.PhoneNumber.IDPhoneNumer,
                        PhoneNumber=parish_priest.Person.PhoneNumber.PhoneNumber,
                        PhoneNumberType=PhoneNumberTypeDTO(
                            IDPhoneNumberType=parish_priest.Person.PhoneNumber.PhoneNumberType.IDPhoneNumberType,
                            PhoneNumberType=parish_priest.Person.PhoneNumber.PhoneNumberType.PhoneNumberType
                        )
                    ),
                    EmailAddress=parish_priest.Person.EmailAddress,
                )
            )
            db.session.commit()
            return parish_priest_dto, success
        except:
            raise

    def get_parish_priest_by_id(self, priest_id: int) -> Optional[ParishPriestDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_parish_priests_by_parish(self, parish_id: int, skip: int = 0, limit: int = 100) -> List[ParishPriestDTO]:
        pass

    def update_parish_priest(self, priest_id: int, priest_data: ParishPriestUpdateDTO) -> Optional[ParishPriestDTO]:
        pass

    def delete_parish_priest(self, priest_id: int) -> bool:
        pass


    # --- Catechist Methods ---
    def register_catechist(self, catechist_data: CatechistCreateDTO) -> CatechistDTO:
        pass

    def get_catechist_by_id(self, catechist_id: int) -> Optional[CatechistDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_all_catechists(self, skip: int = 0, limit: int = 100) -> List[CatechistDTO]:
        pass

    def update_catechist(self, catechist_id: int, catechist_data: CatechistUpdateDTO) -> Optional[CatechistDTO]:
        pass

    def delete_catechist(self, catechist_id: int) -> bool:
        pass

    # --- Catechizing Methods ---
    def register_catechizing(self, catechizing_data: CatechizingCreateDTO) -> CatechizingDTO:
        pass

    def get_catechizing_by_id(self, catechizing_id: int) -> Optional[CatechizingDTO]:
        pass # ID se refiere a Person.IDPerson

    def get_catechizings_by_class(self, class_id: int, skip: int = 0, limit: int = 100) -> List[CatechizingDTO]:
        pass

    def get_all_catechizings(self, skip: int = 0, limit: int = 100) -> List[CatechizingDTO]:
        pass

    def update_catechizing(self, catechizing_id: int, catechizing_data: CatechizingUpdateDTO) -> Optional[CatechizingDTO]:
        pass

    def delete_catechizing(self, catechizing_id: int) -> bool:
        pass

    # --- Métodos auxiliares (podrían ser necesarios) ---
    def get_person_by_dni(self, dni: str) -> Optional[PersonDTO]:
        pass

    def get_user_by_username(self, username: str) -> Optional[UserDTO]:
        pass