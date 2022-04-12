from sqlalchemy import Column, func, types
from sqlalchemy.orm import declarative_base, declarative_mixin, declared_attr
from sqlalchemy.schema import MetaData


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
    created = Column(types.DateTime, default=func.now())
    modified = Column(types.DateTime, onupdate=func.now())
