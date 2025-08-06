class ParamsMissingException(Exception):
    def __init__(self,message):
        self.message = message


class ConfigMissingException(Exception):
    def __init__(self,message):
        self.message = message


class ExtensionNotSupportException(Exception):
    def __init__(self,message):
        self.message = message


class UnSupportedDataSourceException(Exception):
    def __init__(self,message):
        self.message = message


class UnSupportedDataFrameException(Exception):
    def __init__(self,message):
        self.message = message


class ModuleNotFoundException(Exception):
    def __init__(self,message):
        self.message = message


class MLPlotValueError(ValueError):
    """
    A bad value was passed into a function.
    """

    pass


class ValueError(Exception):
    """
    A bad value was passed into a function.
    """

    def __init__(self,message):
        self.message = message


class ailabWarning(UserWarning):
    pass


class TypeError(TypeError):
    pass


class AttributeError(Exception):
    """
    A required attribute is missing on the estimator.
    """

    pass


class KeyError(KeyError):
    """
    An invalid key was used in a hash (dict or set).
    """

    pass


class DataWarning(Warning):
    """
    An invalid key was used in a hash (dict or set).
    """

    pass


class ModelError(Exception):
    """
    A problem when interacting with sklearn or the ml framework.
    """

    def __init__(self,message):
        self.message = message


class NotFitted(ModelError):
    """
    An action was called that requires a fitted model.
    """

    @classmethod
    def from_estimator(cls,estimator,method = None):
        method = method or "this method"
        message = (
            "this {} instance is not fitted yet, please call fit "
            "with the appropriate arguments before using {}"
        ).format(estimator.__class__.__name__,method)
        return cls(message)
