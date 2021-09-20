"""Senior Common Room Command-line interface."""

import click
import dateparser
import datetime
import logging.config
import os
import yaml

from cerberus import Validator
from pytz import timezone
from typing import Union, List

from .server import server
from .database import database


def parse_datetime(value: str) -> datetime.datetime:
    """Parse a datetime string into a timezone-aware DateTime.

    :param value: The datetime string to parse.
    :type value: str
    :return: The parsed, timezone-aware DateTime
    :rtype: datetime.Datetime
    """
    utc = timezone('UTC')
    return dateparser.parse(value, settings={
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': True
    }).astimezone(utc)


CONFIG_SCHEMA = {
    'core': {
        'type': 'dict',
        'schema': {
            'title': {
                'type': 'string',
                'required': False,
                'empty': False,
                'nullable': True,
                'default': 'The Senior Common Room'
            }
        },
        'default': {
            'title': 'The Senior Common Room'
        }
    },
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
    'badges': {
        'type': 'list',
        'required': False,
        'default': [],
        'schema': {
            'type': 'dict',
            'schema': {
                'title': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'url': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'role': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'self_assigned': {
                    'type': 'boolean',
                    'required': False,
                    'default': False,
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
            },
            'main': {
                'type': 'boolean',
                'default': True
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
    'schedule': {
        'type': 'list',
        'default': [],
        'schema': {
            'type': 'dict',
            'schema': {
                'title': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'start': {
                    'type': 'datetime',
                    'required': True,
                    'empty': False,
                    'coerce': parse_datetime
                },
                'end': {
                    'type': 'datetime',
                    'required': True,
                    'empty': False,
                    'coerce': parse_datetime
                },
                'room': {
                    'type': 'string',
                    'required': False,
                    'nullable': True,
                    'default': None
                },
                'description': {
                    'type': 'string',
                    'required': False,
                    'nullable': True,
                    'default': None
                }
            }
        }
    },
    'links': {
        'type': 'list',
        'default': [],
        'schema': {
            'type': 'dict',
            'schema': {
                'title': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'url': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                }
            }
        }
    },
    'logging': {
        'type': 'dict'
    }
}


def validate_config(config: dict) -> Union[list, dict]:
    """Validate the given configuration dictionary.

    Also applies all configuration normalisations.

    Returns either the normalised and validated configuration or a list of configuration errors.

    :param config: The configuration to validate.
    :type config: dict
    :return: Either a dictionary or a list of configuration errors.
    :rtype: Union[list, dict]
    """
    validator = Validator(CONFIG_SCHEMA)
    if validator.validate(config):
        return validator.normalized(config)
    else:
        error_list = []

        def walk_error_tree(err: Union[dict, list, str], path: str) -> List[str]:
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
def main(ctx: click.Context) -> None:
    """Senior-Common-Room commandline tool."""
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
