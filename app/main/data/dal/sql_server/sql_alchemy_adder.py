from sqlalchemy.orm import Session, object_session
from sqlalchemy import Index, PrimaryKeyConstraint
from sqlalchemy.exc import IntegrityError
from typing import Type, TypeVar, Optional, Any, Callable, List as TypingList
from app.main.data.dal.sql_server.sql_models import BaseModel
from app.main.data.duplicate_column_exception import DuplicateColumnException

# --- Tipos y Funciones Helper (pueden estar fuera de la clase o ser estáticos dentro) ---
SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=BaseModel) # O tu db.Model

def default_is_sqlalchemy_model(obj_to_check: Any) -> bool:
    if obj_to_check is None: return False
    if hasattr(obj_to_check, '__mapper__') and hasattr(obj_to_check, '__table__'):
        return True
    obj_type = type(obj_to_check)
    if isinstance(obj_type, type) and issubclass(obj_type, BaseModel):
         return True
    return False

class DBManager:

    @staticmethod
    def _get_unique_constraints_for_model(model_class: Type) -> TypingList[TypingList[str]]:
        """
        Método estático para obtener constraints.
        """
        if hasattr(model_class, '__table_args__'):
            constraints = getattr(model_class, '__table_args__')
            if not constraints:
                return []
            final_constraints = []
            
            for constraint in constraints:
                temp_constraint = []
                if type(constraint) is Index:
                    if not constraint.unique:
                        continue
                    
                    for column in constraint._columns._collection:
                        temp_constraint.append(column[0])
                elif type(constraint) is PrimaryKeyConstraint:
                    temp_constraint.append(constraint.columns._collection[0][0])
                final_constraints.append(temp_constraint)
                
            return final_constraints
        return []

    @staticmethod
    def _get_or_create_single(
        session: Session, # <--- Argumento añadido
        model_instance: SQLAlchemyModel,
        unique_constraints: TypingList[TypingList[str]],
        ignore_duplicate_error: bool
    ) -> tuple[SQLAlchemyModel, bool, Optional[TypingList[str]]]:
        """
        Lógica para una sola instancia. Ahora es estático y recibe la sesión.
        """
        model_class = type(model_instance)

        try:
            session.flush()
            # 1. Intentar encontrar por constraints
            if unique_constraints:
                for constraint_attrs in unique_constraints:
                    # ... (misma lógica de construcción de filter_conditions y query) ...
                    if not constraint_attrs: continue 
                    filter_conditions = {}
                    valid_constraint = True
                    for attr_name in constraint_attrs:
                        if hasattr(model_instance, attr_name):
                            attr_value = getattr(model_instance, attr_name)
                            filter_conditions[attr_name] = attr_value
                        else:
                            valid_constraint = False
                            break
                    if not valid_constraint or not filter_conditions: continue
                    if next((result for result in filter_conditions.values() if result is not None), None) is None:
                        continue
                    existing_instance = session.query(model_class).filter_by(**filter_conditions).one_or_none()
                    if existing_instance:
                        if model_instance.__should_raise_error_if_duplicate__ and not ignore_duplicate_error:
                            raise DuplicateColumnException(model_class.__name__, constraint_attrs)

                        if object_session(model_instance) == session and model_instance in session.new:
                            session.expunge(model_instance)
                        return existing_instance, False, constraint_attrs

        # 2. Si no se encontró, intentar añadir
            for rel_prop in model_instance.__mapper__.relationships:
                attr_name = rel_prop.key
                attr_value = getattr(model_instance, attr_name)
                if rel_prop.uselist:
                    new_list = []
                    for item in attr_value:
                        if item in session:
                            new_list.append(item)
                    setattr(model_instance, attr_name, new_list)
                else:
                    if attr_value and object_session(attr_value) is None:
                        setattr(model_instance, attr_name, None)

            current_instance_session = object_session(model_instance)
            if current_instance_session is None:
                session.add(model_instance)
            elif current_instance_session != session:
                raise ValueError(f"model_instance {model_instance} ({model_class.__name__}) está asociado a una sesión diferente.")
            
            session.flush()
            return model_instance, True, None
        except IntegrityError as e:
            session.rollback()
            # 3. Fallback
            if unique_constraints:
                for constraint_attrs in unique_constraints:
                    # ... (misma lógica de re-búsqueda) ...
                    if not constraint_attrs: continue
                    filter_conditions = {}
                    for attr_name in constraint_attrs:
                        if hasattr(model_instance, attr_name):
                            filter_conditions[attr_name] = getattr(model_instance, attr_name)
                    if not filter_conditions: continue
                    conflicting_instance = session.query(model_class).filter_by(**filter_conditions).one_or_none()
                    if conflicting_instance:
                        if object_session(model_instance) == session and model_instance in session.new:
                            session.expunge(model_instance)
                        return conflicting_instance, False, constraint_attrs
            
            if object_session(model_instance) == session and model_instance in session.new:
                session.expunge(model_instance)
            raise
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def get_or_create(
        session: Session,
        model_instance: SQLAlchemyModel,
        is_model_func_override: Optional[Callable[[Any], bool]] = None,
        ignore_duplicate_error_for: list[str] = [],
        checked_objects: Optional[set[int]] = None,
        separated_objects: Optional[dict[int, list[SQLAlchemyModel]]] = None, 
        current_object: str = ""
    ) -> tuple[SQLAlchemyModel, bool, Optional[TypingList[str]]]:
        if model_instance is None:
            raise ValueError("model_instance no puede ser None")

        model_class = type(model_instance)
        
        _is_model_func_to_use = is_model_func_override if is_model_func_override else default_is_sqlalchemy_model

        if checked_objects is None:
            checked_objects = set()
        if separated_objects is None:
            separated_objects = dict()

        instance_id = id(model_instance)
        # ... (misma lógica de processed_objects y comprobación de estado de sesión) ...
        if instance_id in checked_objects:
            return None, False, None 
            # else: Continuar para procesar si no está limpio y persistente

        checked_objects.add(instance_id)
        
        # 1. Procesar relaciones anidadas
        if hasattr(model_instance, '__mapper__'):
            for rel_prop in model_instance.__mapper__.relationships:
                attr_name = rel_prop.key
                temp_current_attr_name = f"{current_object}{'.' if current_object != '' else ''}{attr_name}"
                
                is_one_to_many = False
                
                try:
                    attr_value = getattr(model_instance, attr_name)
                except AttributeError: continue

                if hasattr(model_instance, f"ID{attr_name}"):
                    is_one_to_many = True
                
                if attr_value is None and is_one_to_many and (id_attr := getattr(model_instance, f"ID{attr_name}", None)) is not None:
                    id_condition = {f"ID{attr_name}": id_attr}
                    attr_value = session.query(rel_prop.mapper.class_).filter_by(**id_condition).one_or_none()
                    if attr_value is None:
                        continue
                    setattr(model_instance, attr_name, attr_value)

                if rel_prop.uselist: # Colección
                    new_list_items = []
                    current_items_iterable = list(attr_value) if attr_value is not None else []

                    for item_in_list in current_items_iterable:
                        if _is_model_func_to_use(item_in_list):
                            
                            # Llamada recursiva estática
                            persisted_item, _, _ = DBManager.get_or_create(
                                session, # Pasar la sesión
                                item_in_list,
                                is_model_func_override, # Pasar el override
                                ignore_duplicate_error_for,
                                checked_objects,
                                separated_objects = separated_objects,
                                current_object=temp_current_attr_name
                            )
                            if persisted_item is not None and object_session(model_instance) is None:
                                new_list_items.append(persisted_item)
                        else:
                            new_list_items.append(item_in_list)
                    
                    setattr(model_instance, attr_name, new_list_items)

                else: # Relación escalar
                    if _is_model_func_to_use(attr_value):
                        scalar_value_session = object_session(attr_value)
                        
                        if is_one_to_many and (id_attr_value := id(attr_value)) in checked_objects and not scalar_value_session:
                            if separated_objects.get(id_attr_value) is None:
                                separated_objects[id_attr_value] = []
                            separated_objects[id_attr_value].append(model_instance)
                            checked_objects.remove(instance_id)
                            return model_instance, False, None
                        elif scalar_value_session:
                            continue

                        # Llamada recursiva estática
                        persisted_scalar_value, _, _ = DBManager.get_or_create(
                            session, # Pasar la sesión
                            attr_value,
                            is_model_func_override, # Pasar el override
                            ignore_duplicate_error_for,
                            checked_objects,
                            separated_objects = separated_objects,
                            current_object=temp_current_attr_name
                        )

                        setattr(model_instance, attr_name, persisted_scalar_value)
        
        # 2. Procesar la instancia actual
        current_model_constraints = DBManager._get_unique_constraints_for_model(model_class)
        
        # Llamada estática
        persisted_instance, created, conflicting_attrs = DBManager._get_or_create_single(
            session, # Pasar la sesión
            model_instance,
            current_model_constraints,
            ignore_duplicate_error=current_object in ignore_duplicate_error_for
        )

        if instance_id in separated_objects.keys():
            object_to_check = separated_objects.pop(instance_id)
            for item in object_to_check:
                setattr(item, model_class.__name__, persisted_instance)
                DBManager.get_or_create(
                    session, # Pasar la sesión
                    item,
                    is_model_func_override, # Pasar el override
                    checked_objects,
                    separated_objects = separated_objects,
                    current_object=temp_current_attr_name
                )

        return persisted_instance, created, conflicting_attrs