from sqlalchemy.orm import Session, object_session, make_transient, DeclarativeBase
from sqlalchemy import Index, PrimaryKeyConstraint
from sqlalchemy.exc import IntegrityError
from typing import Type, TypeVar, Optional, Any, Callable, get_origin, List as TypingList
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
        unique_constraints: TypingList[TypingList[str]]
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
                        if model_instance.__should_raise_error_if_duplicate__:
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
        processed_objects: Optional[set[int]] = None
    ) -> tuple[SQLAlchemyModel, bool, Optional[TypingList[str]]]:
        if model_instance is None:
            raise ValueError("model_instance no puede ser None")

        model_class = type(model_instance)
        
        _is_model_func_to_use = is_model_func_override if is_model_func_override else default_is_sqlalchemy_model

        if processed_objects is None:
            processed_objects = set()

        instance_id = id(model_instance)
        # ... (misma lógica de processed_objects y comprobación de estado de sesión) ...
        current_instance_session_state = object_session(model_instance)
        if instance_id in processed_objects:
            # if current_instance_session_state == session and not session.is_modified(model_instance, include_collections=False) and model_instance not in session.new and model_instance not in session.deleted:
            return None, False, None 
            # else: Continuar para procesar si no está limpio y persistente

        processed_objects.add(instance_id)
        
        # 1. Procesar relaciones anidadas
        if hasattr(model_instance, '__mapper__'):
            for rel_prop in model_instance.__mapper__.relationships:
                attr_name = rel_prop.key
                try:
                    attr_value = getattr(model_instance, attr_name)
                except AttributeError: continue

                if attr_value is None: continue

                if rel_prop.uselist: # Colección
                    new_list_items = []
                    list_content_changed_or_item_rebound = False
                    current_items_iterable = list(attr_value) if attr_value is not None else []

                    for item_in_list in current_items_iterable:
                        if _is_model_func_to_use(item_in_list):
                            item_session = object_session(item_in_list)
                            if item_session is not None and item_session != session:
                                make_transient(item_in_list)
                            
                            # Llamada recursiva estática
                            persisted_item, _, _ = DBManager.get_or_create(
                                session, # Pasar la sesión
                                item_in_list,
                                is_model_func_override, # Pasar el override
                                processed_objects
                            )
                            if persisted_item is not None and object_session(model_instance) is None:
                                new_list_items.append(persisted_item)
                            if item_in_list is not persisted_item:
                                list_content_changed_or_item_rebound = True
                        else:
                            new_list_items.append(item_in_list)
                    
                    setattr(model_instance, attr_name, new_list_items)

                else: # Relación escalar
                    if _is_model_func_to_use(attr_value):
                        scalar_value_session = object_session(attr_value)
                        if scalar_value_session is not None and scalar_value_session != session:
                            make_transient(attr_value)
                        
                        # Llamada recursiva estática
                        persisted_scalar_value, _, _ = DBManager.get_or_create(
                            session, # Pasar la sesión
                            attr_value,
                            is_model_func_override, # Pasar el override
                            processed_objects
                        )
                        # if attr_value is not persisted_scalar_value:
                        setattr(model_instance, attr_name, persisted_scalar_value)
        
        # 2. Procesar la instancia actual
        current_model_constraints = DBManager._get_unique_constraints_for_model(model_class)
        
        # Llamada estática
        persisted_instance, created, conflicting_attrs = DBManager._get_or_create_single(
            session, # Pasar la sesión
            model_instance,
            current_model_constraints
        )
        
        return persisted_instance, created, conflicting_attrs