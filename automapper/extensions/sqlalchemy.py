from typing import Iterable, Type

from sqlalchemy.orm import declarative_base

from automapper import Mapper

Base = declarative_base()


def spec_function(target_cls: Type[Base]) -> Iterable[str]:
    table = target_cls.metadata.tables.get(target_cls.__tablename__)
    return tuple(column.name for column in table.columns)


def extend(mapper: Mapper) -> None:
    mapper.add_spec(Base, spec_function)
