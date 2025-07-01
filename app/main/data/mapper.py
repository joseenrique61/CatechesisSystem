# mapper.py (REFACTORIZADO Y CORREGIDO)

from __future__ import annotations
import typing
import sys
import inspect
from bson import ObjectId

# Para compatibilidad con Python < 3.9
if hasattr(typing, 'get_origin'):
    get_origin = typing.get_origin
    get_args = typing.get_args
else:
    def get_origin(tp):
        return getattr(tp, '__origin__', None)
    def get_args(tp):
        return getattr(tp, '__args__', ())

_T = typing.TypeVar('_T', bound='Mappable')

class Mappable:
    """
    Clase base para objetos que pueden ser creados a partir de otro objeto
    con atributos de nombres coincidentes.
    """
    
    @classmethod
    def _evaluate_forward_ref(cls, type_hint: typing.Any, module_globals: dict, current_globals: dict) -> typing.Any:
        if isinstance(type_hint, typing.ForwardRef):
            if hasattr(type_hint, '_evaluate'):
                try:
                    return type_hint._evaluate(module_globals, current_globals, frozenset())
                except Exception:
                    pass
            try:
                return eval(type_hint.__forward_arg__, module_globals, current_globals)
            except Exception:
                try:
                    return eval(type_hint.__forward_arg__, globals(), current_globals)
                except Exception:
                    return type_hint
        return type_hint

    @classmethod
    def _from_other_obj(cls: typing.Type[_T], db_obj: typing.Any, custom_var_path: str = "", current_depth: int = 0, debug = False, depth: int = -1, ignore_optional: bool = False, ignore_lists: bool = False, include: list[str] = [], exclude: list[str] = [], current_param_name: str = "") -> _T:
        if db_obj is None:
            # Si el destino es opcional, devolver None está bien.
            # La verificación se hará en el constructor de Pydantic.
            return None

        kwargs_for_constructor = {}
        
        try:
            module_cls_defined_in = sys.modules[cls.__module__]
            module_globals = module_cls_defined_in.__dict__
        except (KeyError, AttributeError):
            module_globals = globals()

        mapper_module_globals = globals()

        try:
            loc_type_hints_raw = typing.get_type_hints(cls, globalns=module_globals, localns=module_globals)
        except Exception:
            if hasattr(cls, '__annotations__'):
                loc_type_hints_raw = cls.__annotations__
            else:
                raise TypeError(f"No se pueden obtener anotaciones de tipo para {cls.__name__}")

        loc_type_hints = {}
        for attr_name, raw_type in loc_type_hints_raw.items():
            resolved_type = raw_type
            if isinstance(raw_type, str):
                try:
                    resolved_type = eval(raw_type, module_globals, mapper_module_globals)
                except Exception:
                    resolved_type = typing.ForwardRef(raw_type)

            if isinstance(resolved_type, typing.ForwardRef):
                resolved_type = cls._evaluate_forward_ref(resolved_type, module_globals, mapper_module_globals)
            
            loc_type_hints[attr_name] = resolved_type
        
        for attr_name, loc_attr_type in loc_type_hints.items():
            temp_current_attr_name = f"{current_param_name}{'.' if current_param_name else ''}{attr_name}"
            if temp_current_attr_name in exclude:
                continue

            if not hasattr(db_obj, attr_name):
                origin_type_check = get_origin(loc_attr_type)
                is_optional_when_missing = (origin_type_check is typing.Union and type(None) in get_args(loc_attr_type))
                if is_optional_when_missing:
                    kwargs_for_constructor[attr_name] = None
                continue

            db_attr_value = getattr(db_obj, attr_name)

            actual_loc_type_for_conversion = loc_attr_type
            origin_type = get_origin(loc_attr_type)
            args_type = get_args(loc_attr_type)
            is_optional_target = False

            if origin_type is typing.Union and type(None) in args_type:
                if ignore_optional and temp_current_attr_name not in include:
                    continue
                is_optional_target = True
                non_none_types = [t for t in args_type if t is not type(None)]
                if len(non_none_types) == 1:
                    potential_type = non_none_types[0]
                    if isinstance(potential_type, str):
                        try: potential_type = eval(potential_type, module_globals, mapper_module_globals)
                        except: potential_type = typing.ForwardRef(potential_type)
                    if isinstance(potential_type, typing.ForwardRef):
                        potential_type = cls._evaluate_forward_ref(potential_type, module_globals, mapper_module_globals)
                    actual_loc_type_for_conversion = potential_type
            
            if db_attr_value is None:
                kwargs_for_constructor[attr_name] = None
            
            elif get_origin(actual_loc_type_for_conversion) is list:
                if ignore_lists and temp_current_attr_name not in include:
                    continue
                list_item_type = get_args(actual_loc_type_for_conversion)[0] if get_args(actual_loc_type_for_conversion) else None
                if list_item_type and isinstance(list_item_type, type) and issubclass(list_item_type, Mappable):
                    if depth != -1 and current_depth >= depth and temp_current_attr_name not in include:
                        continue
                    kwargs_for_constructor[attr_name] = [
                        list_item_type._from_other_obj(item, debug=debug, custom_var_path=custom_var_path, current_depth=current_depth + 1, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name=temp_current_attr_name)
                        for item in db_attr_value if item is not None
                    ]
                else:
                    kwargs_for_constructor[attr_name] = list(db_attr_value) if db_attr_value is not None else ([] if not is_optional_target else None)

            elif isinstance(actual_loc_type_for_conversion, type) and issubclass(actual_loc_type_for_conversion, Mappable):
                if depth != -1 and current_depth >= depth and temp_current_attr_name not in include and is_optional_target:
                    continue
                kwargs_for_constructor[attr_name] = actual_loc_type_for_conversion._from_other_obj(db_attr_value, debug=debug, custom_var_path=custom_var_path, current_depth=current_depth + 1, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name=temp_current_attr_name)
            
            else: # Asignación directa
                # <<<--- INICIO DE LA LÓGICA CORREGIDA Y SIMPLIFICADA ---
                # Esta es la parte más importante de la corrección.
                if debug: print(f"[DEBUG]   '{attr_name}' no es Mappable anidado/lista de Mappables o no se reconoce. Asignación directa.")
                
                value_to_assign = getattr(db_obj, attr_name)
                
                if custom_var_path != "":
                    value_to_assign = getattr(value_to_assign, custom_var_path)
                kwargs_for_constructor[attr_name] = value_to_assign

                # Convertimos ObjectId a string específicamente para el campo 'id'.
                if attr_name == 'id' and isinstance(value_to_assign, ObjectId):
                    kwargs_for_constructor[attr_name] = str(value_to_assign)
                else:
                    # Para todos los demás tipos simples (str, int, bool, etc.),
                    # simplemente asignamos el valor directamente.
                    kwargs_for_constructor[attr_name] = value_to_assign
                # --- FIN DE LA LÓGICA CORREGIDA Y SIMPLIFICADA --->>>
        
        try:
            # Pydantic es estricto, así que solo pasamos los kwargs que la clase espera.
            # Obtenemos los campos definidos en el modelo Pydantic.
            model_fields = cls.model_fields.keys()
            final_kwargs = {k: v for k, v in kwargs_for_constructor.items() if k in model_fields}
            
            instance = cls(**final_kwargs)
        except Exception as e:
            if debug:
                print(f"ERROR_CONSTRUCTOR (Mappable): Falló al instanciar {cls.__name__} con kwargs: {final_kwargs}")
                print(f"Excepción: {e}")
            raise
        return instance

    @classmethod
    def from_other_obj(cls: typing.Type[_T], db_obj: typing.Any, depth: int = 1, custom_var_path: str = "", ignore_optional: bool = False, ignore_lists: bool = True, include: list[str] = [], exclude: list[str] = []) -> _T:
        """
        Crea una instancia de 'cls' (una clase DTO) a partir de 'db_obj', 
        mapeando atributos con el mismo nombre.
        """
        if db_obj is None:
            return None
        return cls._from_other_obj(db_obj, custom_var_path=custom_var_path, current_depth=0, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name="")