import asyncpg
import logging

from secrets import token_hex

logger = logging.getLogger('scr.db')

SCHEMAS = (
    ('scr_users', (
        (1, '''CREATE TABLE scr_users (id SERIAL PRIMARY KEY,
                                       email VARCHAR(255) UNIQUE NOT NULL,
                                       salt VARCHAR(255),
                                       password VARCHAR(255),
                                       name VARCHAR(255) NOT NULL,
                                       access_token VARCHAR(255) UNIQUE NULL,
                                       access_token_timestamp TIMESTAMP,
                                       created_at TIMESTAMP NOT NULL,
                                       updated_at TIMESTAMP)'''),
    )),
    ('scr_rooms', (
        (1, '''CREATE TABLE scr_rooms (id SERIAL PRIMARY KEY,
                                       external_id VARCHAR(255),
                                       label VARCHAR(255),
                                       type VARCHAR(16))'''),
        (2, f'''INSERT INTO scr_rooms(external_id, label, type)
                VALUES('{token_hex(32)}', 'Lobby', 'permanent')'''),
    )),
    ('scr_users_rooms', (
        (1, '''CREATE TABLE scr_users_rooms (user_id INT,
                                             room_id INT,
                                             PRIMARY KEY (room_id, user_id),
                                             CONSTRAINT fk_scr_users_rooms_user_id FOREIGN KEY (user_id) REFERENCES scr_users(id),
                                             CONSTRAINT fk_scr_users_rooms_room_id FOREIGN KEY (room_id) REFERENCES scr_rooms(id))'''),  # noqa: E501
    )),
)


async def create_update_db(config):
    """Create / Update the database schema."""
    logger.info('Starting the database create / update')
    async with asyncpg.create_pool(dsn=config.get('database', 'dsn')) as pool:
        async with pool.acquire() as conn:
            current_versions = {'scr_users': 0}
            await conn.execute('CREATE TABLE IF NOT EXISTS scr_versions (name VARCHAR(255) PRIMARY KEY, ' +
                               'version INTEGER)')
            for result in await conn.fetch('''SELECT * FROM scr_versions'''):
                current_versions[result['name']] = result['version']
            for table_name, versions in SCHEMAS:
                for version, statement in versions:
                    if table_name not in current_versions or version > current_versions[table_name]:
                        async with conn.transaction():
                            logger.debug(f'Creating / Updating {table_name} to version {version}')
                            await conn.execute(statement)
                            await conn.execute('''INSERT INTO scr_versions VALUES($1, $2)
                                                  ON CONFLICT(name)
                                                  DO UPDATE SET version = EXCLUDED.version''', table_name, version)
                            current_versions[table_name] = version
                            logger.debug(f'{table_name} at version {version}')
    logger.info('Database creation / update complete')


async def verify_db(pool):
    """Verify that the database is up-to-date."""
    logger.debug('Verifying that the database is up-to-date')
    async with pool.acquire() as conn:
        current_versions = {'scr_users': 0}
        try:
            for result in await conn.fetch('''SELECT * FROM scr_versions'''):
                current_versions[result['name']] = result['version']
            for table_name, versions in SCHEMAS:
                if table_name not in current_versions:
                    logger.debug(f'Table {table_name} needs to be created')
                    return False
                elif versions[-1][0] != current_versions[table_name]:
                    logger.debug(f'Table {table_name} needs to be upgraded from version ' +
                                 '{current_versions[table_name]} to {versions[-1][0]}')
                    return False
        except asyncpg.exceptions.UndefinedTableError:
            logger.debug(f'Database needs to be initialised')
            return False
    return True
