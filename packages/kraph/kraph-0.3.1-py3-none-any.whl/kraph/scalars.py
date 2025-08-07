import io
from typing import IO, Any
from pydantic import BaseModel
from typing import Callable, Generator, Type
from typing import Any, IO, List, Optional, TypeAlias, cast
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema

from pydantic_core import core_schema

StructureIdentifierCoercible = str
""" A custom scalar for wrapping of every supported array like structure on"""
CypherCoercible = str
""" A custom scalar for wrapping of every supported array like structure on"""


class RemoteUpload(str):
    """A custom scalar for wrapping of every supported array like structure on
    the mikro platform. This scalar enables validation of various array formats
    into a mikro api compliant xr.DataArray.."""

    def __init__(self, value: IO[bytes]) -> None:
        self.value = value
        self.key = str(value.name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            v = open(v, "rb")

        if not isinstance(v, io.FileIO) and not isinstance(v, io.BufferedReader):
            raise ValueError("This needs to be a instance of a file")

        return cls(v)

    def __repr__(self):
        return f"RemoteUpload({self.value})"


class NodeID(str):
    def to_graph_id(self):
        return self.split(":")[1]

    def to_graph_name(self):
        return self.split(":")[0]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls: Type["NodeID"], v: Any, *info) -> "NodeID":
        """Validate the ID"""
        if isinstance(v, BaseModel):
            if hasattr(v, "id"):
                return cls(v.id)  # type: ignore
            else:
                raise TypeError("This needs to be a instance of BaseModel with an id")

        if isinstance(v, str):
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError("Needs to be either a instance of BaseModel (with an id) or a string")


class StructureIdentifier(str):
    def to_graph_id(self):
        return self.split(":")[1]

    def to_graph_name(self):
        return self.split(":")[0]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(
        cls: Type["StructureIdentifier"], v: StructureIdentifierCoercible
    ) -> "StructureIdentifier":
        """Validate the ID"""

        if isinstance(v, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            print(registry)

            identifier = registry.get_identifier_for_cls(v.__class__)
            return identifier

        if isinstance(v, str):
            assert "@" in v, "The string needs to be a valid identifier"
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError("Needs to be either a instance of BaseModel (with an id) or a string")


class StructureString(str):
    def to_graph_id(self):
        return self.split(":")[1]

    def to_graph_name(self):
        return self.split(":")[0]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls: Type["NodeID"], v: Any, *info) -> "NodeID":
        """Validate the ID"""
        if isinstance(v, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            identifier = registry.get_identifier_for_cls(v.__class__)
            assert hasattr(v, "id"), "The structure needs to have an id"

            return f"{identifier}:{v.id}"

        if isinstance(v, str):
            assert "@" in v, "The string needs to be a valid identifier"
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError("Needs to be either a instance of BaseModel (with an id) or a string")


class Cypher(str):
    def to_graph_id(self):
        return self.split(":")[1]

    def to_graph_name(self):
        return self.split(":")[0]

    def __set__(self, owner, value: CypherCoercible) -> None: ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls, v: CypherCoercible, *info) -> "Cypher":
        if isinstance(v, str):
            return cls(v)
        raise TypeError("Needs to be either str or a string")
