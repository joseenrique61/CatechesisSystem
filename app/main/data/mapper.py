from __future__ import annotations # Permite usar nombres de clase como tipos antes de su definición completa (Python 3.7+)
import typing
import sys
import inspect
from sqlalchemy.orm.base import Mapped

from app.main.data.dtos.base_dtos import *

# Para compatibilidad con Python < 3.9 para get_origin, get_args
if hasattr(typing, 'get_origin'):
    get_origin = typing.get_origin
    get_args = typing.get_args
else:
    # Fallback simple para versiones antiguas (puede no ser perfecto para todos los casos)
    def get_origin(tp):
        return getattr(tp, '__origin__', None)
    def get_args(tp):
        return getattr(tp, '__args__', ())

# Definimos un TypeVar para la anotación de retorno de from_other
# Esto ayuda a que el type checker sepa que from_other devuelve una instancia de la clase en la que se llama.
_T = typing.TypeVar('_T', bound='Mappable')

class Mappable:
    """
    Clase base para objetos que pueden ser creados a partir de otro objeto
    con atributos de nombres coincidentes.
    """

    def __init__(self, **kwargs):
        """
        Un __init__ genérico que puede ser útil, aunque las subclases
        pueden y a menudo deben definir su propio __init__ más explícito
        para un mejor type checking y claridad.
        Si las subclases definen su propio __init__, este no será llamado
        a menos que se use super().__init__(**kwargs).
        """
        # type_hints = typing.get_type_hints(self.__class__)
        # for key, value in kwargs.items():
        #     if key in type_hints:
        #         setattr(self, key, value)
        # El __init__ de las subclases es más importante para from_other.
        pass

    @classmethod
    def _evaluate_forward_ref(cls, type_hint: typing.Any, module_globals: dict, current_globals: dict) -> typing.Any:
        """Intenta evaluar un ForwardRef explícitamente."""
        if isinstance(type_hint, typing.ForwardRef):
            # En Python 3.9+ ForwardRef tiene un método _evaluate
            if hasattr(type_hint, '_evaluate'):
                try:
                    return type_hint._evaluate(module_globals, current_globals, frozenset())
                except Exception:
                    # A veces necesita también los locals de donde se define la clase original,
                    # pero es difícil obtenerlos aquí. module_globals suele ser suficiente.
                    pass # Intentará con el global de Mappable si falla
            # Fallback para versiones anteriores o si _evaluate falla
            try:
                return eval(type_hint.__forward_arg__, module_globals, current_globals)
            except Exception:
                try: # Último intento con los globals de Mappable
                    return eval(type_hint.__forward_arg__, globals(), current_globals) # globals() aquí es de mapper.py
                except Exception as e:
                    # print(f"DEBUG: Falló la evaluación manual de ForwardRef {type_hint.__forward_arg__}: {e}")
                    return type_hint # Devolver el ForwardRef sin resolver si todo falla
        return type_hint

    @classmethod
    def _from_other_obj(cls: typing.Type[_T], db_obj: typing.Any, custom_var_path: str = "", current_depth: int = 0, debug = False, depth: int = -1, ignore_optional: bool = False, ignore_lists: bool = False, include: list[str] = [], exclude: list[str] = [], current_param_name: str = "") -> _T:
        if db_obj is None:
            raise ValueError(f"No se puede crear {cls.__name__} desde un objeto None.")

        if f"{type(db_obj).__name__}." in current_param_name:
            return None

        kwargs_for_constructor = {}
        
        # Contexto para get_type_hints
        try:
            # Globals del módulo donde 'cls' (e.g., PersonDTO) está definida
            module_cls_defined_in = sys.modules[cls.__module__]
            module_globals = module_cls_defined_in.__dict__
        except (KeyError, AttributeError) as e:
            if debug: print(f"ADVERTENCIA (Mappable): No se pudo obtener el módulo para {cls.__name__} (de {cls.__module__}). Error: {e}. Usando globals() del módulo Mappable (mapper.py).")
            module_globals = globals() # Fallback a los globals de mapper.py

        # Globals del módulo Mappable (puede ser útil como fallback para resolver tipos genéricos de typing)
        mapper_module_globals = globals()

        if debug: print(f"\n[DEBUG] Mapeando a {cls.__name__} (definida en {cls.__module__}) desde {type(db_obj).__name__}")
        if debug: print(f"[DEBUG] Usando module_globals del módulo: {cls.__module__}")

        try:
            # localns puede ser útil si las clases se definen dentro de funciones,
            # pero para DTOs a nivel de módulo, module_globals es la clave.
            # Le pasamos ambos para mayor robustez.
            loc_type_hints_raw = typing.get_type_hints(cls, globalns=module_globals, localns=module_globals) # localns=module_globals es un poco redundante pero inofensivo
        except Exception as e:
            if debug: print(f"ERROR (Mappable): Falló typing.get_type_hints para {cls.__name__}: {e}. Usando __annotations__.")
            if hasattr(cls, '__annotations__'):
                loc_type_hints_raw = cls.__annotations__
            else:
                raise TypeError(f"No se pueden obtener anotaciones de tipo para {cls.__name__}") from e

        # Procesar y resolver ForwardRefs que get_type_hints no pudo resolver
        loc_type_hints = {}
        for attr_name, raw_type in loc_type_hints_raw.items():
            resolved_type = raw_type
            if isinstance(raw_type, str): # Si `from __future__ import annotations` está activo, son strings
                try:
                    # Intenta evaluar la cadena como un tipo
                    resolved_type = eval(raw_type, module_globals, mapper_module_globals) # Darle ambos contextos
                except Exception:
                    if debug: print(f"[DEBUG]   No se pudo evaluar la cadena de tipo '{raw_type}' para '{attr_name}'. Usando ForwardRef.")
                    resolved_type = typing.ForwardRef(raw_type) # Tratarla como ForwardRef

            if get_origin(resolved_type) is Mapped:
                resolved_type = get_args(resolved_type)[0]

            if isinstance(resolved_type, typing.ForwardRef):
                if debug: print(f"[DEBUG]   Atributo '{attr_name}' tiene ForwardRef: {resolved_type.__forward_arg__}. Intentando resolver...")
                evaluated = cls._evaluate_forward_ref(resolved_type, module_globals, mapper_module_globals)
                if evaluated is resolved_type and debug: # No se resolvió
                     print(f"[DEBUG]   FALLO AL RESOLVER ForwardRef: {resolved_type.__forward_arg__} para '{attr_name}'. El tipo seguirá siendo ForwardRef.")
                resolved_type = evaluated
            loc_type_hints[attr_name] = resolved_type
        
        if debug: print(f"[DEBUG] Anotaciones para {cls.__name__} (resueltas): {loc_type_hints}")

        for attr_name, loc_attr_type in loc_type_hints.items():
            temp_current_attr_name = f"{current_param_name}{'.' if current_param_name != '' else ''}{attr_name}"
            if temp_current_attr_name in exclude:
                continue
            
            if debug: print(f"[DEBUG] Procesando atributo '{temp_current_attr_name}' con tipo resuelto '{loc_attr_type}' (repr: {repr(loc_attr_type)}, tipo de esta variable: {type(loc_attr_type)})")

            if not hasattr(db_obj, attr_name):
                # ... (lógica de opcional si falta el atributo, sin cambios) ...
                origin_type_check_optional = get_origin(loc_attr_type)
                args_type_check_optional = get_args(loc_attr_type)
                is_optional_when_missing = (origin_type_check_optional is typing.Union and type(None) in args_type_check_optional)
                
                if is_optional_when_missing:
                    kwargs_for_constructor[attr_name] = None
                elif debug: print(f"[DEBUG]   Atributo '{attr_name}' no en db_obj. Omitiendo.")
                continue

            db_attr_value = getattr(db_obj, attr_name)
            # ... (lógica de valor DB, sin cambios) ...

            actual_loc_type_for_conversion = loc_attr_type
            origin_type = get_origin(loc_attr_type)
            args_type = get_args(loc_attr_type)
            is_optional_target = False

            if origin_type is typing.Union and type(None) in args_type:
                if ignore_optional and temp_current_attr_name not in include:
                    continue
                
                is_optional_target = True
                non_none_types = [t for t in args_type if t is not type(None) and t is not None]
                if len(non_none_types) == 1:
                    potential_type = non_none_types[0]
                    # Si este tipo también es un ForwardRef o una cadena, intentar resolverlo
                    if isinstance(potential_type, str):
                        try: potential_type = eval(potential_type, module_globals, mapper_module_globals)
                        except: potential_type = typing.ForwardRef(potential_type)
                    if isinstance(potential_type, typing.ForwardRef):
                        potential_type = cls._evaluate_forward_ref(potential_type, module_globals, mapper_module_globals)
                    actual_loc_type_for_conversion = potential_type
                else: # Union más compleja o error en resolución
                    if debug: print(f"[DEBUG]   Advertencia: Tipo Optional complejo o no resuelto para '{attr_name}': {args_type}. Usando el tipo Union original para lógica.")
                    actual_loc_type_for_conversion = loc_attr_type # Mantener el Union
            
            if debug: print(f"[DEBUG]   Tipo 'loc' actual para conversión ('{attr_name}'): {actual_loc_type_for_conversion} (repr: {repr(actual_loc_type_for_conversion)}, tipo de esta variable: {type(actual_loc_type_for_conversion)})")

            if db_attr_value is None:
                # ... (lógica de db_attr_value es None, sin cambios) ...
                kwargs_for_constructor[attr_name] = None # Siempre se puede pasar None si el valor de DB es None
            
            # Mapeo de Listas de Mappables
            elif get_origin(actual_loc_type_for_conversion) is list or get_origin(loc_attr_type) is list:
                if ignore_lists and temp_current_attr_name not in include:
                    continue

                list_item_type_actual = actual_loc_type_for_conversion # Por si actual_loc_type_for_conversion ya es el tipo del item
                if get_origin(actual_loc_type_for_conversion) is list: # Si actual_loc_type_for_conversion es List[X]
                    list_args = get_args(actual_loc_type_for_conversion)
                    if list_args:
                        list_item_type_actual = list_args[0]
                        # Resolver si es ForwardRef o string
                        if isinstance(list_item_type_actual, str):
                            try: list_item_type_actual = eval(list_item_type_actual, module_globals, mapper_module_globals)
                            except: list_item_type_actual = typing.ForwardRef(list_item_type_actual)
                        if isinstance(list_item_type_actual, typing.ForwardRef):
                            list_item_type_actual = cls._evaluate_forward_ref(list_item_type_actual, module_globals, mapper_module_globals)
                    else: # List sin tipo especificado, o List[Any]
                        if debug: print(f"[DEBUG]   '{attr_name}' es una lista pero sin tipo de item especificado en 'loc'. Se copiará tal cual.")
                        kwargs_for_constructor[attr_name] = list(db_attr_value) if db_attr_value is not None else []
                        continue
                
                if debug: print(f"[DEBUG]   '{attr_name}' es una lista. Tipo de item esperado: {list_item_type_actual}")
                
                if isinstance(list_item_type_actual, type) and issubclass(list_item_type_actual, Mappable):
                    if db_attr_value is not None:
                        if depth != -1 and current_depth >= depth and temp_current_attr_name not in include:
                            if debug: print(f"[DEBUG]   '{attr_name}' (tipo {actual_loc_type_for_conversion.__name__}) es subclase de Mappable. Depth máximo alcanzado")
                            continue
                        kwargs_for_constructor[attr_name] = []
                        for item in db_attr_value:
                            temp_item = list_item_type_actual._from_other_obj(item, debug=debug, custom_var_path=custom_var_path, current_depth=current_depth + 1, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name=temp_current_attr_name)
                            if temp_item is None:
                                continue
                            kwargs_for_constructor[attr_name].append(temp_item)
                        # kwargs_for_constructor[attr_name] = [list_item_type_actual._from_other_obj(item, debug=debug, custom_var_path=custom_var_path, current_depth=current_depth + 1, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name=temp_current_attr_name) for item in db_attr_value]
                    else:
                        kwargs_for_constructor[attr_name] = [] if not is_optional_target else None
                    if debug: print(f"[DEBUG]     Mapeada lista de Mappables para '{attr_name}'.")
                else:
                    if debug: print(f"[DEBUG]     '{attr_name}' es una lista de tipos no-Mappable o no resueltos. Se copiará tal cual.")
                    kwargs_for_constructor[attr_name] = list(db_attr_value) if db_attr_value is not None else ([] if not is_optional_target else None)

            # Mapeo de Mappables individuales (no listas)
            elif isinstance(actual_loc_type_for_conversion, type) and issubclass(actual_loc_type_for_conversion, Mappable):
                if depth != -1 and current_depth >= depth and temp_current_attr_name not in include and is_optional_target:
                    if debug: print(f"[DEBUG]   '{attr_name}' (tipo {actual_loc_type_for_conversion.__name__}) es subclase de Mappable. LlamDepth máximo alcanzado")
                    continue
                if debug: print(f"[DEBUG]   '{attr_name}' (tipo {actual_loc_type_for_conversion.__name__}) es subclase de Mappable. Llamando recursivamente a from_db_obj.")
                kwargs_for_constructor[attr_name] = actual_loc_type_for_conversion._from_other_obj(db_attr_value, debug=debug, custom_var_path=custom_var_path, current_depth=current_depth + 1, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name=temp_current_attr_name)
            
            # elif hasattr(actual_loc_type_for_conversion, '_from_db_obj') and callable(getattr(actual_loc_type_for_conversion, 'from_db_obj')):
            #     if debug: print(f"[DEBUG]   '{attr_name}' (tipo {getattr(actual_loc_type_for_conversion, '__name__', repr(actual_loc_type_for_conversion))}) tiene from_db_obj. Llamando recursivamente.")
            #     kwargs_for_constructor[attr_name] = actual_loc_type_for_conversion._from_db_obj(db_attr_value, debug=debug)
            
            else: # Asignación directa
                if debug: print(f"[DEBUG]   '{attr_name}' no es Mappable anidado/lista de Mappables o no se reconoce. Asignación directa.")

                if custom_var_path != "":
                    db_attr_value = getattr(db_attr_value, custom_var_path)
                kwargs_for_constructor[attr_name] = db_attr_value
        
        if debug: print(f"[DEBUG] Argumentos finales para el constructor de {cls.__name__}: {kwargs_for_constructor}")
        try:
            instance = cls(**kwargs_for_constructor)
        except TypeError as e:
            if debug:
                print(f"ERROR_CONSTRUCTOR (Mappable): Falló al instanciar {cls.__name__} con kwargs: {kwargs_for_constructor}")
                # ... (código de debug para firma del constructor) ...
                try:
                    init_method = cls.__init__
                    # Si es un dataclass y no tiene __init__ explícito, __init__ es object.__init__.
                    # La firma real está en la clase misma para dataclasses.
                    target_for_signature = cls if init_method is object.__init__ and hasattr(cls, '__dataclass_fields__') else init_method
                    sig = inspect.signature(target_for_signature)
                    print(f"[DEBUG_CONSTRUCTOR] Firma de {cls.__name__} (o su __init__): {sig}")
                except Exception as e_sig:
                    print(f"[DEBUG_CONSTRUCTOR] No se pudo obtener la firma de {cls.__name__}.__init__: {e_sig}")
            raise 
        return instance

    @classmethod
    def from_other_obj(cls: typing.Type[_T], db_obj: typing.Any, depth: int = 1, custom_var_path: str = "", ignore_optional: bool = False, ignore_lists: bool = True, include: list[str] = [], exclude: list[str] = []) -> _T:
        """
        Crea una instancia de 'cls' (una clase *DTO) a partir de 'db_obj', 
        mapeando atributos con el mismo nombre.
        Maneja recursivamente los atributos que también son Mappable.
        """
        return cls._from_other_obj(db_obj, custom_var_path=custom_var_path, current_depth=0, depth=depth, ignore_optional=ignore_optional, ignore_lists=ignore_lists, include=include, exclude=exclude, current_param_name="")