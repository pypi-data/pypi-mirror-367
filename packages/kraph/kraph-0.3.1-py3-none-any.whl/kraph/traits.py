"""
Kraph Traits Module

This module provides trait classes and utility functions for the Kraph knowledge graph system.
It defines the core behaviors and validation logic for various graph entities including:

- Entity traits: For representing graph nodes with semantic meaning
- Structure traits: For representing data structures and their relationships
- Measurement and metric traits: For quantitative data and observations
- Relation traits: For defining connections between entities
- Category traits: For organizing and classifying graph elements

The module also includes validation functions for category definitions and utility
classes for handling intermediate operations in the graph construction pipeline.

Key Components:
- Validation functions for category definitions
- Dataclasses for intermediate graph operations
- Trait classes that define graph entity behaviors
- Context managers for ontology and graph scoping
"""

from typing import Self, TypeVar, Optional, Union, Type
from collections.abc import Iterable
from koil import unkoil
from pydantic import BaseModel, field_validator
from typing import TYPE_CHECKING, Any, List, Optional, Union
from rath.scalars import ID
from kraph.vars import current_ontology, current_graph
import dataclasses
import datetime
from types import TracebackType
from rath.turms.utils import NotQueriedError, get_attributes_or_error


if TYPE_CHECKING:
    from kraph.api.schema import (
        Entity,
        MeasurementCategory,
        MetricCategory,
        RelationCategory,
        EntityCategory,
        StructureCategory,
        MetricKind,
        Structure,
        Metric,
    )
    from rekuest_next.structures.registry import StructureRegistry


def validate_reagent_category_definition(cls, value):
    """
    Validate and normalize reagent category definition input.

    This function validates reagent category definitions, which can be specified as:
    - Strings prefixed with "class:" for category filters
    - Strings prefixed with "tag:" for tag filters
    - ReagentCategoryTrait instances

    Args:
        cls: The class this validator is attached to (unused but required by Pydantic)
        value: The category definition to validate. Can be a single item or iterable.
               Valid formats:
               - "class:category_name" for category filtering
               - "tag:tag_name" for tag filtering
               - ReagentCategoryTrait instance

    Returns:
        CategoryDefinitionInput: Normalized category definition with separate
                               category and tag filters

    Raises:
        ValueError: If the input format is invalid, contains entity categories,
                   or has no filters specified

    Examples:
        >>> validate_reagent_category_definition(None, "class:antibody")
        >>> validate_reagent_category_definition(None, ["tag:primary", "class:antibody"])
    """
    from kraph.api.schema import CategoryDefinitionInput

    if isinstance(value, CategoryDefinitionInput):
        return value

    tagFilters = []
    categoryFilters = []

    if not isinstance(value, Iterable):
        value = [value]

    for i in value:
        if isinstance(i, str):
            if i.startswith("class:"):
                categoryFilters.append(i[len("class:") :])
            elif i.startswith("tag:"):
                tagFilters.append(i[len("tag:") :])
            else:
                raise ValueError(f"Unknown filter {i}")
        elif isinstance(i, EntityCategoryTrait):
            raise ValueError("Reagent role cannot have entity categories")
        elif isinstance(i, ReagentCategoryTrait):
            categoryFilters.append(i.id)
        else:
            raise ValueError(
                f'Unknown filter {i}. Either specify a string with ""tag:" or "class:" or a ReagentCategoryTrait'
            )

    if not categoryFilters and not tagFilters:
        raise ValueError("You must specify at least one class or tag filter")

    return CategoryDefinitionInput(
        categoryFilters=categoryFilters,
        tagFilters=tagFilters,
    )


CoercibleCategoryDefinitionInput = Union[
    str,
    "EntityCategoryTrait",
    "ReagentCategoryTrait",
]


def validate_entitiy_category_definition(
    cls, value: list[CoercibleCategoryDefinitionInput] | CoercibleCategoryDefinitionInput
) -> "CategoryDefinitionInput":
    """
    Validate and normalize entity category definition input.

    This function validates entity category definitions, which can be specified as:
    - Strings prefixed with "class:" for category filters
    - Strings prefixed with "tag:" for tag filters
    - EntityCategoryTrait instances

    Args:
        cls: The class this validator is attached to (unused but required by Pydantic)
        value: The category definition to validate. Can be a single item or iterable.
               Valid formats:
               - "class:category_name" for category filtering
               - "tag:tag_name" for tag filtering
               - EntityCategoryTrait instance

    Returns:
        CategoryDefinitionInput: Normalized category definition with separate
                               category and tag filters

    Raises:
        ValueError: If the input format is invalid, contains reagent categories,
                   or has no filters specified

    Examples:
        >>> validate_entitiy_category_definition(None, "class:protein")
        >>> validate_entitiy_category_definition(None, ["tag:enzyme", "class:protein"])
    """
    from kraph.api.schema import CategoryDefinitionInput

    if isinstance(value, CategoryDefinitionInput):
        return value

    tagFilters: list[str] = []
    categoryFilters: list[ID] = []

    if not isinstance(value, list) and not isinstance(value, tuple):
        value = [value]

    for i in value:
        if isinstance(i, str):
            if i.startswith("class:"):
                categoryFilters.append(i[len("class:") :])
            elif i.startswith("tag:"):
                tagFilters.append(i[len("tag:") :])
            else:
                raise ValueError(f"Unknown filter {i}")
        elif isinstance(i, EntityCategoryTrait):
            entity_id = get_attributes_or_error(i, "id")
            categoryFilters.append(entity_id)
        elif isinstance(i, ReagentCategoryTrait):
            raise ValueError("Enitity role cannot have reagent categories")
        else:
            raise ValueError(
                f'Unknown filter {i}. Either specify a string with ""tag:" or "class:" or a EntityCategoryTrait'
            )

    if not categoryFilters and not tagFilters:
        raise ValueError("You must specify at least one class or tag filter")

    return CategoryDefinitionInput(
        categoryFilters=tuple(categoryFilters),
        tagFilters=tuple(tagFilters),
    )


def validate_structure_category_definition(cls, value):
    """
    Validate and normalize structure category definition input.

    This function validates structure category definitions, which can be specified as:
    - Strings prefixed with "class:" for category filters
    - Strings prefixed with "tag:" for tag filters
    - Strings starting with "@" and containing "/" for direct category references
    - StructureCategoryTrait instances
    - BaseModel classes (which get converted to identifier filters)

    Args:
        cls: The class this validator is attached to (unused but required by Pydantic)
        value: The category definition to validate. Can be a single item or iterable.
               Valid formats:
               - "class:category_name" for category filtering
               - "tag:tag_name" for tag filtering
               - "@namespace/category" for direct category reference
               - StructureCategoryTrait instance
               - BaseModel class or instance

    Returns:
        StructureCategoryDefinitionInput: Normalized category definition with separate
                                        category, identifier, and tag filters

    Raises:
        ValueError: If the input format is invalid, contains incompatible category types,
                   or has no filters specified
        TypeError: If a class type check fails

    Examples:
        >>> validate_structure_category_definition(None, "class:image")
        >>> validate_structure_category_definition(None, ["tag:microscopy", MyModel])
    """
    from kraph.api.schema import (
        StructureCategoryDefinitionInput,
    )

    if isinstance(value, StructureCategoryDefinitionInput):
        return value

    tagFilters = []
    categoryFilters = []
    identifierFilters = []

    if not isinstance(value, list) and not isinstance(value, tuple):
        value = [value]

    for i in value:
        if isinstance(i, str):
            if i.startswith("@") and "/" in i:
                categoryFilters.append(i)
            if i.startswith("class:"):
                categoryFilters.append(i[len("class:") :])
            elif i.startswith("tag:"):
                tagFilters.append(i[len("tag:") :])
            else:
                raise ValueError(f"Unknown filter {i}")
        elif isinstance(i, StructureCategoryTrait):
            categoryFilters.append(i.id)
        elif isinstance(i, ReagentCategoryTrait):
            raise ValueError("Enitity role cannot have reagent categories")
        elif isinstance(i, EntityCategoryTrait):
            raise ValueError("Structure role cannot have entity categories")
        else:
            try:
                # check if it is a class
                if not isinstance(i, type):
                    i = i.__class__

                if issubclass(i, BaseModel):
                    from rekuest_next.structures.default import (
                        get_default_structure_registry,
                    )

                    registry = get_default_structure_registry()
                    identifier = registry.get_identifier_for_cls(i)
                    if identifier is None:
                        raise ValueError(f"Structure category {i} not registered")
                    identifierFilters.append(identifier)
                else:
                    raise ValueError(f"Unknown filter {i}")
            except TypeError as e:
                raise e

    if not categoryFilters and not tagFilters and not identifierFilters:
        raise ValueError("You must specify at least one class, identifier or tag filter")

    return StructureCategoryDefinitionInput(
        categoryFilters=categoryFilters,
        identifierFilters=identifierFilters,
        tagFilters=tagFilters,
    )


def assert_is_reagent_or_id(value):
    """
    Validate that a value is either a reagent ID string or a Reagent object.

    This utility function ensures that inputs to reagent-related operations
    are in the correct format - either a string ID or a Reagent object
    from which the ID can be extracted.

    Args:
        value: The value to validate. Should be either:
               - A string representing a reagent ID
               - A Reagent object with an 'id' attribute

    Returns:
        str: The reagent ID as a string

    Raises:
        ValueError: If the value is neither a string nor a Reagent object

    Examples:
        >>> assert_is_reagent_or_id("reagent_123")  # Returns "reagent_123"
        >>> assert_is_reagent_or_id(reagent_obj)    # Returns reagent_obj.id
    """
    from kraph.api.schema import Reagent

    if isinstance(value, str):
        return value
    elif getattr(value, "typename", None) == "Reagent":
        return getattr(value, "id")
    else:
        raise ValueError(
            f"Value {value} is not a string or a Reagent. You need to specify a single value for {value} (pass quantity as node mapping instead)"
        )


def assert_is_entity_or_id(value):
    """
    Validate that a value is either an entity ID string or an Entity object.

    This utility function ensures that inputs to entity-related operations
    are in the correct format - either a string ID or an Entity object
    from which the ID can be extracted.

    Args:
        value: The value to validate. Should be either:
               - A string representing an entity ID
               - An Entity object with an 'id' attribute

    Returns:
        str: The entity ID as a string

    Raises:
        ValueError: If the value is neither a string nor an Entity object

    Examples:
        >>> assert_is_entity_or_id("entity_456")  # Returns "entity_456"
        >>> assert_is_entity_or_id(entity_obj)    # Returns entity_obj.id
    """
    from kraph.api.schema import Entity

    if isinstance(value, str):
        return value
    elif getattr(value, "typename", None) == "Entity":
        return getattr(value, "id")
    else:
        raise ValueError(
            f"Value {value} is not a string or a Entity. You need to specify a single value for {value} (pass quantity as node mapping instead)"
        )


@dataclasses.dataclass
class MetricWithValue:
    """
    Represents a metric category paired with a specific value.

    This dataclass is used as an intermediate representation when creating
    metrics. It stores a metric category along with a concrete value,
    and can be combined with structures using the reverse-or operator (__ror__).

    Attributes:
        metric_category (MetricCategory): The category that defines the type of metric
        value (float): The numeric value for this metric instance

    Usage:
        This class is typically created by calling a MetricCategoryTrait with a value:
        >>> metric_with_value = my_metric_category(42.0)
        >>> structure | metric_with_value  # Creates a metric
    """

    metric_category: "MetricCategory"
    value: float

    def __ror__(self, other):
        """
        Create a metric by combining this metric-value pair with a structure.

        This method is called when using the | operator with a structure on the left
        and a MetricWithValue on the right (e.g., structure | metric_value).

        Args:
            other: The structure to associate this metric with. Can be:
                  - StructureTrait: A kraph structure object
                  - BaseModel: A Pydantic model that can be converted to a structure

        Returns:
            Metric: A new metric object linking the structure to this metric value

        Raises:
            NotImplementedError: If other is not a supported type
            AssertionError: If the structure and metric are not in the same graph

        Examples:
            >>> my_structure | MetricWithValue(category, 42.0)
            >>> my_model_instance | MetricWithValue(category, 3.14)
        """
        from rekuest_next.structures.default import get_default_structure_registry
        from kraph.api.schema import create_structure, create_metric

        if isinstance(other, BaseModel):
            registry = get_default_structure_registry()
            structure_string = registry.get_identifier_for_cls(type(other))
            id = get_attributes_or_error(other, "id")
            return create_metric(
                structure=create_structure(
                    f"{structure_string}:{id}", self.metric_category.graph.id
                ),
                category=self.metric_category,
                value=self.value,
            )

        if isinstance(other, StructureTrait):
            assert other.graph.id == self.metric_category.graph.id, (
                "Structure and metric must be in the same graph"
            )
            return create_metric(structure=other, category=self.metric_category, value=self.value)

        raise NotImplementedError("You can only merge a measurement with a structure")


@dataclasses.dataclass
class MeasurementWithStructureAndValidity:
    """
    Represents a measurement category with structure and temporal validity constraints.

    This dataclass combines a measurement category with a specific structure and
    optional temporal validity bounds. It supports the pipe operator to create
    measurements between the structure and entities.

    Attributes:
        measurement_category (MeasurementCategory): The category defining the measurement type
        structure (Structure): The structure being measured
        valid_from (Optional[datetime.datetime]): When this measurement becomes valid
        valid_to (Optional[datetime.datetime]): When this measurement expires

    Usage:
        This is typically created as an intermediate when using temporal measurements:
        >>> measurement_cat(valid_from=start_time) | structure | entity
    """

    measurement_category: "MeasurementCategory"
    structure: "Structure"
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None

    def __or__(self, other):
        """
        Create a measurement by combining this measurement-structure pair with an entity.

        Args:
            other: The target to measure. Can be:
                  - EntityTrait: A kraph entity object

        Returns:
            Measurement: A new measurement linking the structure to the entity

        Raises:
            NotImplementedError: If other is not an EntityTrait or BaseModel

        Examples:
            >>> measurement_with_structure | my_entity
        """
        from rekuest_next.structures.default import get_default_structure_registry
        from kraph.api.schema import create_structure, create_metric, create_measurement

        if isinstance(other, EntityTrait):
            id = get_attributes_or_error(other, "id")

            return create_measurement(
                self.measurement_category,
                self.structure.id,
                id,
                valid_from=self.valid_from,
                valid_to=self.valid_to,
            )

        if isinstance(other, BaseModel):
            raise NotImplementedError("You can only merge a measurement with a structure")

        raise NotImplementedError("You can only merge a measurement with a structure")


@dataclasses.dataclass
class IntermediateStructureRelationWithValidity:
    structure_relation_category: "StructureRelationCategoryTrait"
    structure: "Structure"
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None

    def __or__(self, other):
        from rekuest_next.structures.default import get_default_structure_registry
        from kraph.api.schema import (
            create_structure_relation,
            create_structure,
        )

        if isinstance(other, StructureTrait):
            id = get_attributes_or_error(other, "id")

            return create_structure_relation(
                self.structure_relation_category,
                self.structure.id,
                id,
                valid_from=self.valid_from,
                valid_to=self.valid_to,
            )

        if isinstance(other, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            structure_string = registry.get_identifier_for_cls(type(other))
            id = get_attributes_or_error(other, "id")

            right_structure = create_structure(
                f"{structure_string}:{id}", self.structure_relation_category.graph.id
            )

            return create_structure_relation(
                self.structure.id,
                right_structure.id,
                self.structure_relation_category,
            )

        raise NotImplementedError("You can only merge a measurement with a structure")


@dataclasses.dataclass
class MeasurementWithValidity:
    measurement_category: "MeasurementCategory"
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None

    def __ror__(self, other):
        from rekuest_next.structures.default import get_default_structure_registry
        from kraph.api.schema import create_structure, create_metric

        if isinstance(other, StructureTrait):
            return MeasurementWithStructureAndValidity(
                structure=other, valid_from=self.valid_from, valid_to=self.valid_to
            )

        if isinstance(other, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            structure_string = registry.get_identifier_for_cls(type(other))
            id = get_attributes_or_error(other, "id")

            return MeasurementWithStructureAndValidity(
                measurement_category=self.measurement_category,
                structure=create_structure(
                    f"{structure_string}:{id}", self.measurement_category.graph.id
                ),
                valid_from=self.valid_from,
                valid_to=self.valid_to,
            )

        raise NotImplementedError("You can only merge a measurement with a structure")


@dataclasses.dataclass
class IntermediateRelation:
    left: "Entity"
    category: "RelationCategoryTrait"

    def __or__(self, other):
        from kraph.api.schema import create_relation, EntityCategoryDefinition, Entity

        if isinstance(other, Entity):
            source: EntityCategoryDefinition = get_attributes_or_error(
                self.category, "source_definition"
            )
            target: EntityCategoryDefinition = get_attributes_or_error(
                self.category, "target_definition"
            )

            if source.category_filters:
                assert self.left.category.id in source.category_filters, (
                    f"Source {self.left.category} not in {source.category_filters}"
                )
            if source.tag_filters:
                assert self.left.category.id in source.tag_filters, (
                    f"Source {self.left.category.id} not in {source.tag_filters}"
                )

            if target.category_filters:
                assert other.category.id in target.category_filters, (
                    f"Target {other.category.id} not in {target.category_filters}"
                )

            if target.tag_filters:
                assert other.category.id in target.tag_filters, (
                    f"Target {other.category.id} not in {target.tag_filters}"
                )

            return create_relation(source=self.left, target=other, category=self.category)

        raise NotImplementedError("You can only merge a relation with an entity")


@dataclasses.dataclass
class RelationWithValidity:
    kind: "RelationCategoryTrait"
    value: float | None = None
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None


@dataclasses.dataclass
class StructureRelationWithValidity:
    kind: "StructureRelationCategoryTrait"
    value: float | None = None
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None

    def __ror__(self, other):
        from rekuest_next.structures.default import get_default_structure_registry
        from kraph.api.schema import create_structure, create_metric

        if isinstance(other, StructureTrait):
            return IntermediateStructureRelationWithValidity(
                structure_relation_category=self.kind,
                structure=other,
                valid_from=self.valid_from,
                valid_to=self.valid_to,
            )

        if isinstance(other, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            structure_string = registry.get_identifier_for_cls(type(other))
            id = get_attributes_or_error(other, "id")

            return IntermediateStructureRelationWithValidity(
                structure_relation_category=self.kind,
                structure=create_structure(
                    f"{structure_string}:{id}",
                    self.kind.graph.id,
                ),
                valid_from=self.valid_from,
                valid_to=self.valid_to,
            )

        raise NotImplementedError("You can only merge a measurement with a structure")


@dataclasses.dataclass
class IntermediateDescription:
    left: "StructureTrait"
    metric_with_value: "MetricWithValue"

    def __or__(self, other) -> "Metric":
        from kraph.api.schema import create_metric, create_structure

        if isinstance(other, StructureTrait):
            return create_metric(
                self.left,
                self.metric_with_value.metric_category,
                self.metric_with_value.value,
            )

        if isinstance(other, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            registry = get_default_structure_registry()
            structure_string = registry.get_identifier_for_cls(type(other))
            id = get_attributes_or_error(other, "id")

            structure = create_structure(
                f"{structure_string}:{id}",
                self.metric_with_value.metric_category.graph.id,
            )
            return create_metric(
                structure,
                self.metric_with_value.metric_category,
                self.metric_with_value.value,
            )

        raise NotImplementedError


@dataclasses.dataclass
class IntermediateRelationWithValidity:
    left: "EntityTrait"
    relation_with_validity: RelationWithValidity

    def __or__(self, other):
        from kraph.api.schema import create_relation

        if isinstance(other, EntityTrait):
            return create_relation(
                self.left,
                other,
                self.relation_with_validity.relation,
                valid_from=self.relation_with_validity.valid_from,
                valid_to=self.relation_with_validity.valid_to,
            )

        raise NotImplementedError


T = TypeVar("T", bound="BaseModel")


class StructureTrait(BaseModel):
    """
    Trait for structure entities in the knowledge graph.

    Structures represent data objects or computational artifacts that can be
    measured, related to each other, or linked to entities. This trait provides
    the core behavior for structure objects including combination operations
    and resolution to concrete Python objects.

    Key behaviors:
    - Cannot be directly merged with other structures or entities (use relations/measurements)
    - Can be resolved to concrete Python objects via the structure registry
    - Supports pipe operations with measurement categories and relations

    Examples:
        >>> structure | measurement_category(valid_from=now) | entity
        >>> structure.resolve()  # Gets the underlying Python object
    """

    def __or__(self, other: Any) -> Optional["StructureTrait"]:
        """
        Handle pipe operations with other graph elements.

        Args:
            other: The object to combine with this structure. Can be:
                  - None: Returns self unchanged
                  - MeasurementCategoryTrait: Raises helpful error about instantiation
                  - RelationCategoryTrait: Returns None (incomplete implementation)

        Returns:
            Self or None depending on the operation

        Raises:
            NotImplementedError: For invalid combinations or incomplete implementations
        """
        if other is None:
            return self

        if isinstance(other, StructureTrait):
            raise NotImplementedError(
                "Cannot merge structures directly, use a relation or measurement inbetween"
            )

        if isinstance(other, EntityTrait):
            raise NotImplementedError(
                "Cannot merge structure and entities directly, use a relation or measurement inbetween"
            )

        if isinstance(other, MeasurementCategoryTrait):
            raise NotImplementedError(
                "When merging a structure and a measurement, please instatiante the measurement with a value first"
            )

        if isinstance(other, RelationCategoryTrait):
            raise NotImplementedError(
                "When merging a structure and a relation, please instatiante the relation with a value first"
            )

        raise NotImplementedError(
            f"Cannot merge {type(self).__name__} with {type(other).__name__}. "
        )

    def resolve(self, registry: Optional["StructureRegistry"] = None) -> Any:
        """
        Resolve this structure to its underlying Python object.

        This method uses the structure registry to convert the graph structure
        back into a concrete Python object that can be used in computations.

        Args:
            registry (Optional[StructureRegistry]): The structure registry to use.
                                                   If None, uses the default registry.

        Returns:
            Any: The resolved Python object corresponding to this structure

        Raises:
            NotQueriedError: If required attributes are not available

        Examples:
            >>> structure = create_structure("MyModel:123", graph_id)
            >>> obj = structure.resolve()  # Gets the MyModel instance
        """
        identifier = get_attributes_or_error(self, "identifier")
        object = get_attributes_or_error(self, "object")

        from rekuest_next.structures.default import get_default_structure_registry

        registry = registry or get_default_structure_registry()

        fullfilled = registry.get_fullfilled_structure(identifier)

        return unkoil(fullfilled.aexpand, object)


class NodeTrait(BaseModel):
    """Trait for nodes in the knowledge graph."""

    pass


class NodeCategoryTrait(BaseModel):
    """Trait for categories of nodes in the knowledge graph."""

    pass


class MetricTrait(BaseModel):
    def __or__(self, other):
        raise NotImplementedError(
            "You cannot merge metrics directly, use a relation or measurement inbetween"
        )

        raise NotImplementedError


class RelationCategoryTrait(BaseModel):
    def __str__(self):
        return get_attributes_or_error(self, "age_name")

    def __or__(self, other):
        raise NotImplementedError

    def __call__(self, valid_from=None, valid_to=None):
        return RelationWithValidity(kind=self, valid_from=valid_from, valid_to=valid_to)


class StructureRelationCategoryTrait(BaseModel):
    def __str__(self):
        return get_attributes_or_error(self, "age_name")

    def __or__(self, other):
        raise NotImplementedError

    def __call__(self, valid_from=None, valid_to=None):
        return StructureRelationWithValidity(kind=self, valid_from=valid_from, valid_to=valid_to)


class MeasurementCategoryTrait(BaseModel):
    def __ror__(self, other):
        from kraph.api.schema import create_measurement

        if isinstance(other, StructureTrait):
            raise ValueError(
                f"You cannot merge a measurement category with a structure directly, you need to first give it a validity range by Calling the class YOUR_MEASUREMENT(valid_from=..., valid_to=...)"
            )

        if isinstance(other, BaseModel):
            from rekuest_next.structures.default import get_default_structure_registry

            raise ValueError(
                f"You cannot merge a measurement category with a structure directly, you need to first give it a validity range by Calling the class YOUR_MEASUREMENT(valid_from=..., valid_to=...)"
            )

        raise NotImplementedError(
            "Measurement categories cannot be merged directly, use a relation or measurement inbetween"
        )

    def __call__(self, valid_from=None, valid_to=None):
        from kraph.api.schema import MetricKind

        return MeasurementWithValidity(
            measurement_category=self, valid_from=valid_from, valid_to=valid_to
        )


class ReagentCategoryTrait(BaseModel):
    def __call__(self, *args, external_id=None, **kwargs):
        from kraph.api.schema import create_reagent

        """Creates an entity with a name


        """
        id = get_attributes_or_error(self, "id")
        return create_reagent(id, *args, external_id=external_id, **kwargs)


class StructureCategoryTrait(BaseModel):
    def __or__(self, other):
        raise NotImplementedError(
            "You cannot relate structure categories directly. Use a entitiy instead"
        )

    def create_structure(self, identifier) -> "Entity":
        from kraph.api.schema import create_structure

        """Creates an entity with a name


        """
        graph = current_graph.get()
        return create_structure(identifier, graph)

    def __call__(self, *args, **kwds):
        return self.create_structure(*args, **kwds)


class EntityCategoryTrait(BaseModel):
    """Allows for the creation of a generic categoryss"""

    def __or__(self, other):
        raise NotImplementedError(
            "You cannot relate structure categories directly. Use an entitiy instead E.g. by calling the category"
        )

    def __call__(self, *args, **kwargs):
        from kraph.api.schema import create_entity

        """Creates an entity with a name


        """
        id = get_attributes_or_error(self, "id")
        return create_entity(id, *args, **kwargs)


class NaturalEventCategoryTrait(BaseModel):
    """Allows for the creation of a generic category"""

    def __or__(self, other):
        raise NotImplementedError(
            "You cannot relate structure categories directly. Use an entitiy instead E.g. by calling the category"
        )

    def __call__(self, *args, external_id=None, **kwargs):
        from kraph.api.schema import record_natural_event

        """Creates an entity with a name


        """
        id = get_attributes_or_error(self, "id")
        return record_natural_event(id, *args, **kwargs)


class ProtocolEventCategoryTrait(BaseModel):
    """Allows for the creation of a generic category"""

    def __or__(self, other):
        raise NotImplementedError(
            "You cannot relate structure categories directly. Use an entitiy instead E.g. by calling the category"
        )

    def __call__(self, external_id=None, **kwargs):
        from kraph.api.schema import (
            record_protocol_event,
            EntityRoleDefinition,
            ReagentRoleDefinition,
            NodeMapping,
            VariableMappingInput,
            VariableDefinition,
            Reagent,
        )

        """Creates an entity with a name


        """
        reagent_source_roles: list[ReagentRoleDefinition] = get_attributes_or_error(
            self, "source_reagent_roles"
        )
        reagent_target_roles: list[ReagentRoleDefinition] = get_attributes_or_error(
            self, "target_reagent_roles"
        )

        entity_source_roles: list[EntityRoleDefinition] = get_attributes_or_error(
            self, "source_entity_roles"
        )
        entity_target_roles: list[EntityRoleDefinition] = get_attributes_or_error(
            self, "target_entity_roles"
        )

        variable_definitions: list[VariableDefinition] = get_attributes_or_error(
            self, "variable_definitions"
        )

        entity_sources: list[NodeMapping] = kwargs.get("entity_sources", [])
        entity_targets: list[NodeMapping] = kwargs.get("entity_targets", [])
        reagent_sources: list[NodeMapping] = kwargs.get("reagent_sources", [])
        reagent_targets: list[NodeMapping] = kwargs.get("reagent_targets", [])
        variable_mappings: list[VariableMappingInput] = kwargs.get("variable_mappings", [])

        validated_entity_sources = []
        validated_entity_targets = []
        validated_reagent_sources = []
        validated_reagent_targets = []
        validated_variable_mappings = []

        for i in reagent_source_roles:
            if i.role not in [x.key for x in reagent_sources]:
                if i.needs_quantity:
                    raise ValueError(
                        f"Reagent source role {i.role} requires a quantity. You need to specify a quanitnity in a node mapping for {i.role}"
                    )

                elif i.role in kwargs:
                    passed_value = kwargs.pop(i.role)
                    assert_is_reagent_or_id(passed_value)
                    validated_reagent_sources.append(NodeMapping(key=i.role, node=passed_value))

                else:
                    if i.optional:
                        continue
                    raise ValueError(
                        f"Reagent source role {i.role} not found in source or keyword arguments"
                    )

            else:
                passed_values = [x.key for x in reagent_sources]
                assert len(passed_values) == 1, (
                    f"Reagent source role {i.role} found multiple times in source. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                )
                assert isinstance(passed_values, NodeMapping), (
                    f"Reagent source role {i.role} is not a node mapping. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                )
                validated_reagent_sources.append(passed_values[0])

        for i in entity_source_roles:
            if i.role not in [x.key for x in entity_sources]:
                if i.role in kwargs:
                    passed_value = kwargs.pop(i.role)
                    if isinstance(passed_value, list) or isinstance(passed_value, tuple):
                        assert i.allow_multiple, (
                            f"Entity source role {i.role} does not allow multiple values. You need to specify a single value for {i.role}"
                        )

                        for passed_v in passed_value:
                            assert_is_entity_or_id(passed_v)
                            validated_entity_sources.append(NodeMapping(key=i.role, node=passed_v))
                    else:
                        assert_is_entity_or_id(passed_value)
                        validated_entity_sources.append(NodeMapping(key=i.role, node=passed_value))
                else:
                    if i.optional:
                        continue
                    else:
                        raise ValueError(
                            f"Reagent source role {i.role} not found in source or keyword arguments"
                        )

            else:
                passed_values = [x.key for x in reagent_sources]
                if len(passed_values) > 1 and not i.allow_multiple:
                    raise ValueError(
                        f"Reagent source role {i.role} found multiple times in source. You need to specify a single value for {i.role}"
                    )

                for i in passed_values:
                    assert isinstance(i, NodeMapping), (
                        f"Reagent source role {i.role} is not a node mapping. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                    )
                    validated_entity_sources.append(i)

        for i in reagent_target_roles:
            if i.role not in [x.key for x in reagent_targets]:
                if i.needs_quantity:
                    raise ValueError(
                        f"Reagent target role {i.role} requires a quantity. You need to specify a quanitnity in a node mapping for {i.role}"
                    )

                elif i.role in kwargs:
                    passed_value = kwargs.pop(i.role)
                    assert_is_reagent_or_id(passed_value)
                    validated_reagent_targets.append(NodeMapping(key=i.role, node=passed_value))

                else:
                    if i.optional:
                        continue
                    raise ValueError(
                        f"Reagent target role {i.role} not found in source or keyword arguments"
                    )

            else:
                passed_values = [x.key for x in reagent_targets]
                assert len(passed_values) == 1, (
                    f"Reagent target role {i.role} found multiple times in source. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                )
                assert isinstance(passed_values, NodeMapping), (
                    f"Reagent target role {i.role} is not a node mapping. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                )
                validated_reagent_targets.append(passed_values[0])

        for i in entity_target_roles:
            if i.role not in [x.key for x in entity_targets]:
                if i.role in kwargs:
                    passed_value = kwargs.pop(i.role)
                    if isinstance(passed_value, list) or isinstance(passed_value, tuple):
                        assert i.allow_multiple, (
                            f"Entity target role {i.role} does not allow multiple values. You need to specify a single value for {i.role}"
                        )

                        for passed_v in passed_value:
                            assert_is_entity_or_id(passed_v)
                            validated_entity_targets.append(NodeMapping(key=i.role, node=passed_v))
                    else:
                        assert_is_entity_or_id(passed_value)
                        validated_entity_targets.append(NodeMapping(key=i.role, node=passed_value))
                else:
                    if i.optional:
                        continue
                    else:
                        raise ValueError(
                            f"Reagent target role {i.role} not found in source or keyword arguments"
                        )

            else:
                passed_values = [x.key for x in entity_targets]
                if len(passed_values) > 1 and not i.allow_multiple:
                    raise ValueError(
                        f"Entity target role {i.role} found multiple times in source. You need to specify a single value for {i.role}"
                    )

                for i in passed_values:
                    assert isinstance(i, NodeMapping), (
                        f"Entity target role {i.role} is not a node mapping. You need to specify a single value for {i.role} (pass quantity as node mapping instead)"
                    )
                    validated_entity_targets.append(i)

        for i in variable_definitions:
            if i.param not in [x.key for x in variable_mappings]:
                if i.param in kwargs:
                    passed_value = kwargs.pop(i.param)
                    validated_variable_mappings.append(
                        VariableMappingInput(key=i.param, value=passed_value)
                    )
                else:
                    if i.optional:
                        continue
                    else:
                        raise ValueError(
                            f"Variable mapping {i.param} not found in source or keyword arguments"
                        )

            else:
                passed_values = [x.key for x in variable_mappings]
                assert len(passed_values) == 1, (
                    f"Variable mapping {i.param} found multiple times in source. You need to specify a single value for {i.param} (pass quantity as node mapping instead)"
                )
                assert isinstance(passed_values, VariableMappingInput), (
                    f"Variable mapping {i.param} is not a node mapping. You need to specify a single value for {i.param} (pass quantity as node mapping instead)"
                )
                validated_variable_mappings.append(passed_values[0])

        return record_protocol_event(
            category=self,
            external_id=external_id,
            entity_sources=validated_entity_sources,
            entity_targets=validated_entity_targets,
            reagent_sources=validated_reagent_sources,
            reagent_targets=validated_reagent_targets,
            **kwargs,
        )


class MetricCategoryTrait(BaseModel):
    """Allows for the creation of a generic category"""

    def __or__(self, other):
        raise NotImplementedError(
            "You cannot relate structure categories directly. Use an entitiy instead E.g. by calling the category"
        )

    def __call__(self, value, target=None):
        from kraph.api.schema import create_metric

        """Creates an entity with a name


        """
        try:
            kind = get_attributes_or_error(self, "category.metric_kind")
        except NotQueriedError:
            kind = None

        if kind:
            if kind == MetricKind.FLOAT:
                assert isinstance(value, float), "Value must be a float"
            elif kind == MetricKind.INT:
                assert isinstance(value, int), "Value must be an int"
            elif kind == MetricKind.STRING:
                assert isinstance(value, str), "Value must be a string"
            elif kind == MetricKind.BOOLEAN:
                assert isinstance(value, bool), "Value must be a bool"
            else:
                raise NotImplementedError(f"Kind {kind} not implemented")

        if target is not None:
            assert isinstance(target, StructureTrait), "Target must be an structure"
            assert target.graph.id == self.graph.id, "Target and metric must be in the same graph"
            return create_metric(
                target,
                category=self,
                value=value,
            )

        return MetricWithValue(
            metric_category=self,
            value=value,
        )


class ExpressionTrait(BaseModel):
    def __or__(self, other):
        raise NotImplementedError

    def __str__(self):
        return getattr(self, "label", super().__str__())


class EntityTrait(BaseModel):
    """
    Trait for entity objects in the knowledge graph.

    Entities represent real-world objects, concepts, or phenomena that can be
    related to each other and measured by structures. This trait provides
    the core behavior for entity objects including relationship creation,
    metric assignment, and protocol operations.

    Key behaviors:
    - Can be combined with relation categories to create relations
    - Can be combined with relation validity objects for temporal relations
    - Cannot be directly merged with other entities or structures
    - Supports metric assignment via the set() method
    - Can be subject to protocol steps

    Examples:
        >>> entity1 | relation_category | entity2
        >>> entity | relation_category(valid_from=now) | other_entity
        >>> entity.set(metric_expression, 42.0)
        >>> entity.subject_to(protocol=my_protocol)
    """

    def __or__(self, other):
        """
        Handle pipe operations with other graph elements.

        Args:
            other: The object to combine with this entity. Can be:
                  - RelationWithValidity: Creates intermediate relation with validity
                  - RelationCategoryTrait: Creates intermediate relation
                  - MeasurementCategoryTrait: Raises helpful error about instantiation

        Returns:
            IntermediateRelationWithValidity or IntermediateRelation depending on input

        Raises:
            NotImplementedError: For invalid combinations
        """
        if isinstance(other, RelationWithValidity):
            return IntermediateRelationWithValidity(left=self, relation_with_validity=other)
        if isinstance(other, EntityTrait):
            raise NotImplementedError(
                "Cannot merge entities directly, use a relation or measurement inbetween"
            )
        if isinstance(other, StructureTrait):
            raise NotImplementedError(
                "Cannot merge entities and structures directly, use a relation or measurement inbetween"
            )
        if isinstance(other, RelationCategoryTrait):
            return IntermediateRelation(left=self, category=other)
        if isinstance(other, MeasurementCategoryTrait):
            raise NotImplementedError(
                "When merging a entity and a measurement, please instatiante the measurement with a value first"
            )


class GraphTrait(BaseModel):
    """
    Trait for graph context management and graph operations.

    This trait provides context manager functionality for setting the current
    graph scope, as well as convenience methods for creating various graph
    entities like categories and relations within this graph context.

    Attributes:
        _token: Internal token used for context management

    Key Features:
    - Context management for graph scope
    - Factory methods for creating graph entities
    - Automatic graph association for created entities

    Usage:
        >>> with my_graph:
        ...     # All operations use my_graph as context
        ...     protein_cat = my_graph.create_entity_category("protein")
        ...     temp_metric = my_graph.create_metric_category("temperature")
    """

    _token = None

    def __enter__(self) -> Self:
        """
        Enter the graph context.

        Sets this graph as the current global graph context.

        Returns:
            self: This graph instance for use in the with statement
        """
        self._token = current_graph.set(self)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        """
        Exit the graph context.

        Restores the previous graph context that was active before
        entering this context.

        Args:
            exc_type: Exception type (if any exception occurred)
            exc_value: Exception value (if any exception occurred)
            traceback: Exception traceback (if any exception occurred)
        """
        current_graph.reset(self._token)
        current_graph.reset(self._token)

    def create_entity_category(
        self,
        label: str,
        description: str = None,
        **kwargs,
    ) -> "EntityCategory":
        """
        Create a new entity category within this graph.

        Entity categories define types of real-world objects or concepts
        that can be represented as entities in the knowledge graph.

        Args:
            label (str): A human-readable name for the category
            description (str, optional): A detailed description of the category
            **kwargs: Additional arguments passed to the creation function

        Returns:
            EntityCategory: The newly created entity category

        Examples:
            >>> protein_cat = graph.create_entity_category("Protein", "Biological proteins")
            >>> cell_cat = graph.create_entity_category("Cell Line")
        """
        from kraph.api.schema import create_entity_category

        return create_entity_category(graph=self, label=label, description=description, **kwargs)

    def create_structure_category(
        self,
        identifier: str,
        description: str = None,
        **kwargs,
    ) -> "StructureCategory":
        """
        Create a new structure category within this graph.

        Structure categories define types of data structures or computational
        artifacts that can be stored and manipulated in the knowledge graph.

        Args:
            identifier (str): A unique identifier for the structure type
            description (str, optional): A detailed description of the category
            **kwargs: Additional arguments passed to the creation function

        Returns:
            StructureCategory: The newly created structure category

        Examples:
            >>> image_cat = graph.create_structure_category("@arkitekt/image")
            >>> table_cat = graph.create_structure_category("@arkitekt/table", "Data tables")
        """
        from kraph.api.schema import create_structure_category

        return create_structure_category(
            graph=self, identifier=identifier, description=description, **kwargs
        )

    def create_measurement_category(
        self,
        label: str,
        description: str = None,
        **kwargs,
    ) -> "MeasurementCategory":
        """
        Create a new measurement category within this graph.

        Measurement categories define types of observations or measurements
        that can be made on structures and associated with entities.

        Args:
            label (str): A human-readable name for the measurement type
            description (str, optional): A detailed description of the category
            **kwargs: Additional arguments passed to the creation function

        Returns:
            MeasurementCategory: The newly created measurement category

        Examples:
            >>> length_cat = graph.create_measurement_category("Length", "Linear measurements")
            >>> intensity_cat = graph.create_measurement_category("Fluorescence Intensity")
        """
        from kraph.api.schema import create_measurement_category

        return create_measurement_category(
            graph=self, label=label, description=description, **kwargs
        )

    def create_relation_category(
        self,
        label: str,
        description: str = None,
        **kwargs,
    ) -> "RelationCategory":
        """
        Create a new relation category within this graph.

        Relation categories define types of relationships that can exist
        between entities in the knowledge graph.

        Args:
            label (str): A human-readable name for the relation type
            description (str, optional): A detailed description of the category
            **kwargs: Additional arguments passed to the creation function
                     May include source_definition and target_definition

        Returns:
            RelationCategory: The newly created relation category

        Examples:
            >>> binds_to = graph.create_relation_category("binds to", "Binding relationship")
            >>> part_of = graph.create_relation_category("part of", source_definition=...)
        """
        from kraph.api.schema import create_relation_category, CategoryDefinitionInput

        return create_relation_category(
            graph=self,
            label=label,
            description=description,
            **kwargs,
        )

    def create_metric_category(
        self,
        label: str,
        kind: "MetricKind" = None,
        description: str = None,
        **kwargs,
    ) -> "MetricCategory":
        """
        Create a new metric category within this graph.

        Metric categories define types of quantitative measurements
        that can be associated with structures in the knowledge graph.

        Args:
            label (str): A human-readable name for the metric type
            kind (MetricKind, optional): The data type for metric values
                                       (FLOAT, INT, STRING, BOOLEAN)
            description (str, optional): A detailed description of the category
            **kwargs: Additional arguments passed to the creation function

        Returns:
            MetricCategory: The newly created metric category

        Examples:
            >>> temp_metric = graph.create_metric_category("Temperature", MetricKind.FLOAT)
            >>> count_metric = graph.create_metric_category("Cell Count", MetricKind.INT)
        """
        from kraph.api.schema import create_metric_category

        return create_metric_category(
            graph=self, label=label, description=description, kind=kind, **kwargs
        )


class HasPresignedDownloadAccessor(BaseModel):
    """
    Trait for objects that support file downloads via presigned URLs.

    This trait adds download functionality to objects that have presigned URLs,
    allowing them to download associated files to the local filesystem.

    Attributes:
        _dataset (Any): Internal dataset storage (unused)

    Usage:
        Objects with this trait can call download() to retrieve associated files.
        The presigned_url and key attributes must be available on the object.

    Examples:
        >>> file_obj.download()  # Downloads to default filename
        >>> file_obj.download("custom_name.txt")  # Downloads with custom name
    """

    _dataset: Any = None

    def download(self, file_name: str = None) -> "str":
        """
        Download the file associated with this object.

        Uses the object's presigned URL to download the file to the local
        filesystem. If no filename is provided, uses the object's key as
        the filename.

        Args:
            file_name (str, optional): The local filename to save as.
                                     If None, uses the object's key attribute.

        Returns:
            str: The path to the downloaded file

        Raises:
            NotQueriedError: If presigned_url or key attributes are not available

        Examples:
            >>> path = my_file.download()
            >>> path = my_file.download("my_data.csv")
        """
        from kraph.io import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class EntityRoleDefinitionInputTrait(BaseModel):
    """
    Trait for validating entity role definitions in protocol contexts.

    This trait provides automatic validation for entity role definition inputs,
    ensuring that category definitions are properly formatted for entity roles
    in protocols and experimental procedures.

    The validation converts various input formats to standardized
    CategoryDefinitionInput objects with proper entity category filters.
    """

    @field_validator("category_definition", mode="before", check_fields=False)
    def validate_category_definition(cls, value):
        """Validate and normalize entity category definition."""
        return validate_entitiy_category_definition(cls, value)


class ReagentRoleDefinitionInputTrait(BaseModel):
    """
    Trait for validating reagent role definitions in protocol contexts.

    This trait provides automatic validation for reagent role definition inputs,
    ensuring that category definitions are properly formatted for reagent roles
    in protocols and experimental procedures.

    The validation converts various input formats to standardized
    CategoryDefinitionInput objects with proper reagent category filters.
    """

    @field_validator("category_definition", mode="before", check_fields=False)
    def validate_category_definition(cls, value):
        """Validate and normalize reagent category definition."""
        return validate_reagent_category_definition(cls, value)


class RelationCategoryInputTrait(BaseModel):
    """
    Trait for validating relation category inputs.

    This trait provides automatic validation for relation category creation,
    ensuring that source and target definitions are properly formatted
    as entity category definitions.

    Both source and target definitions are validated to ensure they
    contain valid entity category filters and tag filters.
    """

    @field_validator("source_definition", mode="before", check_fields=False)
    def validate_source_definition(cls, value):
        """Validate and normalize source entity category definition."""
        return validate_entitiy_category_definition(cls, value)

    @field_validator("target_definition", mode="before", check_fields=False)
    def validate_target_definition(cls, value):
        """Validate and normalize target entity category definition."""
        return validate_entitiy_category_definition(cls, value)


class StructureRelationCategoryInputTrait(BaseModel):
    """
    Trait for validating structure relation category inputs.

    This trait provides automatic validation for structure relation category creation,
    ensuring that source and target definitions are properly formatted
    as structure category definitions.

    Both source and target definitions are validated to ensure they
    contain valid structure category, identifier, and tag filters.
    """

    @field_validator("source_definition", mode="before", check_fields=False)
    def validate_source_definition(cls, value):
        """Validate and normalize source structure category definition."""
        return validate_structure_category_definition(cls, value)

    @field_validator("target_definition", mode="before", check_fields=False)
    def validate_target_definition(cls, value):
        """Validate and normalize target structure category definition."""
        return validate_structure_category_definition(cls, value)


class MeasurementCategoryInputTrait(BaseModel):
    """
    Trait for validating measurement category inputs.

    This trait provides automatic validation for measurement category creation,
    ensuring that structure and entity definitions are properly formatted.

    The structure definition is validated as a structure category definition,
    while the entity definition is validated as an entity category definition.
    """

    @field_validator("structure_definition", mode="before", check_fields=False)
    def validate_source_definition(cls, value):
        """Validate and normalize structure category definition."""
        return validate_structure_category_definition(cls, value)

    @field_validator("entity_definition", mode="before", check_fields=False)
    def validate_target_definition(cls, value):
        """Validate and normalize entity category definition."""
        return validate_entitiy_category_definition(cls, value)


class MetricCategoryInputTrait(BaseModel):
    """
    Trait for validating metric category inputs.

    This trait provides automatic validation for metric category creation,
    ensuring that structure definitions are properly formatted as
    structure category definitions.

    The structure definition defines which types of structures
    this metric can be applied to.
    """

    @field_validator("structure_definition", mode="before", check_fields=False)
    def validate_source_definition(cls, value):
        """Validate and normalize structure category definition."""
        return validate_structure_category_definition(cls, value)
