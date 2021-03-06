import os
from alembic import context

import sys

from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from rcdb.model import Condition, ConditionType, Run, ConfigurationFile, LogRecord

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Condition.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.



def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    alembic_config = config.get_section(config.config_ini_section)
    x_args = context.get_x_argument(as_dictionary=True)
    if "rcdb_connection" in x_args:
        connection_string = x_args["rcdb_connection"]
    elif "RCDB_CONNECTION" in os.environ:
        connection_string = os.environ["RCDB_CONNECTION"]
        if connection_string.startswith("mysql://"):
            try:
                # noinspection PyUnresolvedReferences
                import MySQLdb
            except ImportError as err:
                # sql alchemy uses MySQLdb by default. But it might be not install in the system
                # in such case we fallback to mysqlconnector which is embedded in CCDB
                connection_string = connection_string.replace("mysql://", "mysql+mysqlconnector://")
    else:
        raise Exception("Connection string is not found. "
                        "Set is using '-x rcdb_connection=value' flag "
                        "or by setting RCDB_CONNECTION environment variable")

    alembic_config["sqlalchemy.url"] = connection_string

    print alembic_config

    engine = engine_from_config(
                alembic_config,
                prefix='sqlalchemy.',
                poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
                connection=connection,
                target_metadata=target_metadata
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

