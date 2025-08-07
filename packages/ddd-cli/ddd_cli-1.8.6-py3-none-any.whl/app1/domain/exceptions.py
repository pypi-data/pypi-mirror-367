
# domain/exceptions.py

class PromotionError(Exception):
    """Excepción base para errores relacionados con el dominio Promotion."""
    pass


class PromotionValueError(PromotionError):
    """Error de valor en atributos de la entidad Promotion."""
    def __init__(self, field: str, detail: str):
        self.field = field
        self.detail = detail
        super().__init__(f"Error en el campo '{field}': {detail}")


class PromotionValidationError(PromotionError):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("La validación de la Promotion falló.")


class PromotionAlreadyExistsError(PromotionError):
    """Cuando se intenta crear una Promotion que ya existe."""
    def __init__(self, cause):
        self.cause = cause
        super().__init__(f"Promotion existe.")


class PromotionNotFoundError(PromotionError):
    """Cuando se intenta acceder a una Promotion inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"Promotion con ID {id} no encontrada.")


class PromotionOperationNotAllowedError(PromotionError):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"La operación '{operation_name}' no está permitida en esta Promotion.")        


class PromotionPermissionError(PromotionError):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("No tienes permisos para realizar esta acción sobre la Promotion.")      
