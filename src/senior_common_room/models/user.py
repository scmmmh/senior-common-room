"""Models related to the user."""
from cerberus import Validator
from sqlalchemy import (Column, Integer, String)
from sqlalchemy_json import NestedMutableJson

from .meta import Base
from ..validation import ValidationException, jsonapi_type_validator, jsonapi_id_validator


USER_SCHEMA = {
    'type': jsonapi_type_validator('users'),
    'id': jsonapi_id_validator(required=False),
    'attributes': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'email': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'token': {
                'type': 'string',
                'required': False,
                'empty': False,
            },
            'status': {
                'type': 'string',
                'required': True,
                'allowed': ['active', 'blocked'],
            },
        }
    }
}


class User(Base):
    """Database model representing the user."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(length=255), unique=True)
    name = Column(String(length=255))
    token = Column(String(length=255))
    avatar = Column(String(length=255), unique=True)
    timezone = Column(String(length=255))
    roles = Column(NestedMutableJson)
    blocked_users = Column(NestedMutableJson)
    status = Column(String(length=255))

    @classmethod
    def from_jsonapi(cls, data: dict):  # noqa: ANN102, ANN206
        """Create a new ``User`` instance from the ``data``.

        Applies validation to the incoming data, which must be in JSONAPI format.

        :param data: The data to use to instantiate the new instance
        :type data: dict
        :throws: ValidationException on validation errors
        """
        validator = Validator(USER_SCHEMA)
        if validator.validate(data):
            data = validator.normalized(data)
            if 'id' in data:
                user = User(id=int(data['id']), **data['attributes'])
            else:
                user = User(**data['attributes'])
            return user
        else:
            raise ValidationException(validator.errors)
