# domain/exceptions.py

class Entity1Error(Exception):
    """Excepción base para errores relacionados con el dominio Entity1."""
    pass


class Entity1ValueError(Entity1Error):
    """Error de valor en atributos de la entidad Entity1."""
    def __init__(self, field: str, detail: str):
        self.field = field
        self.detail = detail
        super().__init__(f"Error en el campo '{field}': {detail}")


class Entity1ValidationError(Entity1Error):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la Entity1 falló.")


class Entity1AlreadyExistsError(Entity1Error):
    """Cuando se intenta crear una Entity1 que ya existe."""
    def __init__(self, cause):
        self.cause = cause
        super().__init__(f"Entity1 existe.")


class Entity1NotFoundError(Entity1Error):
    """Cuando se intenta acceder a una Entity1 inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"Entity1 con ID {id} no encontrada.")


class Entity1OperationNotAllowedError(Entity1Error):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta Entity1.")        


class Entity1PermissionError(Entity1Error):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la Entity1.")      
