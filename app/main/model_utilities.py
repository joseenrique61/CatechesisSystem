from app import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

def insert_model(model) -> tuple[object, bool]:
    """
    Insert a model into the database.
    :param model: The model to insert.
    :return: True if the model was inserted successfully, False otherwise. The model itself, whether it is the passed to the function or the one from the db, is returned.
    """
    try:
        db.session.add(model)
        db.session.flush()
        return model, True
    except IntegrityError as e:
        db.session.rollback()
        # result = db.session.query(model.__class__).filter_by(**(model.__dict__)).one()

        mapper = inspect(type(model)) # Obtiene el mapper para la clase del modelo
        filter_conditions = {}

        for column in mapper.columns: # Itera sobre las columnas mapeadas
            column_name = column.key # Nombre del atributo en el modelo
            if hasattr(model, column_name):
                value = getattr(model, column_name)
                # Solo incluir en el filtro si el valor no es None
                # y no es una clave primaria si el valor es el default (ej. 0 para int autoincremental no asignado)
                # Esto último es más complejo de generalizar, por ahora solo verificamos None.
                if value is not None:
                    # Evitar claves primarias no establecidas si son autoincrementales
                    # Esta lógica puede necesitar ser más robusta
                    is_pk_and_default = False
                    if column.primary_key:
                        # Si es PK y el tipo es int y el valor es 0, podríamos asumirlo como no establecido
                        # Esto es una simplificación.
                        if isinstance(value, int) and value == 0:
                                is_pk_and_default = True # Podría ser más específico (ej. si es autoincrement)


                    if not is_pk_and_default:
                        filter_conditions[column_name] = value

        if not filter_conditions:
            print("No se generaron condiciones de filtro válidas a partir de los atributos del modelo.")
            return None, False

        print(f"Buscando {type(model).__name__} con filtros: {filter_conditions}")
        return db.session.query(type(model)).filter_by(**filter_conditions).one_or_none(), False
    except Exception as e:
        db.session.rollback()
        raise e