class ACNError(Exception):
    pass

class KeyStructureError(ACNError):
    pass

class ConfigurationError(ACNError):
    pass

class DataError(ACNError):
    pass