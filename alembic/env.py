from logging.config import fileConfig

from alembic import context

from app.core.config import settings
from app.core.database import Base, criar_engine
import app.domain.models  # noqa: F401  (registra as tabelas no metadata)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    # Permite sobrescrever pela linha de comando: alembic -x url=sqlite:///outro.db upgrade head
    return context.get_x_argument(as_dictionary=True).get("url", settings.database_url)


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True,
                      render_as_batch=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = criar_engine(_url())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=True, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
