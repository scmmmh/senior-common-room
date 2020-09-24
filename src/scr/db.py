import asyncpg


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
)


async def setup_db():
    """Create / Upgrade the database schema."""
    current_versions = {'scr_users': 0}
    conn = await asyncpg.connect('postgresql://dev:devPWD@localhost/senior-common-room')
    await conn.execute('CREATE TABLE IF NOT EXISTS scr_versions (name VARCHAR(255) PRIMARY KEY, version INTEGER)')
    for result in await conn.fetch('''SELECT * FROM scr_versions'''):
        current_versions[result['name']] = result['version']
    for table_name, versions in SCHEMAS:
        for version, statement in versions:
            if version > current_versions[table_name]:
                async with conn.transaction():
                    await conn.execute(statement)
                    await conn.execute('''INSERT INTO scr_versions VALUES($1, $2)
                                          ON CONFLICT(name)
                                          DO UPDATE SET version = EXCLUDED.version''', table_name, version)
    await conn.close()
