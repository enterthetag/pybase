from sqlalchemy import types
from sqlalchemy.orm import (
    declarative_base,
    declarative_mixin,
    declared_attr,
    mapped_column,
)
from sqlalchemy.schema import MetaData
from sqlalchemy.sql import functions


class _Base:
    # pylint: disable=no-member,no-self-argument

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(
    cls=_Base,
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    ),
)


@declarative_mixin
class Timestamped:
    created = mapped_column(types.DateTime, default=functions.now())
    modified = mapped_column(types.DateTime, onupdate=functions.now())
