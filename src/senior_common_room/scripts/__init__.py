import click
import logging.config
import os
import yaml

from cerberus import Validator
from typing import Union

from .server import server
from .database import database


CONFIG_SCHEMA = {
    'database': {
        'type': 'dict',
        'required': True,
        'schema': {
            'dsn': {
                'type': 'string',
                'required': True,
                'empty': False
            }
        }
    },
    'mosquitto': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'server': {
        'type': 'dict',
        'required': True,
        'schema': {
            'base_url': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'prefixes': {
                'type': 'dict',
                'required': True,
                'empty': False,
                'schema': {
                    'avatars': {
                        'type': 'string',
                        'required': True
                    }
                }
            }
        }
    },
    'rooms': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'slug': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'label': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'mapUrl': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'tilesets': {
                    'type': 'list',
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'name': {
                                'type': 'string',
                                'required': True,
                                'empty': False
                            },
                            'url': {
                                'type': 'string',
                                'required': True,
                                'empty': False
                            }
                        }
                    }
                }
            }
        }
    },
    'email': {
        'type': 'dict',
        'required': True,
        'schema': {
            'server': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'secure': {
                'type': 'boolean',
                'default': False
            },
            'from': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'authentication': {
                'type': 'dict',
                'schema': {
                    'username': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    },
                    'password': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    }
                }
            }
        }
    },
    'jitsi': {
        'type': 'dict',
        'schema': {
            'server': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'jwt': {
                'type': 'dict',
                'schema': {
                    'application_id': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    },
                    'client_id': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    },
                    'secret': {
                        'type': 'string',
                        'required': True,
                        'empty': False
                    }
                }
            }
        }
    },
    'storage': {
        'type': 'dict',
        'required': True,
        'schema': {
            'avatars': {
                'type': 'string',
                'required': True
            }
        }
    },
    'logging': {
        'type': 'dict'
    }
}


def validate_config(config: dict) -> Union[list, dict]:
    validator = Validator(CONFIG_SCHEMA)
    if validator.validate(config):
        return validator.normalized(config)
    else:
        error_list = []

        def walk_error_tree(err, path):
            if isinstance(err, dict):
                for key, value in err.items():
                    walk_error_tree(value, path + (str(key), ))
            elif isinstance(err, list):
                for sub_err in err:
                    walk_error_tree(sub_err, path)
            else:
                error_list.append(f'{".".join(path)}: {err}')

        walk_error_tree(validator.errors, ())
        return error_list


@click.group()
@click.pass_context
def main(ctx):
    config = None
    if os.path.exists('config.yml'):
        with open('config.yml') as in_f:
            config = yaml.load(in_f, Loader=yaml.FullLoader)
    elif os.path.exists('/etc/senior-common-room/config.yml'):
        with open('/etc/senior-common-room/config.yml') as in_f:
            config = yaml.load(in_f, Loader=yaml.FullLoader)
    if not config:
        raise click.ClickException('No configuration found (./config.yml, /etc/senior-common-room/config.yml)')
    normalised = validate_config(config)
    if isinstance(normalised, list):
        error_str = '\n'.join(normalised)
        raise click.ClickException(f'Configuration errors:\n\n{error_str}')
    else:
        ctx.obj = {'config': normalised}
        if 'logging' in normalised:
            logging.config.dictConfig(normalised['logging'])


main.add_command(server)
main.add_command(database)
