from email_validator import validate_email, EmailNotValidError
from hashlib import sha512
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy import and_

from ..models import User
from ..routes import decode_route
from ..util import Validator


def valid_email(field, value, error):
    """Validates that the ``value`` in ``field`` is a valid e-mail address.

    :param field: The field being validated
    :type field: str
    :param value: The field value to validate
    :param error: Callback to set the error message, if the ``value`` is not valid
    """
    try:
        validate_email(value, check_deliverability=False)
    except EmailNotValidError as e:
        error(field, str(e))


login_schema = {'email': {'type': 'string', 'empty': False, 'validator': valid_email},
                'password': {'type': 'string', 'empty': False},
                'redirect': {'type': 'string'},
                'csrf_token': {'type': 'string'}}


@view_config(route_name='user.login', renderer='scr:templates/users/login.jinja2')
def login(request):
    """Handle logging the user in."""
    if request.method == 'POST':
        validator = Validator(login_schema)
        if validator.validate(request.params):
            user = request.dbsession.query(User).filter(and_(User.email == request.params['email'].lower(),
                                                             User.status == 'active')).first()
            if user:
                hash = sha512()
                hash.update(user.salt.encode('utf-8'))
                hash.update(b'$$')
                hash.update(request.params['password'].encode('utf-8'))
                if user.password == hash.hexdigest():
                    request.session['user-id'] = user.id
                    return HTTPFound(location=decode_route(request, 'user.view', {'uid': user.id}))
            return {'errors': {'email': ['Either there is no user with this e-mail address ' +
                                         'or the password is incorrect.'],
                               'password': ['Either there is no user with this e-mail address ' +
                                            'or the password is incorrect.']},
                    'values': request.params}
        else:
            return {'errors': validator.errors, 'values': request.params}
    return {}


@view_config(route_name='user.logout', renderer='scr:templates/users/logout.jinja2')
def logout(request):
    """Handle logging the user out."""
    if request.method == 'POST':
        request.session.clear()
        return HTTPFound(location=request.route_url('root'))
    return {}
