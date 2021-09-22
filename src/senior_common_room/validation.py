"""Helper classes and functions for validation."""
from cerberus.errors import ErrorList


class ValidationException(Exception):
    """Exception class that holds a list of validation errors.

    The errors are available from the ``errors`` property.
    """

    def __init__(self, errors: ErrorList) -> None:  # noqa: ANN101
        """Create a new ValidationException for the given ``errors``.

        :param errors: The errors that caused this :class:`~senior_common_room.validation.ValidationException`
        :type errors: ErrorList
        """
        self.errors = errors


def jsonapi_type_validator(type_name: str) -> dict:
    """Create a validator for JSONAPI types.

    :param type_name: The name of the type to create the validator for.
    :type type_name: str
    :return: Returns the validation schema
    :rtype: dict
    """
    return {
        'type': 'string',
        'required': True,
        'allowed': [type_name],
    }


def jsonapi_id_validator(required: bool) -> dict:
    """Create a validator for a JSONAPI id value.

    :param required: Whether the id value is required.
    :type required: str
    :return: Returns the validation schema
    :rtype: dict
    """
    return {
        'type': 'string',
        'required': required,
        'regex': r'[0-9]+',
    }
