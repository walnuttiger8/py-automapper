from typing import Protocol, Type, TypeVar, Iterable, cast
from unittest import TestCase

import pytest

from automapper import mapper as global_mapper, Mapper, MappingError, DuplicatedRegistrationError


# Test data
T = TypeVar("T")


class ParentClass:
    def __init__(self, num: int, text: str) -> None:
        self.num = num
        self.text = text


class ChildClass(ParentClass):
    def __init__(self, num: int, text: str, flag: bool) -> None:
        super().__init__(num, text)
        self.flag = flag

    @classmethod
    def fields(cls) -> Iterable[str]:
        return (field for field in cls.__init__.__annotations__.keys() if field != "return")


class AnotherClass:
    def __init__(self, text: str, num: int) -> None:
        self.text = text
        self.num = num

    @classmethod
    def fields(cls) -> Iterable[str]:
        return ["text", "num"]


class ClassWithFieldsMethodProtocol(Protocol):
    def fields(self) -> Iterable[str]:
        ...


class ComplexClass:
    def __init__(self, obj: ParentClass, text: str) -> None:
        self.obj = obj
        self.text = text


class AnotherComplexClass:
    def __init__(self, text: str, obj: ChildClass) -> None:
        self.text = text
        self.obj = obj


def custom_spec_func(concrete_class: Type[T]) -> Iterable[str]:
    fields = []
    for val_name in concrete_class.__init__.__annotations__:
        if val_name != "return":
            fields.append(val_name)
    return fields


def classifier_func(target_cls: Type[T]) -> bool:
    return callable(getattr(target_cls, "fields", None))


def spec_func(target_cls: Type[T]) -> Iterable[str]:
    return cast(ClassWithFieldsMethodProtocol, target_cls).fields()


# Test class
class AutomapperTest(TestCase):
    def setUp(self):
        self.mapper = Mapper()

    def test_add_spec__adds_to_internal_collection(self):
        self.mapper.add_spec(ParentClass, custom_spec_func)
        assert ParentClass in self.mapper._class_specs
        assert ["num", "text", "flag"] == self.mapper._class_specs[ParentClass](ChildClass)

    def test_add_spec__error_on_adding_same_class_spec(self):
        self.mapper.add_spec(ParentClass, custom_spec_func)
        with pytest.raises(DuplicatedRegistrationError):
            self.mapper.add_spec(ParentClass, lambda concrete_type: ["field1", "field2"])

    def test_add_spec__adds_to_internal_collection_for_classifier(self):
        self.mapper.add_spec(classifier_func, spec_func)
        assert classifier_func in self.mapper._classifier_specs
        assert ["text", "num"] == self.mapper._classifier_specs[classifier_func](AnotherClass)

    def test_add_spec__error_on_duplicated_registration(self):
        self.mapper.add_spec(classifier_func, spec_func)
        with pytest.raises(DuplicatedRegistrationError):
            self.mapper.add_spec(classifier_func, lambda concrete_type: ["field1", "field2"])

    def test_add__appends_class_to_class_mapping(self):
        with pytest.raises(MappingError):
            self.mapper.map(ChildClass)

        self.mapper.add_spec(AnotherClass, custom_spec_func)
        self.mapper.add(ChildClass, AnotherClass)
        result = self.mapper.map(ChildClass(10, "test_message", True))

        assert isinstance(result, AnotherClass)
        assert result.text == "test_message"
        assert result.num == 10

    def test_add__error_on_adding_same_source_class(self):
        class TempAnotherClass:
            pass

        self.mapper.add(ChildClass, AnotherClass)
        with pytest.raises(DuplicatedRegistrationError):
            self.mapper.add(ChildClass, TempAnotherClass)

    def test_to__global_mapper_works_with_provided_init_extension(self):
        source_obj = ChildClass(10, "test_text", False)

        result = global_mapper.to(AnotherClass).map(source_obj)

        assert isinstance(result, AnotherClass)
        assert result.text == "test_text"

    def test_map__skip_none_values_from_source_object(self):
        # TODO: implement
        pass

    def test_map__pass_none_values_from_source_object(self):
        # TODO: implement
        pass
