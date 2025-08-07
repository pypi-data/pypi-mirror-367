from kraph.traits import (
    MeasurementCategoryTrait,
    ProtocolEventCategoryTrait,
    ReagentRoleDefinitionInputTrait,
    RelationCategoryTrait,
    RelationCategoryInputTrait,
    NodeCategoryTrait,
    HasPresignedDownloadAccessor,
    StructureRelationCategoryInputTrait,
    EntityRoleDefinitionInputTrait,
    NodeTrait,
    StructureTrait,
    MetricTrait,
    MetricCategoryTrait,
    NaturalEventCategoryTrait,
    EntityCategoryTrait,
    ReagentCategoryTrait,
    StructureRelationCategoryTrait,
    GraphTrait,
    StructureCategoryTrait,
    MeasurementCategoryInputTrait,
    EntityTrait,
    MetricCategoryInputTrait,
)
from kraph.rath import KraphRath
from pydantic import ConfigDict, Field, BaseModel
from kraph.scalars import (
    RemoteUpload,
    Cypher,
    NodeID,
    StructureIdentifierCoercible,
    StructureString,
    StructureIdentifier,
    CypherCoercible,
)
from typing import Iterable, Literal, Annotated, List, Optional, Tuple, Union, Any
from kraph.funcs import execute, aexecute
from enum import Enum
from datetime import datetime
from rath.scalars import IDCoercible, ID


class ViewKind(str, Enum):
    """No documentation"""

    PATH = "PATH"
    PAIRS = "PAIRS"
    TABLE = "TABLE"
    INT_METRIC = "INT_METRIC"
    FLOAT_METRIC = "FLOAT_METRIC"
    NODE_LIST = "NODE_LIST"
    EDGE_LIST = "EDGE_LIST"


class ColumnKind(str, Enum):
    """No documentation"""

    NODE = "NODE"
    VALUE = "VALUE"
    EDGE = "EDGE"


class MetricKind(str, Enum):
    """No documentation"""

    INT = "INT"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"
    STRING = "STRING"
    CATEGORY = "CATEGORY"
    BOOLEAN = "BOOLEAN"
    THREE_D_VECTOR = "THREE_D_VECTOR"
    TWO_D_VECTOR = "TWO_D_VECTOR"
    ONE_D_VECTOR = "ONE_D_VECTOR"
    FOUR_D_VECTOR = "FOUR_D_VECTOR"
    N_VECTOR = "N_VECTOR"


class InstanceKind(str, Enum):
    """No documentation"""

    LOT = "LOT"
    SAMPLE = "SAMPLE"
    ENTITY = "ENTITY"
    UNKNOWN = "UNKNOWN"


class NodeQueryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of IDs"
    search: Optional[str] = None
    "Search by text"
    id: Optional[ID] = None
    and_: Optional["NodeQueryFilter"] = Field(alias="AND", default=None)
    or_: Optional["NodeQueryFilter"] = Field(alias="OR", default=None)
    not_: Optional["NodeQueryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OffsetPaginationInput(BaseModel):
    """No documentation"""

    offset: int
    limit: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphQueryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of IDs"
    search: Optional[str] = None
    "Search by text"
    id: Optional[ID] = None
    and_: Optional["GraphQueryFilter"] = Field(alias="AND", default=None)
    or_: Optional["GraphQueryFilter"] = Field(alias="OR", default=None)
    not_: Optional["GraphQueryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    ontology: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["StructureCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["StructureCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["StructureCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ProtocolEventCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["ProtocolEventCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["ProtocolEventCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["ProtocolEventCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NaturalEventCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["NaturalEventCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["NaturalEventCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["NaturalEventCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EntityCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    ontology: Optional[ID] = None
    pinned: Optional[bool] = None
    tags: Optional[Tuple[str, ...]] = None
    and_: Optional["EntityCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["EntityCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["EntityCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReagentCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    ontology: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["ReagentCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["ReagentCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["ReagentCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MeasurementCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    source_identifier: Optional[str] = Field(alias="sourceIdentifier", default=None)
    and_: Optional["MeasurementCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["MeasurementCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["MeasurementCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RelationCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    ontology: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["RelationCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["RelationCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["RelationCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureRelationCategoryFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    id: Optional[ID] = None
    search: Optional[str] = None
    graph: Optional[ID] = None
    ontology: Optional[ID] = None
    pinned: Optional[bool] = None
    source_identifier: Optional[str] = Field(alias="sourceIdentifier", default=None)
    target_identifier: Optional[str] = Field(alias="targetIdentifier", default=None)
    and_: Optional["StructureRelationCategoryFilter"] = Field(alias="AND", default=None)
    or_: Optional["StructureRelationCategoryFilter"] = Field(alias="OR", default=None)
    not_: Optional["StructureRelationCategoryFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EntityFilter(BaseModel):
    """Filter for entities in the graph"""

    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of entity IDs"
    external_ids: Optional[Tuple[ID, ...]] = Field(alias="externalIds", default=None)
    "Filter by list of entity IDs"
    search: Optional[str] = None
    "Search entities by text"
    tags: Optional[Tuple[str, ...]] = None
    "Filter by list of categorie tags"
    graph: Optional[ID] = None
    "Filter by graph ID"
    categories: Optional[Tuple[ID, ...]] = None
    "Filter by list of entity categories"
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    "Filter by creation date before this date"
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    "Filter by creation date after this date"
    active: Optional[bool] = None
    "Filter by active status"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphPaginationInput(BaseModel):
    """No documentation"""

    limit: Optional[int] = None
    offset: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphFilter(BaseModel):
    """No documentation"""

    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of IDs"
    search: Optional[str] = None
    "Search by text"
    id: Optional[ID] = None
    pinned: Optional[bool] = None
    and_: Optional["GraphFilter"] = Field(alias="AND", default=None)
    or_: Optional["GraphFilter"] = Field(alias="OR", default=None)
    not_: Optional["GraphFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureFilter(BaseModel):
    """Filter for entity relations in the graph"""

    graph: Optional[ID] = None
    "Filter by graph ID"
    kind: Optional[ID] = None
    "Filter by relation kind"
    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of relation IDs"
    linked_expression: Optional[ID] = Field(alias="linkedExpression", default=None)
    "Filter by linked expression ID"
    search: Optional[str] = None
    "Search relations by text"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReagentFilter(BaseModel):
    """Filter for entities in the graph"""

    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of entity IDs"
    external_ids: Optional[Tuple[ID, ...]] = Field(alias="externalIds", default=None)
    "Filter by list of entity IDs"
    search: Optional[str] = None
    "Search entities by text"
    tags: Optional[Tuple[str, ...]] = None
    "Filter by list of categorie tags"
    graph: Optional[ID] = None
    "Filter by graph ID"
    categories: Optional[Tuple[ID, ...]] = None
    "Filter by list of entity categories"
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    "Filter by creation date before this date"
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    "Filter by creation date after this date"
    active: Optional[bool] = None
    "Filter by active status"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MetricFilter(BaseModel):
    """Filter for entity relations in the graph"""

    graph: Optional[ID] = None
    "Filter by graph ID"
    kind: Optional[ID] = None
    "Filter by relation kind"
    ids: Optional[Tuple[ID, ...]] = None
    "Filter by list of relation IDs"
    linked_expression: Optional[ID] = Field(alias="linkedExpression", default=None)
    "Filter by linked expression ID"
    search: Optional[str] = None
    "Search relations by text"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphInput(BaseModel):
    """Input type for creating a new ontology"""

    name: str
    "The name of the ontology (will be converted to snake_case)"
    description: Optional[str] = None
    "An optional description of the ontology"
    image: Optional[ID] = None
    "An optional ID reference to an associated image"
    pin: Optional[bool] = None
    "Whether this ontology should be pinned or not"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateGraphInput(BaseModel):
    """Input type for updating an existing ontology"""

    id: ID
    "The ID of the ontology to update"
    name: Optional[str] = None
    "New name for the ontology (will be converted to snake_case)"
    purl: Optional[str] = None
    "A new PURL for the ontology (will be converted to snake_case)"
    description: Optional[str] = None
    "New description for the ontology"
    image: Optional[ID] = None
    "New ID reference to an associated image"
    nodes: Optional[Tuple["GraphNodeInput", ...]] = None
    "New nodes for the ontology"
    pin: Optional[bool] = None
    "Whether this ontology should be pinned or not"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphNodeInput(BaseModel):
    """Input type for creating a new ontology node"""

    id: str
    "The AGE_NAME of the ontology"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    color: Optional[Tuple[int, ...]] = None
    "An optional RGBA color for the ontology node"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeleteGraphInput(BaseModel):
    """Input type for deleting an ontology"""

    id: ID
    "The ID of the ontology to delete"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PinGraphInput(BaseModel):
    """Input type for pinning an ontology"""

    id: ID
    "The ID of the ontology to pin"
    pinned: bool
    "Whether to pin the ontology or not"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MetricCategoryInput(MetricCategoryInputTrait, BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    structure_definition: "CategoryDefinitionInput" = Field(alias="structureDefinition")
    "The structure category for this expression"
    label: str
    "The label/name of the expression"
    kind: MetricKind
    "The type of metric data this expression represents"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CategoryDefinitionInput(BaseModel):
    """Input for creating a new expression"""

    category_filters: Optional[Tuple[ID, ...]] = Field(
        alias="categoryFilters", default=None
    )
    "A list of classes to filter the entities"
    tag_filters: Optional[Tuple[str, ...]] = Field(alias="tagFilters", default=None)
    "A list of tags to filter the entities by"
    default_use_active: Optional[ID] = Field(alias="defaultUseActive", default=None)
    "The default ACTIVE reagent to use for this port if a reagent is not provided"
    default_use_new: Optional[ID] = Field(alias="defaultUseNew", default=None)
    "The default creation of entity or reagent to use for this port if a reagent is not provided"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MeasurementCategoryInput(MeasurementCategoryInputTrait, BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    label: str
    "The label/name of the expression"
    structure_definition: "StructureCategoryDefinitionInput" = Field(
        alias="structureDefinition"
    )
    "The source definition for this expression"
    entity_definition: CategoryDefinitionInput = Field(alias="entityDefinition")
    "The target definition for this expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureCategoryDefinitionInput(BaseModel):
    """Input for creating a new expression"""

    category_filters: Optional[Tuple[ID, ...]] = Field(
        alias="categoryFilters", default=None
    )
    "A list of classes to filter the entities"
    identifier_filters: Optional[Tuple[StructureIdentifier, ...]] = Field(
        alias="identifierFilters", default=None
    )
    "A list of StructureIdentifier to filter the entities"
    tag_filters: Optional[Tuple[str, ...]] = Field(alias="tagFilters", default=None)
    "A list of tags to filter the entities by"
    default_use_active: Optional[ID] = Field(alias="defaultUseActive", default=None)
    "The default ACTIVE reagent to use for this port if a reagent is not provided"
    default_use_new: Optional[ID] = Field(alias="defaultUseNew", default=None)
    "The default creation of entity or reagent to use for this port if a reagent is not provided"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureCategoryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[RemoteUpload] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    identifier: StructureIdentifier
    "The label/name of the expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateStructureCategoryInput(BaseModel):
    """Input for updating an existing expression"""

    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    id: ID
    "The ID of the expression to update"
    identifier: Optional[str] = None
    "The label/name of the expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RelationCategoryInput(RelationCategoryInputTrait, BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    label: str
    "The label/name of the expression"
    source_definition: CategoryDefinitionInput = Field(alias="sourceDefinition")
    "The source definition for this expression"
    target_definition: CategoryDefinitionInput = Field(alias="targetDefinition")
    "The target definition for this expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureRelationCategoryInput(StructureRelationCategoryInputTrait, BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    label: str
    "The label/name of the expression"
    source_definition: StructureCategoryDefinitionInput = Field(
        alias="sourceDefinition"
    )
    "The source definition for this expression"
    target_definition: StructureCategoryDefinitionInput = Field(
        alias="targetDefinition"
    )
    "The target definition for this expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateStructureRelationCategoryInput(BaseModel):
    """Input for updating an existing expression"""

    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    label: Optional[str] = None
    "New label for the expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EntityCategoryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    label: str
    "The label/name of the expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateEntityCategoryInput(BaseModel):
    """Input for updating an existing generic category"""

    description: Optional[str] = None
    "New description for the expression"
    purl: Optional[str] = None
    "New permanent URL for the expression"
    color: Optional[Tuple[int, ...]] = None
    "New RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "New image ID for the expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    id: ID
    "The ID of the expression to update"
    label: Optional[str] = None
    "New label for the generic category"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReagentCategoryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    label: str
    "The label/name of the expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NaturalEventCategoryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    label: str
    "The label/name of the expression"
    source_entity_roles: Tuple["EntityRoleDefinitionInput", ...] = Field(
        alias="sourceEntityRoles"
    )
    "The source definitions for this expression"
    target_entity_roles: Tuple["EntityRoleDefinitionInput", ...] = Field(
        alias="targetEntityRoles"
    )
    "The target definitions for this expression"
    support_definition: CategoryDefinitionInput = Field(alias="supportDefinition")
    "The support definition for this expression"
    plate_children: Optional[Tuple["PlateChildInput", ...]] = Field(
        alias="plateChildren", default=None
    )
    "A list of children for the plate"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EntityRoleDefinitionInput(EntityRoleDefinitionInputTrait, BaseModel):
    """Input for creating a new expression"""

    role: str
    "The parameter name"
    variable_amount: Optional[bool] = Field(alias="variableAmount", default=None)
    "Whether this port allows a variable amount of entities or not"
    optional: Optional[bool] = None
    "Whether this port is optional or not"
    category_definition: CategoryDefinitionInput = Field(alias="categoryDefinition")
    "The category definition for this expression"
    description: Optional[str] = None
    "A detailed description of the role"
    label: Optional[str] = None
    "The label/name of the role"
    allow_multiple: Optional[bool] = Field(alias="allowMultiple", default=None)
    "Whether this port allows multiple entities or not"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PlateChildInput(BaseModel):
    """No documentation"""

    id: Optional[ID] = None
    type: Optional[str] = None
    text: Optional[str] = None
    children: Optional[Tuple["PlateChildInput", ...]] = None
    value: Optional[str] = None
    color: Optional[str] = None
    font_size: Optional[str] = Field(alias="fontSize", default=None)
    background_color: Optional[str] = Field(alias="backgroundColor", default=None)
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateNaturalEventCategoryInput(BaseModel):
    """Input for updating an existing expression"""

    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional ID reference to an associated image"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    id: ID
    "The ID of the expression to update"
    label: Optional[str] = None
    "The label/name of the expression"
    source_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="sourceEntityRoles", default=None
    )
    "The source definitions for this expression"
    target_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="targetEntityRoles", default=None
    )
    "The target definitions for this expression"
    support_definition: Optional[CategoryDefinitionInput] = Field(
        alias="supportDefinition", default=None
    )
    "The support definition for this expression"
    plate_children: Optional[Tuple[PlateChildInput, ...]] = Field(
        alias="plateChildren", default=None
    )
    "A list of children for the plate"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ProtocolEventCategoryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the graph this expression belongs to. If not provided, uses default ontology"
    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional image associated with this expression"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    sequence: Optional[ID] = None
    "The ID of the sequence this category will get internal_ids from"
    auto_create_sequence: Optional[bool] = Field(
        alias="autoCreateSequence", default=None
    )
    "Whether to create a sequence if it does not exist"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    label: str
    "The label/name of the expression"
    plate_children: Optional[Tuple[PlateChildInput, ...]] = Field(
        alias="plateChildren", default=None
    )
    "A list of children for the plate"
    source_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="sourceEntityRoles", default=None
    )
    "The source definitions for this expression"
    source_reagent_roles: Optional[Tuple["ReagentRoleDefinitionInput", ...]] = Field(
        alias="sourceReagentRoles", default=None
    )
    "The target definitions for this expression"
    target_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="targetEntityRoles", default=None
    )
    "The target definitions for this expression"
    target_reagent_roles: Optional[Tuple["ReagentRoleDefinitionInput", ...]] = Field(
        alias="targetReagentRoles", default=None
    )
    "The target definitions for this expression"
    variable_definitions: Optional[Tuple["VariableDefinitionInput", ...]] = Field(
        alias="variableDefinitions", default=None
    )
    "The variable definitions for this expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReagentRoleDefinitionInput(ReagentRoleDefinitionInputTrait, BaseModel):
    """Input for creating a new expression"""

    role: str
    "The parameter name"
    needs_quantity: Optional[bool] = Field(alias="needsQuantity", default=None)
    "Whether this port needs a quantity or not"
    variable_amount: Optional[bool] = Field(alias="variableAmount", default=None)
    "Whether this port allows a variable amount of entities or not"
    optional: Optional[bool] = None
    "Whether this port is optional or not"
    category_definition: CategoryDefinitionInput = Field(alias="categoryDefinition")
    "The category definition for this expression"
    description: Optional[str] = None
    "A detailed description of the role"
    label: Optional[str] = None
    "The label/name of the role"
    allow_multiple: Optional[bool] = Field(alias="allowMultiple", default=None)
    "Whether this port allows multiple entities or not"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class VariableDefinitionInput(BaseModel):
    """Input for creating a new expression"""

    param: str
    "The parameter name"
    value_kind: MetricKind = Field(alias="valueKind")
    "The type of metric data this expression represents"
    optional: Optional[bool] = None
    "Whether this port is optional or not"
    default: Optional[Any] = None
    "The default value for this port"
    description: Optional[str] = None
    "A detailed description of the role"
    label: Optional[str] = None
    "The label/name of the role"
    options: Optional[Tuple["OptionInput", ...]] = None
    "A list of options for this port (if only a few values are allowed)"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OptionInput(BaseModel):
    """No documentation"""

    label: str
    "The label of the option"
    value: Any
    "The value of the option. This can be a string, number, or boolean"
    description: Optional[str] = None
    "A detailed description of the option"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateProtocolEventCategoryInput(BaseModel):
    """Input for updating an existing expression"""

    description: Optional[str] = None
    "A detailed description of the expression"
    purl: Optional[str] = None
    "Permanent URL identifier for the expression"
    color: Optional[Tuple[int, ...]] = None
    "RGBA color values as list of 3 or 4 integers"
    image: Optional[ID] = None
    "An optional ID reference to an associated image"
    tags: Optional[Tuple[str, ...]] = None
    "A list of tags associated with this expression"
    pin: Optional[bool] = None
    "Whether this expression should be pinned or not"
    position_x: Optional[float] = Field(alias="positionX", default=None)
    "An optional x position for the ontology node"
    position_y: Optional[float] = Field(alias="positionY", default=None)
    "An optional y position for the ontology node"
    height: Optional[float] = None
    "An optional height for the ontology node"
    width: Optional[float] = None
    "An optional width for the ontology node"
    id: ID
    "The ID of the expression to update"
    label: Optional[str] = None
    "The label/name of the expression"
    plate_children: Optional[Tuple[PlateChildInput, ...]] = Field(
        alias="plateChildren", default=None
    )
    "A list of children for the plate"
    source_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="sourceEntityRoles", default=None
    )
    "The source definitions for this expression"
    source_reagent_roles: Optional[Tuple[ReagentRoleDefinitionInput, ...]] = Field(
        alias="sourceReagentRoles", default=None
    )
    "The target definitions for this expression"
    target_entity_roles: Optional[Tuple[EntityRoleDefinitionInput, ...]] = Field(
        alias="targetEntityRoles", default=None
    )
    "The target definitions for this expression"
    target_reagent_roles: Optional[Tuple[ReagentRoleDefinitionInput, ...]] = Field(
        alias="targetReagentRoles", default=None
    )
    "The target definitions for this expression"
    variable_definitions: Optional[Tuple[VariableDefinitionInput, ...]] = Field(
        alias="variableDefinitions", default=None
    )
    "The variable definitions for this expression"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ScatterPlotInput(BaseModel):
    """Input for creating a new expression"""

    query: ID
    "The query to use"
    name: str
    "The label/name of the expression"
    description: Optional[str] = None
    "A detailed description of the expression"
    id_column: str = Field(alias="idColumn")
    "The column to use for the ID of the points"
    x_column: str = Field(alias="xColumn")
    "The column to use for the x-axis"
    x_id_column: Optional[str] = Field(alias="xIdColumn", default=None)
    "The column to use for the x-axis ID (node, or edge)"
    y_column: str = Field(alias="yColumn")
    "The column to use for the y-axis"
    y_id_column: Optional[str] = Field(alias="yIdColumn", default=None)
    "The column to use for the y-axis ID (node, or edge)"
    size_column: Optional[str] = Field(alias="sizeColumn", default=None)
    "The column to use for the size of the points"
    color_column: Optional[str] = Field(alias="colorColumn", default=None)
    "The column to use for the color of the points"
    shape_column: Optional[str] = Field(alias="shapeColumn", default=None)
    "The column to use for the shape of the points"
    test_against: Optional[ID] = Field(alias="testAgainst", default=None)
    "The graph to test against"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeleteScatterPlotInput(BaseModel):
    """Input for deleting an expression"""

    id: ID
    "The ID of the expression to delete"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordNaturalEventInput(BaseModel):
    """No documentation"""

    category: ID
    entity_sources: Optional[Tuple["NodeMapping", ...]] = Field(
        alias="entitySources", default=None
    )
    entity_targets: Optional[Tuple["NodeMapping", ...]] = Field(
        alias="entityTargets", default=None
    )
    supporting_structure: Optional[ID] = Field(
        alias="supportingStructure", default=None
    )
    external_id: Optional[str] = Field(alias="externalId", default=None)
    valid_from: Optional[datetime] = Field(alias="validFrom", default=None)
    valid_to: Optional[datetime] = Field(alias="validTo", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NodeMapping(BaseModel):
    """No documentation"""

    key: str
    node: ID
    quantity: Optional[float] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordProtocolEventInput(BaseModel):
    """No documentation"""

    category: ID
    external_id: Optional[str] = Field(alias="externalId", default=None)
    entity_sources: Optional[Tuple[NodeMapping, ...]] = Field(
        alias="entitySources", default=None
    )
    entity_targets: Optional[Tuple[NodeMapping, ...]] = Field(
        alias="entityTargets", default=None
    )
    reagent_sources: Optional[Tuple[NodeMapping, ...]] = Field(
        alias="reagentSources", default=None
    )
    reagent_targets: Optional[Tuple[NodeMapping, ...]] = Field(
        alias="reagentTargets", default=None
    )
    variables: Optional[Tuple["VariableMappingInput", ...]] = None
    valid_from: Optional[datetime] = Field(alias="validFrom", default=None)
    valid_to: Optional[datetime] = Field(alias="validTo", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class VariableMappingInput(BaseModel):
    """No documentation"""

    key: str
    value: Any
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ToldYouSoInput(BaseModel):
    """Input type for creating a new entity"""

    reason: Optional[str] = None
    "The reason why you made this assumption"
    name: Optional[str] = None
    "Optional name for the entity"
    external_id: Optional[str] = Field(alias="externalId", default=None)
    "An optional external ID for the entity (will upsert if exists)"
    context: Optional["ContextInput"] = None
    "The context of the measurement"
    valid_from: Optional[str] = Field(alias="validFrom", default=None)
    "The start date of the measurement"
    valid_to: Optional[str] = Field(alias="validTo", default=None)
    "The end date of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ContextInput(BaseModel):
    """No documentation"""

    assignation_id: Optional[ID] = Field(alias="assignationId", default=None)
    assignee_id: Optional[ID] = Field(alias="assigneeId", default=None)
    template_id: Optional[ID] = Field(alias="templateId", default=None)
    node_id: Optional[ID] = Field(alias="nodeId", default=None)
    args: Optional[Any] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MeasurementInput(BaseModel):
    """No documentation"""

    category: ID
    structure: NodeID
    entity: NodeID
    valid_from: Optional[datetime] = Field(alias="validFrom", default=None)
    valid_to: Optional[datetime] = Field(alias="validTo", default=None)
    context: Optional[ContextInput] = None
    "The context of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RelationInput(BaseModel):
    """Input type for creating a relation between two entities"""

    source: ID
    "ID of the left entity (format: graph:id)"
    target: ID
    "ID of the right entity (format: graph:id)"
    category: ID
    "ID of the relation category (LinkedExpression)"
    context: Optional[ContextInput] = None
    "The context of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureRelationInput(BaseModel):
    """Input type for creating a relation between two entities"""

    source: ID
    "ID of the left entity (format: graph:id)"
    target: ID
    "ID of the right entity (format: graph:id)"
    category: ID
    "ID of the relation category (LinkedExpression)"
    context: Optional[ContextInput] = None
    "The context of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MetricInput(BaseModel):
    """No documentation"""

    structure: NodeID
    category: ID
    value: Any
    "The value of the measurement"
    context: Optional[ContextInput] = None
    "The context of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StructureInput(BaseModel):
    """No documentation"""

    structure: StructureString
    graph: ID
    context: Optional[ContextInput] = None
    "The context of the measurement"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateModelInput(BaseModel):
    """Input type for creating a new model"""

    name: str
    "The name of the model"
    model: RemoteUpload
    "The uploaded model file (e.g. .h5, .onnx, .pt)"
    view: Optional[ID] = None
    "Optional view ID to associate with the model"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMediaUploadInput(BaseModel):
    """No documentation"""

    key: str
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EntityInput(BaseModel):
    """Input type for creating a new entity"""

    entity_category: ID = Field(alias="entityCategory")
    "The ID of the kind (LinkedExpression) to create the entity from"
    name: Optional[str] = None
    "Optional name for the entity"
    external_id: Optional[str] = Field(alias="externalId", default=None)
    "An optional external ID for the entity (will upsert if exists)"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReagentInput(BaseModel):
    """Input type for creating a new entity"""

    reagent_category: ID = Field(alias="reagentCategory")
    "The ID of the kind (LinkedExpression) to create the entity from"
    name: Optional[str] = None
    "Optional name for the entity"
    external_id: Optional[str] = Field(alias="externalId", default=None)
    "An optional external ID for the entity (will upsert if exists)"
    set_active: Optional[bool] = Field(alias="setActive", default=None)
    "Set the reagent as active"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphQueryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the ontology this expression belongs to. If not provided, uses default ontology"
    name: str
    "The label/name of the expression"
    query: Cypher
    "The label/name of the expression"
    description: Optional[str] = None
    "A detailed description of the expression"
    kind: ViewKind
    "The kind/type of this expression"
    columns: Optional[Tuple["ColumnInput", ...]] = None
    "The columns (if ViewKind is Table)"
    relevant_for: Optional[Tuple[ID, ...]] = Field(alias="relevantFor", default=None)
    "A list of categories where this query is releveant and should be shown"
    pin: Optional[bool] = None
    "Whether to pin this expression for the current user"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ColumnInput(BaseModel):
    """No documentation"""

    name: str
    kind: ColumnKind
    label: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ID] = None
    value_kind: Optional[MetricKind] = Field(alias="valueKind", default=None)
    searchable: Optional[bool] = None
    idfor: Optional[Tuple[ID, ...]] = None
    preferhidden: Optional[bool] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PinGraphQueryInput(BaseModel):
    """No documentation"""

    id: ID
    pin: bool
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NodeQueryInput(BaseModel):
    """Input for creating a new expression"""

    graph: ID
    "The ID of the ontology this expression belongs to. If not provided, uses default ontology"
    name: str
    "The label/name of the expression"
    query: Cypher
    "The label/name of the expression"
    description: Optional[str] = None
    "A detailed description of the expression"
    kind: ViewKind
    "The kind/type of this expression"
    columns: Optional[Tuple[ColumnInput, ...]] = None
    "The columns (if ViewKind is Table)"
    test_against: Optional[ID] = Field(alias="testAgainst", default=None)
    "The node to test against"
    relevant_for: Optional[Tuple[ID, ...]] = Field(alias="relevantFor", default=None)
    "The list of categories this expression is relevant for"
    pin: Optional[bool] = None
    "Whether to pin this expression for the current user"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PinNodeQueryInput(BaseModel):
    """No documentation"""

    id: ID
    pin: bool
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BaseCategoryGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class BaseCategoryBase(BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"
    graph: BaseCategoryGraph
    "The ontology the expression belongs to."


class BaseCategoryCatch(BaseCategoryBase):
    """Catch all class for BaseCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"
    graph: BaseCategoryGraph
    "The ontology the expression belongs to."


class BaseCategoryMetricCategory(BaseCategoryBase, MetricCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class BaseCategoryStructureCategory(
    BaseCategoryBase, StructureCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class BaseCategoryProtocolEventCategory(
    BaseCategoryBase, ProtocolEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class BaseCategoryEntityCategory(BaseCategoryBase, EntityCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class BaseCategoryReagentCategory(BaseCategoryBase, ReagentCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class BaseCategoryNaturalEventCategory(
    BaseCategoryBase, NaturalEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class BaseCategoryMeasurementCategory(
    BaseCategoryBase, MeasurementCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )


class BaseCategoryRelationCategory(BaseCategoryBase, RelationCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )


class BaseCategoryStructureRelationCategory(
    BaseCategoryBase, StructureRelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )


class BaseNodeCategoryBase(NodeCategoryTrait, BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"
    position_x: Optional[float] = Field(default=None, alias="positionX")
    "The x position of the node in the graph"
    position_y: Optional[float] = Field(default=None, alias="positionY")
    "The y position of the node in the graph"
    width: Optional[float] = Field(default=None)
    "The width of the node in the graph"
    height: Optional[float] = Field(default=None)
    "The height of the node in the graph"


class BaseNodeCategoryCatch(BaseNodeCategoryBase):
    """Catch all class for BaseNodeCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"
    position_x: Optional[float] = Field(default=None, alias="positionX")
    "The x position of the node in the graph"
    position_y: Optional[float] = Field(default=None, alias="positionY")
    "The y position of the node in the graph"
    width: Optional[float] = Field(default=None)
    "The width of the node in the graph"
    height: Optional[float] = Field(default=None)
    "The height of the node in the graph"


class BaseNodeCategoryMetricCategory(
    BaseNodeCategoryBase, MetricCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class BaseNodeCategoryStructureCategory(
    BaseNodeCategoryBase, StructureCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class BaseNodeCategoryProtocolEventCategory(
    BaseNodeCategoryBase, ProtocolEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class BaseNodeCategoryEntityCategory(
    BaseNodeCategoryBase, EntityCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class BaseNodeCategoryReagentCategory(
    BaseNodeCategoryBase, ReagentCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class BaseNodeCategoryNaturalEventCategory(
    BaseNodeCategoryBase, NaturalEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class BaseEdgeCategoryBase(BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"


class BaseEdgeCategoryCatch(BaseEdgeCategoryBase):
    """Catch all class for BaseEdgeCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"


class BaseEdgeCategoryMeasurementCategory(
    BaseEdgeCategoryBase, MeasurementCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )


class BaseEdgeCategoryRelationCategory(
    BaseEdgeCategoryBase, RelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )


class BaseEdgeCategoryStructureRelationCategory(
    BaseEdgeCategoryBase, StructureRelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )


class BaseNodeBase(NodeTrait, BaseModel):
    """No documentation"""

    id: NodeID
    "The unique identifier of the entity within its graph"
    label: str


class BaseNodeCatch(BaseNodeBase):
    """Catch all class for BaseNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: NodeID
    "The unique identifier of the entity within its graph"
    label: str


class BaseNodeEntity(BaseNodeBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class BaseNodeStructure(BaseNodeBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class BaseNodeMetric(BaseNodeBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class BaseNodeProtocolEvent(BaseNodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class BaseNodeNaturalEvent(BaseNodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class BaseNodeReagent(BaseNodeBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class NaturalEventCategory(NaturalEventCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class NaturalEvent(BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    valid_from: Optional[datetime] = Field(default=None, alias="validFrom")
    "Protocol steps where this entity was the target"
    valid_to: Optional[datetime] = Field(default=None, alias="validTo")
    "Protocol steps where this entity was the target"
    category: NaturalEventCategory
    "Protocol steps where this entity was the target"
    model_config = ConfigDict(frozen=True)


class ProtocolEventCategory(ProtocolEventCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ProtocolEvent(BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    valid_from: Optional[datetime] = Field(default=None, alias="validFrom")
    "Protocol steps where this entity was the target"
    valid_to: Optional[datetime] = Field(default=None, alias="validTo")
    "Protocol steps where this entity was the target"
    category: ProtocolEventCategory
    "Protocol steps where this entity was the target"
    model_config = ConfigDict(frozen=True)


class PresignedPostCredentials(BaseModel):
    """Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["PresignedPostCredentials"] = Field(
        alias="__typename", default="PresignedPostCredentials", exclude=True
    )
    key: str
    x_amz_credential: str = Field(alias="xAmzCredential")
    x_amz_algorithm: str = Field(alias="xAmzAlgorithm")
    x_amz_date: str = Field(alias="xAmzDate")
    x_amz_signature: str = Field(alias="xAmzSignature")
    policy: str
    datalayer: str
    bucket: str
    store: str
    model_config = ConfigDict(frozen=True)


class BaseEdgeBase(BaseModel):
    """No documentation"""

    id: NodeID
    "The unique identifier of the entity within its graph"
    left_id: str = Field(alias="leftId")
    right_id: str = Field(alias="rightId")


class BaseEdgeCatch(BaseEdgeBase):
    """Catch all class for BaseEdgeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: NodeID
    "The unique identifier of the entity within its graph"
    left_id: str = Field(alias="leftId")
    right_id: str = Field(alias="rightId")


class BaseEdgeMeasurement(BaseEdgeBase, BaseModel):
    """A measurement is an edge from a structure to an entity. Importantly Measurement are always directed from the structure to the entity, and never the other way around."""

    typename: Literal["Measurement"] = Field(
        alias="__typename", default="Measurement", exclude=True
    )


class BaseEdgeRelation(BaseEdgeBase, BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["Relation"] = Field(
        alias="__typename", default="Relation", exclude=True
    )


class BaseEdgeParticipant(BaseEdgeBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Participant"] = Field(
        alias="__typename", default="Participant", exclude=True
    )


class BaseEdgeDescription(BaseEdgeBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Description"] = Field(
        alias="__typename", default="Description", exclude=True
    )


class BaseEdgeStructureRelation(BaseEdgeBase, BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["StructureRelation"] = Field(
        alias="__typename", default="StructureRelation", exclude=True
    )


class MeasurementCategory(MeasurementCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class Measurement(BaseModel):
    """A measurement is an edge from a structure to an entity. Importantly Measurement are always directed from the structure to the entity, and never the other way around."""

    typename: Literal["Measurement"] = Field(
        alias="__typename", default="Measurement", exclude=True
    )
    valid_from: datetime = Field(alias="validFrom")
    "Timestamp from when this entity is valid"
    valid_to: datetime = Field(alias="validTo")
    "Timestamp until when this entity is valid"
    category: MeasurementCategory
    model_config = ConfigDict(frozen=True)


class RelationCategory(RelationCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class Relation(BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["Relation"] = Field(
        alias="__typename", default="Relation", exclude=True
    )
    category: RelationCategory
    model_config = ConfigDict(frozen=True)


class StructureRelationCategory(StructureRelationCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class StructureRelation(BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["StructureRelation"] = Field(
        alias="__typename", default="StructureRelation", exclude=True
    )
    category: StructureRelationCategory
    model_config = ConfigDict(frozen=True)


class Participant(BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Participant"] = Field(
        alias="__typename", default="Participant", exclude=True
    )
    role: str
    "Timestamp from when this entity is valid"
    quantity: Optional[float] = Field(default=None)
    "Timestamp from when this entity is valid"
    model_config = ConfigDict(frozen=True)


class EntityCategory(EntityCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class Entity(EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    category: EntityCategory
    "Protocol steps where this entity was the target"
    label: str
    model_config = ConfigDict(frozen=True)


class ListEntityCategory(EntityCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ListEntity(EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    category: ListEntityCategory
    "Protocol steps where this entity was the target"
    model_config = ConfigDict(frozen=True)


class ListGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)
    pinned: bool
    model_config = ConfigDict(frozen=True)


class ListGraphQuery(BaseModel):
    """A view of a graph, that contains entities and relations."""

    typename: Literal["GraphQuery"] = Field(
        alias="__typename", default="GraphQuery", exclude=True
    )
    id: ID
    name: str
    query: str
    description: Optional[str] = Field(default=None)
    pinned: bool
    model_config = ConfigDict(frozen=True)


class BaseListCategoryStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class BaseListCategoryTags(BaseModel):
    """A tag is a label that can be assigned to entities and relations."""

    typename: Literal["Tag"] = Field(alias="__typename", default="Tag", exclude=True)
    id: ID
    value: str
    model_config = ConfigDict(frozen=True)


class BaseListCategoryBase(BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"
    description: Optional[str] = Field(default=None)
    "A description of the expression."
    store: Optional[BaseListCategoryStore] = Field(default=None)
    "An image or other media file that can be used to represent the expression."
    tags: Tuple[BaseListCategoryTags, ...]
    "The tags that are associated with the expression"


class BaseListCategoryCatch(BaseListCategoryBase):
    """Catch all class for BaseListCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"
    description: Optional[str] = Field(default=None)
    "A description of the expression."
    store: Optional[BaseListCategoryStore] = Field(default=None)
    "An image or other media file that can be used to represent the expression."
    tags: Tuple[BaseListCategoryTags, ...]
    "The tags that are associated with the expression"


class BaseListCategoryMetricCategory(
    BaseListCategoryBase, MetricCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class BaseListCategoryStructureCategory(
    BaseListCategoryBase, StructureCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class BaseListCategoryProtocolEventCategory(
    BaseListCategoryBase, ProtocolEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class BaseListCategoryEntityCategory(
    BaseListCategoryBase, EntityCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class BaseListCategoryReagentCategory(
    BaseListCategoryBase, ReagentCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class BaseListCategoryNaturalEventCategory(
    BaseListCategoryBase, NaturalEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class BaseListCategoryMeasurementCategory(
    BaseListCategoryBase, MeasurementCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )


class BaseListCategoryRelationCategory(
    BaseListCategoryBase, RelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )


class BaseListCategoryStructureRelationCategory(
    BaseListCategoryBase, StructureRelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )


class BaseListNodeCategoryBase(NodeCategoryTrait, BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"
    position_x: Optional[float] = Field(default=None, alias="positionX")
    "The x position of the node in the graph"
    position_y: Optional[float] = Field(default=None, alias="positionY")
    "The y position of the node in the graph"
    width: Optional[float] = Field(default=None)
    "The width of the node in the graph"
    height: Optional[float] = Field(default=None)
    "The height of the node in the graph"


class BaseListNodeCategoryCatch(BaseListNodeCategoryBase):
    """Catch all class for BaseListNodeCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"
    position_x: Optional[float] = Field(default=None, alias="positionX")
    "The x position of the node in the graph"
    position_y: Optional[float] = Field(default=None, alias="positionY")
    "The y position of the node in the graph"
    width: Optional[float] = Field(default=None)
    "The width of the node in the graph"
    height: Optional[float] = Field(default=None)
    "The height of the node in the graph"


class BaseListNodeCategoryMetricCategory(
    BaseListNodeCategoryBase, MetricCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class BaseListNodeCategoryStructureCategory(
    BaseListNodeCategoryBase, StructureCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class BaseListNodeCategoryProtocolEventCategory(
    BaseListNodeCategoryBase, ProtocolEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class BaseListNodeCategoryEntityCategory(
    BaseListNodeCategoryBase, EntityCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class BaseListNodeCategoryReagentCategory(
    BaseListNodeCategoryBase, ReagentCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class BaseListNodeCategoryNaturalEventCategory(
    BaseListNodeCategoryBase, NaturalEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class BaseListEdgeCategoryBase(BaseModel):
    """No documentation"""

    id: ID
    "The unique identifier of the expression within its graph"


class BaseListEdgeCategoryCatch(BaseListEdgeCategoryBase):
    """Catch all class for BaseListEdgeCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    "The unique identifier of the expression within its graph"


class BaseListEdgeCategoryMeasurementCategory(
    BaseListEdgeCategoryBase, MeasurementCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )


class BaseListEdgeCategoryRelationCategory(
    BaseListEdgeCategoryBase, RelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )


class BaseListEdgeCategoryStructureRelationCategory(
    BaseListEdgeCategoryBase, StructureRelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )


class MetricCategory(MetricCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class Metric(MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    category: MetricCategory
    "Protocol steps where this entity was the target"
    value: float
    "The value of the metric"
    model_config = ConfigDict(frozen=True)


class ListMetric(MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    value: float
    "The value of the metric"
    label: str
    model_config = ConfigDict(frozen=True)


class NodeQuery(BaseModel):
    """A view of a node entities and relations."""

    typename: Literal["NodeQuery"] = Field(
        alias="__typename", default="NodeQuery", exclude=True
    )
    id: ID
    name: str
    pinned: bool
    model_config = ConfigDict(frozen=True)


class ListNodeQuery(BaseModel):
    """A view of a node entities and relations."""

    typename: Literal["NodeQuery"] = Field(
        alias="__typename", default="NodeQuery", exclude=True
    )
    id: ID
    name: str
    query: str
    description: Optional[str] = Field(default=None)
    pinned: bool
    model_config = ConfigDict(frozen=True)


class PairsPairsSourceBase(NodeTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class PairsPairsSourceBaseEntity(PairsPairsSourceBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class PairsPairsSourceBaseStructure(PairsPairsSourceBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    identifier: str
    "The unique identifier of the entity within its graph"
    object: str
    "The expression that defines this entity's type"


class PairsPairsSourceBaseMetric(PairsPairsSourceBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class PairsPairsSourceBaseProtocolEvent(PairsPairsSourceBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class PairsPairsSourceBaseNaturalEvent(PairsPairsSourceBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class PairsPairsSourceBaseReagent(PairsPairsSourceBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class PairsPairsSourceBaseCatchAll(PairsPairsSourceBase, BaseModel):
    """Catch all class for PairsPairsSourceBase"""

    typename: str = Field(alias="__typename", exclude=True)


class PairsPairsTargetBase(NodeTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class PairsPairsTargetBaseEntity(PairsPairsTargetBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class PairsPairsTargetBaseStructure(PairsPairsTargetBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    identifier: str
    "The unique identifier of the entity within its graph"
    object: str
    "The expression that defines this entity's type"


class PairsPairsTargetBaseMetric(PairsPairsTargetBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class PairsPairsTargetBaseProtocolEvent(PairsPairsTargetBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class PairsPairsTargetBaseNaturalEvent(PairsPairsTargetBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class PairsPairsTargetBaseReagent(PairsPairsTargetBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class PairsPairsTargetBaseCatchAll(PairsPairsTargetBase, BaseModel):
    """Catch all class for PairsPairsTargetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class PairsPairs(BaseModel):
    """A paired structure two entities and the relation between them."""

    typename: Literal["Pair"] = Field(alias="__typename", default="Pair", exclude=True)
    source: Union[
        Annotated[
            Union[
                PairsPairsSourceBaseEntity,
                PairsPairsSourceBaseStructure,
                PairsPairsSourceBaseMetric,
                PairsPairsSourceBaseProtocolEvent,
                PairsPairsSourceBaseNaturalEvent,
                PairsPairsSourceBaseReagent,
            ],
            Field(discriminator="typename"),
        ],
        PairsPairsSourceBaseCatchAll,
    ]
    "The left entity."
    target: Union[
        Annotated[
            Union[
                PairsPairsTargetBaseEntity,
                PairsPairsTargetBaseStructure,
                PairsPairsTargetBaseMetric,
                PairsPairsTargetBaseProtocolEvent,
                PairsPairsTargetBaseNaturalEvent,
                PairsPairsTargetBaseReagent,
            ],
            Field(discriminator="typename"),
        ],
        PairsPairsTargetBaseCatchAll,
    ]
    "The right entity."
    model_config = ConfigDict(frozen=True)


class Pairs(BaseModel):
    """A collection of paired entities."""

    typename: Literal["Pairs"] = Field(
        alias="__typename", default="Pairs", exclude=True
    )
    pairs: Tuple[PairsPairs, ...]
    "The paired entities."
    model_config = ConfigDict(frozen=True)


class ReagentCategory(ReagentCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class Reagent(BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    category: ReagentCategory
    "Protocol steps where this entity was the target"
    external_id: Optional[str] = Field(default=None, alias="externalId")
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class ListReagent(BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class EntityCategoryDefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ReagentCategoryDefinition(BaseModel):
    """No documentation"""

    typename: Literal["ReagentCategoryDefinition"] = Field(
        alias="__typename", default="ReagentCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class VariableDefinition(BaseModel):
    """No documentation"""

    typename: Literal["VariableDefinition"] = Field(
        alias="__typename", default="VariableDefinition", exclude=True
    )
    param: str
    value_kind: MetricKind = Field(alias="valueKind")
    default: Optional[Any] = Field(default=None)
    optional: bool
    model_config = ConfigDict(frozen=True)


class ScatterPlot(BaseModel):
    """A scatter plot of a table graph, that contains entities and relations."""

    typename: Literal["ScatterPlot"] = Field(
        alias="__typename", default="ScatterPlot", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)
    x_column: str = Field(alias="xColumn")
    y_column: str = Field(alias="yColumn")
    model_config = ConfigDict(frozen=True)


class ListScatterPlot(BaseModel):
    """A scatter plot of a table graph, that contains entities and relations."""

    typename: Literal["ScatterPlot"] = Field(
        alias="__typename", default="ScatterPlot", exclude=True
    )
    id: ID
    name: str
    x_column: str = Field(alias="xColumn")
    y_column: str = Field(alias="yColumn")
    model_config = ConfigDict(frozen=True)


class MediaStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    id: ID
    presigned_url: str = Field(alias="presignedUrl")
    key: str
    model_config = ConfigDict(frozen=True)


class Structure(StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    object: str
    "The expression that defines this entity's type"
    identifier: str
    "The unique identifier of the entity within its graph"
    model_config = ConfigDict(frozen=True)


class ListStructureCategory(StructureCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )
    identifier: str
    "The structure that this class represents"
    id: ID
    "The unique identifier of the expression within its graph"
    model_config = ConfigDict(frozen=True)


class ListStructure(StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    category: ListStructureCategory
    "Protocol steps where this entity was the target"
    model_config = ConfigDict(frozen=True)


class InformedStructureCategory(StructureCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )
    id: ID
    "The unique identifier of the expression within its graph"
    identifier: str
    "The structure that this class represents"
    model_config = ConfigDict(frozen=True)


class InformedStructureGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class InformedStructure(StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    id: NodeID
    "The unique identifier of the entity within its graph"
    category: InformedStructureCategory
    "Protocol steps where this entity was the target"
    graph: InformedStructureGraph
    "The unique identifier of the entity within its graph"
    model_config = ConfigDict(frozen=True)


class Column(BaseModel):
    """A column definition for a table view."""

    typename: Literal["Column"] = Field(
        alias="__typename", default="Column", exclude=True
    )
    name: str
    kind: ColumnKind
    value_kind: Optional[MetricKind] = Field(default=None, alias="valueKind")
    label: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    category: Optional[ID] = Field(default=None)
    searchable: Optional[bool] = Field(default=None)
    idfor: Optional[Tuple[ID, ...]] = Field(default=None)
    preferhidden: Optional[bool] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class StructureCategory(
    BaseNodeCategoryStructureCategory,
    BaseCategoryStructureCategory,
    StructureCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )
    identifier: str
    "The structure that this class represents"
    model_config = ConfigDict(frozen=True)


class MetricCategory(
    BaseNodeCategoryMetricCategory,
    BaseCategoryMetricCategory,
    MetricCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )
    metric_kind: MetricKind = Field(alias="metricKind")
    "The kind of metric this expression represents"
    model_config = ConfigDict(frozen=True)


class ReagentCategory(
    BaseNodeCategoryReagentCategory,
    BaseCategoryReagentCategory,
    ReagentCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )
    model_config = ConfigDict(frozen=True)


class MeasurementCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class MeasurementCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class MeasurementCategory(
    BaseEdgeCategoryMeasurementCategory,
    BaseCategoryMeasurementCategory,
    MeasurementCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )
    source_definition: MeasurementCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: MeasurementCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    model_config = ConfigDict(frozen=True)


class RelationCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class RelationCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class RelationCategory(
    BaseEdgeCategoryRelationCategory,
    BaseCategoryRelationCategory,
    RelationCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )
    source_definition: RelationCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: RelationCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    model_config = ConfigDict(frozen=True)


class StructureRelationCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class StructureRelationCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class StructureRelationCategory(
    BaseEdgeCategoryStructureRelationCategory,
    BaseCategoryStructureRelationCategory,
    StructureRelationCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )
    source_definition: StructureRelationCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: StructureRelationCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    model_config = ConfigDict(frozen=True)


class EdgeBase(BaseModel):
    """No documentation"""


class EdgeCatch(EdgeBase):
    """Catch all class for EdgeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"


class EdgeMeasurement(BaseEdgeMeasurement, Measurement, EdgeBase, BaseModel):
    """A measurement is an edge from a structure to an entity. Importantly Measurement are always directed from the structure to the entity, and never the other way around."""

    typename: Literal["Measurement"] = Field(
        alias="__typename", default="Measurement", exclude=True
    )


class EdgeRelation(BaseEdgeRelation, Relation, EdgeBase, BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["Relation"] = Field(
        alias="__typename", default="Relation", exclude=True
    )


class EdgeParticipant(BaseEdgeParticipant, Participant, EdgeBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Participant"] = Field(
        alias="__typename", default="Participant", exclude=True
    )


class EdgeDescription(BaseEdgeDescription, EdgeBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Description"] = Field(
        alias="__typename", default="Description", exclude=True
    )


class EdgeStructureRelation(
    BaseEdgeStructureRelation, StructureRelation, EdgeBase, BaseModel
):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["StructureRelation"] = Field(
        alias="__typename", default="StructureRelation", exclude=True
    )


class ListEntityCategory(
    BaseNodeCategoryEntityCategory,
    BaseListCategoryEntityCategory,
    EntityCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )
    instance_kind: InstanceKind = Field(alias="instanceKind")
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ListReagentCategory(
    BaseNodeCategoryReagentCategory,
    BaseListCategoryReagentCategory,
    ReagentCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )
    instance_kind: InstanceKind = Field(alias="instanceKind")
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ListMetricCategory(
    BaseNodeCategoryMetricCategory,
    BaseListCategoryMetricCategory,
    MetricCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )
    label: str
    "The label of the expression"
    metric_kind: MetricKind = Field(alias="metricKind")
    "The kind of metric this expression represents"
    model_config = ConfigDict(frozen=True)


class ListStructureCategory(
    BaseListNodeCategoryStructureCategory,
    BaseListCategoryStructureCategory,
    StructureCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )
    identifier: str
    "The structure that this class represents"
    model_config = ConfigDict(frozen=True)


class ListMeasurementCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListMeasurementCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListMeasurementCategory(
    BaseListEdgeCategoryMeasurementCategory,
    BaseListCategoryMeasurementCategory,
    MeasurementCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )
    source_definition: ListMeasurementCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: ListMeasurementCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ListRelationCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListRelationCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityCategoryDefinition"] = Field(
        alias="__typename", default="EntityCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListRelationCategory(
    BaseListEdgeCategoryRelationCategory,
    BaseListCategoryRelationCategory,
    RelationCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )
    source_definition: ListRelationCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: ListRelationCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class ListStructureRelationCategorySourcedefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListStructureRelationCategoryTargetdefinition(BaseModel):
    """No documentation"""

    typename: Literal["StructureCategoryDefinition"] = Field(
        alias="__typename", default="StructureCategoryDefinition", exclude=True
    )
    tag_filters: Optional[Tuple[str, ...]] = Field(default=None, alias="tagFilters")
    category_filters: Optional[Tuple[ID, ...]] = Field(
        default=None, alias="categoryFilters"
    )
    model_config = ConfigDict(frozen=True)


class ListStructureRelationCategory(
    BaseListEdgeCategoryStructureRelationCategory,
    BaseListCategoryStructureRelationCategory,
    StructureRelationCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )
    source_definition: ListStructureRelationCategorySourcedefinition = Field(
        alias="sourceDefinition"
    )
    "The unique identifier of the expression within its graph"
    target_definition: ListStructureRelationCategoryTargetdefinition = Field(
        alias="targetDefinition"
    )
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class EntityRoleDefinition(BaseModel):
    """No documentation"""

    typename: Literal["EntityRoleDefinition"] = Field(
        alias="__typename", default="EntityRoleDefinition", exclude=True
    )
    role: str
    category_definition: EntityCategoryDefinition = Field(alias="categoryDefinition")
    optional: bool
    allow_multiple: bool = Field(alias="allowMultiple")
    model_config = ConfigDict(frozen=True)


class ReagentRoleDefinition(BaseModel):
    """No documentation"""

    typename: Literal["ReagentRoleDefinition"] = Field(
        alias="__typename", default="ReagentRoleDefinition", exclude=True
    )
    role: str
    category_definition: ReagentCategoryDefinition = Field(alias="categoryDefinition")
    needs_quantity: bool = Field(alias="needsQuantity")
    optional: bool
    model_config = ConfigDict(frozen=True)


class Model(BaseModel):
    """A model represents a trained machine learning model that can be used for analysis."""

    typename: Literal["Model"] = Field(
        alias="__typename", default="Model", exclude=True
    )
    id: ID
    "The unique identifier of the model"
    name: str
    "The name of the model"
    store: Optional[MediaStore] = Field(default=None)
    "Optional file storage location containing the model weights/parameters"
    model_config = ConfigDict(frozen=True)


class NodeBase(NodeTrait, BaseModel):
    """No documentation"""


class NodeCatch(NodeBase):
    """Catch all class for NodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"


class NodeEntity(BaseNodeEntity, Entity, NodeBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class NodeStructure(BaseNodeStructure, Structure, NodeBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class NodeMetric(BaseNodeMetric, Metric, NodeBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class NodeProtocolEvent(BaseNodeProtocolEvent, NodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class NodeNaturalEvent(BaseNodeNaturalEvent, NodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class NodeReagent(BaseNodeReagent, Reagent, NodeBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class TableGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    age_name: str = Field(alias="ageName")
    model_config = ConfigDict(frozen=True)


class Table(BaseModel):
    """A collection of paired entities."""

    typename: Literal["Table"] = Field(
        alias="__typename", default="Table", exclude=True
    )
    graph: TableGraph
    "The graph this table was queried from."
    rows: Tuple[Any, ...]
    "The paired entities."
    columns: Tuple[Column, ...]
    "The columns describind this table."
    model_config = ConfigDict(frozen=True)


class NaturalEventCategoryStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class NaturalEventCategory(
    BaseNodeCategoryNaturalEventCategory,
    BaseCategoryNaturalEventCategory,
    NaturalEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )
    plate_children: Optional[Tuple[Any, ...]] = Field(
        default=None, alias="plateChildren"
    )
    "The children of this plate"
    label: str
    "The label of the expression"
    age_name: str = Field(alias="ageName")
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    description: Optional[str] = Field(default=None)
    "A description of the expression."
    store: Optional[NaturalEventCategoryStore] = Field(default=None)
    "An image or other media file that can be used to represent the expression."
    source_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="sourceEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    target_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="targetEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    model_config = ConfigDict(frozen=True)


class ListNaturalEventCategory(
    BaseNodeCategoryNaturalEventCategory,
    BaseListCategoryNaturalEventCategory,
    NaturalEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )
    label: str
    "The label of the expression"
    source_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="sourceEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    target_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="targetEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    model_config = ConfigDict(frozen=True)


class ProtocolEventCategoryStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ProtocolEventCategory(
    BaseNodeCategoryProtocolEventCategory,
    BaseCategoryProtocolEventCategory,
    ProtocolEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )
    plate_children: Optional[Tuple[Any, ...]] = Field(
        default=None, alias="plateChildren"
    )
    "The children of this plate"
    label: str
    "The label of the expression"
    age_name: str = Field(alias="ageName")
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    description: Optional[str] = Field(default=None)
    "A description of the expression."
    store: Optional[ProtocolEventCategoryStore] = Field(default=None)
    "An image or other media file that can be used to represent the expression."
    source_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="sourceEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    target_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="targetEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    source_reagent_roles: Tuple[ReagentRoleDefinition, ...] = Field(
        alias="sourceReagentRoles"
    )
    "The unique identifier of the expression within its graph"
    target_reagent_roles: Tuple[ReagentRoleDefinition, ...] = Field(
        alias="targetReagentRoles"
    )
    "The unique identifier of the expression within its graph"
    variable_definitions: Tuple[VariableDefinition, ...] = Field(
        alias="variableDefinitions"
    )
    model_config = ConfigDict(frozen=True)


class ListProtocolEventCategory(
    BaseNodeCategoryProtocolEventCategory,
    BaseListCategoryProtocolEventCategory,
    ProtocolEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )
    label: str
    "The label of the expression"
    source_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="sourceEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    target_entity_roles: Tuple[EntityRoleDefinition, ...] = Field(
        alias="targetEntityRoles"
    )
    "The unique identifier of the expression within its graph"
    source_reagent_roles: Tuple[ReagentRoleDefinition, ...] = Field(
        alias="sourceReagentRoles"
    )
    "The unique identifier of the expression within its graph"
    target_reagent_roles: Tuple[ReagentRoleDefinition, ...] = Field(
        alias="targetReagentRoles"
    )
    "The unique identifier of the expression within its graph"
    model_config = ConfigDict(frozen=True)


class DetailNodeGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class DetailNodeBase(NodeTrait, BaseModel):
    """No documentation"""

    graph: DetailNodeGraph
    "The unique identifier of the entity within its graph"


class DetailNodeCatch(DetailNodeBase):
    """Catch all class for DetailNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    graph: DetailNodeGraph
    "The unique identifier of the entity within its graph"


class DetailNodeEntity(NodeEntity, DetailNodeBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class DetailNodeStructure(NodeStructure, DetailNodeBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class DetailNodeMetric(NodeMetric, DetailNodeBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class DetailNodeProtocolEvent(NodeProtocolEvent, DetailNodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class DetailNodeNaturalEvent(NodeNaturalEvent, DetailNodeBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class DetailNodeReagent(NodeReagent, DetailNodeBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class PathNodesBase(NodeTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class PathNodesBaseEntity(NodeEntity, PathNodesBase, EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class PathNodesBaseStructure(NodeStructure, PathNodesBase, StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class PathNodesBaseMetric(NodeMetric, PathNodesBase, MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class PathNodesBaseProtocolEvent(NodeProtocolEvent, PathNodesBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class PathNodesBaseNaturalEvent(NodeNaturalEvent, PathNodesBase, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class PathNodesBaseReagent(NodeReagent, PathNodesBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class PathNodesBaseCatchAll(PathNodesBase, BaseModel):
    """Catch all class for PathNodesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class PathEdgesBase(BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class PathEdgesBaseMeasurement(EdgeMeasurement, PathEdgesBase, BaseModel):
    """A measurement is an edge from a structure to an entity. Importantly Measurement are always directed from the structure to the entity, and never the other way around."""

    typename: Literal["Measurement"] = Field(
        alias="__typename", default="Measurement", exclude=True
    )


class PathEdgesBaseRelation(EdgeRelation, PathEdgesBase, BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["Relation"] = Field(
        alias="__typename", default="Relation", exclude=True
    )


class PathEdgesBaseParticipant(EdgeParticipant, PathEdgesBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Participant"] = Field(
        alias="__typename", default="Participant", exclude=True
    )


class PathEdgesBaseDescription(EdgeDescription, PathEdgesBase, BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Description"] = Field(
        alias="__typename", default="Description", exclude=True
    )


class PathEdgesBaseStructureRelation(EdgeStructureRelation, PathEdgesBase, BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["StructureRelation"] = Field(
        alias="__typename", default="StructureRelation", exclude=True
    )


class PathEdgesBaseCatchAll(PathEdgesBase, BaseModel):
    """Catch all class for PathEdgesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class Path(BaseModel):
    """No documentation"""

    typename: Literal["Path"] = Field(alias="__typename", default="Path", exclude=True)
    nodes: Tuple[
        Union[
            Annotated[
                Union[
                    PathNodesBaseEntity,
                    PathNodesBaseStructure,
                    PathNodesBaseMetric,
                    PathNodesBaseProtocolEvent,
                    PathNodesBaseNaturalEvent,
                    PathNodesBaseReagent,
                ],
                Field(discriminator="typename"),
            ],
            PathNodesBaseCatchAll,
        ],
        ...,
    ]
    edges: Tuple[
        Union[
            Annotated[
                Union[
                    PathEdgesBaseMeasurement,
                    PathEdgesBaseRelation,
                    PathEdgesBaseParticipant,
                    PathEdgesBaseDescription,
                    PathEdgesBaseStructureRelation,
                ],
                Field(discriminator="typename"),
            ],
            PathEdgesBaseCatchAll,
        ],
        ...,
    ]
    model_config = ConfigDict(frozen=True)


class GraphQueryGraph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class GraphQuery(BaseModel):
    """A view of a graph, that contains entities and relations."""

    typename: Literal["GraphQuery"] = Field(
        alias="__typename", default="GraphQuery", exclude=True
    )
    id: ID
    query: str
    name: str
    graph: GraphQueryGraph
    scatter_plots: Tuple[ListScatterPlot, ...] = Field(alias="scatterPlots")
    "The list of metric expressions defined in this ontology"
    render: Union[Path, Pairs, Table]
    pinned: bool
    model_config = ConfigDict(frozen=True)


class EntityCategoryStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class EntityCategory(
    BaseNodeCategoryEntityCategory,
    BaseCategoryEntityCategory,
    EntityCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )
    instance_kind: InstanceKind = Field(alias="instanceKind")
    "The unique identifier of the expression within its graph"
    age_name: str = Field(alias="ageName")
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    description: Optional[str] = Field(default=None)
    "A description of the expression."
    store: Optional[EntityCategoryStore] = Field(default=None)
    "An image or other media file that can be used to represent the expression."
    best_query: Optional[GraphQuery] = Field(default=None, alias="bestQuery")
    model_config = ConfigDict(frozen=True)


class GraphLatestnodesBase(NodeTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class GraphLatestnodesBaseEntity(
    NodeEntity, GraphLatestnodesBase, EntityTrait, BaseModel
):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class GraphLatestnodesBaseStructure(
    NodeStructure, GraphLatestnodesBase, StructureTrait, BaseModel
):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class GraphLatestnodesBaseMetric(
    NodeMetric, GraphLatestnodesBase, MetricTrait, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class GraphLatestnodesBaseProtocolEvent(
    NodeProtocolEvent, GraphLatestnodesBase, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class GraphLatestnodesBaseNaturalEvent(
    NodeNaturalEvent, GraphLatestnodesBase, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class GraphLatestnodesBaseReagent(NodeReagent, GraphLatestnodesBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class GraphLatestnodesBaseCatchAll(GraphLatestnodesBase, BaseModel):
    """Catch all class for GraphLatestnodesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class Graph(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)
    structure_categories: Tuple[ListStructureCategory, ...] = Field(
        alias="structureCategories"
    )
    "The list of structure expressions defined in this ontology"
    entity_categories: Tuple[ListEntityCategory, ...] = Field(alias="entityCategories")
    "The list of generic expressions defined in this ontology"
    metric_categories: Tuple[ListMetricCategory, ...] = Field(alias="metricCategories")
    "The list of metric expressions defined in this ontology"
    protocol_event_categories: Tuple[ListProtocolEventCategory, ...] = Field(
        alias="protocolEventCategories"
    )
    "The list of step expressions defined in this ontology"
    natural_event_categories: Tuple[ListNaturalEventCategory, ...] = Field(
        alias="naturalEventCategories"
    )
    "The list of step expressions defined in this ontology"
    relation_categories: Tuple[ListRelationCategory, ...] = Field(
        alias="relationCategories"
    )
    "The list of relation expressions defined in this ontology"
    measurement_categories: Tuple[ListMeasurementCategory, ...] = Field(
        alias="measurementCategories"
    )
    "The list of measurement exprdessions defined in this ontology"
    structure_relation_categories: Tuple[ListStructureRelationCategory, ...] = Field(
        alias="structureRelationCategories"
    )
    "The list of structure relation expressions defined in this ontology"
    graph_queries: Tuple[GraphQuery, ...] = Field(alias="graphQueries")
    "The list of metric expressions defined in this ontology"
    latest_nodes: Tuple[
        Union[
            Annotated[
                Union[
                    GraphLatestnodesBaseEntity,
                    GraphLatestnodesBaseStructure,
                    GraphLatestnodesBaseMetric,
                    GraphLatestnodesBaseProtocolEvent,
                    GraphLatestnodesBaseNaturalEvent,
                    GraphLatestnodesBaseReagent,
                ],
                Field(discriminator="typename"),
            ],
            GraphLatestnodesBaseCatchAll,
        ],
        ...,
    ] = Field(alias="latestNodes")
    model_config = ConfigDict(frozen=True)


class NodeCategoryBase(NodeCategoryTrait, BaseModel):
    """No documentation"""


class NodeCategoryCatch(NodeCategoryBase):
    """Catch all class for NodeCategoryBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"


class NodeCategoryMetricCategory(
    MetricCategory, NodeCategoryBase, MetricCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class NodeCategoryStructureCategory(
    StructureCategory, NodeCategoryBase, StructureCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class NodeCategoryProtocolEventCategory(
    ProtocolEventCategory, NodeCategoryBase, ProtocolEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class NodeCategoryEntityCategory(
    EntityCategory, NodeCategoryBase, EntityCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class NodeCategoryReagentCategory(
    ReagentCategory, NodeCategoryBase, ReagentCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class NodeCategoryNaturalEventCategory(
    NaturalEventCategory, NodeCategoryBase, NaturalEventCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class CreateMeasurementCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_measurement_category: MeasurementCategory = Field(
        alias="createMeasurementCategory"
    )
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateMeasurementCategory"""

        input: MeasurementCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateMeasurementCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MeasurementCategory on MeasurementCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nmutation CreateMeasurementCategory($input: MeasurementCategoryInput!) {\n  createMeasurementCategory(input: $input) {\n    ...MeasurementCategory\n    __typename\n  }\n}"


class CreateMetricCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_metric_category: MetricCategory = Field(alias="createMetricCategory")
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateMetricCategory"""

        input: MetricCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateMetricCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MetricCategory on MetricCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  metricKind\n  __typename\n}\n\nmutation CreateMetricCategory($input: MetricCategoryInput!) {\n  createMetricCategory(input: $input) {\n    ...MetricCategory\n    __typename\n  }\n}"


class CreateReagentCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_reagent_category: ReagentCategory = Field(alias="createReagentCategory")
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateReagentCategory"""

        input: ReagentCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateReagentCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentCategory on ReagentCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  __typename\n}\n\nmutation CreateReagentCategory($input: ReagentCategoryInput!) {\n  createReagentCategory(input: $input) {\n    ...ReagentCategory\n    __typename\n  }\n}"


class CreateRelationCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_relation_category: RelationCategory = Field(alias="createRelationCategory")
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateRelationCategory"""

        input: RelationCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment RelationCategory on RelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nmutation CreateRelationCategory($input: RelationCategoryInput!) {\n  createRelationCategory(input: $input) {\n    ...RelationCategory\n    __typename\n  }\n}"


class CreateEntityMutation(BaseModel):
    """No documentation found for this operation."""

    create_entity: Entity = Field(alias="createEntity")
    "Create a new entity"

    class Arguments(BaseModel):
        """Arguments for CreateEntity"""

        input: EntityInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateEntity"""

        document = "fragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nmutation CreateEntity($input: EntityInput!) {\n  createEntity(input: $input) {\n    ...Entity\n    __typename\n  }\n}"


class CreateEntityCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_entity_category: EntityCategory = Field(alias="createEntityCategory")
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateEntityCategory"""

        input: EntityCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateEntityCategory"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment EntityCategory on EntityCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  instanceKind\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  bestQuery {\n    ...GraphQuery\n    __typename\n  }\n  __typename\n}\n\nmutation CreateEntityCategory($input: EntityCategoryInput!) {\n  createEntityCategory(input: $input) {\n    ...EntityCategory\n    __typename\n  }\n}"


class UpdateEntityCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    update_entity_category: EntityCategory = Field(alias="updateEntityCategory")
    "Update an existing expression"

    class Arguments(BaseModel):
        """Arguments for UpdateEntityCategory"""

        input: UpdateEntityCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateEntityCategory"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment EntityCategory on EntityCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  instanceKind\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  bestQuery {\n    ...GraphQuery\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateEntityCategory($input: UpdateEntityCategoryInput!) {\n  updateEntityCategory(input: $input) {\n    ...EntityCategory\n    __typename\n  }\n}"


class CreateGraphMutation(BaseModel):
    """No documentation found for this operation."""

    create_graph: Graph = Field(alias="createGraph")
    "Create a new graph"

    class Arguments(BaseModel):
        """Arguments for CreateGraph"""

        input: GraphInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateGraph"""

        document = "fragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment BaseListNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ListProtocolEventCategory on ProtocolEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListRelationCategory on RelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureRelationCategory on StructureRelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureCategory on StructureCategory {\n  ...BaseListCategory\n  ...BaseListNodeCategory\n  identifier\n  __typename\n}\n\nfragment ListMetricCategory on MetricCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  metricKind\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment ListNaturalEventCategory on NaturalEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment Graph on Graph {\n  id\n  name\n  description\n  structureCategories {\n    ...ListStructureCategory\n    __typename\n  }\n  entityCategories {\n    ...ListEntityCategory\n    __typename\n  }\n  metricCategories {\n    ...ListMetricCategory\n    __typename\n  }\n  protocolEventCategories {\n    ...ListProtocolEventCategory\n    __typename\n  }\n  naturalEventCategories {\n    ...ListNaturalEventCategory\n    __typename\n  }\n  relationCategories {\n    ...ListRelationCategory\n    __typename\n  }\n  measurementCategories {\n    ...ListMeasurementCategory\n    __typename\n  }\n  structureRelationCategories {\n    ...ListStructureRelationCategory\n    __typename\n  }\n  graphQueries(pagination: {limit: 0}) {\n    ...GraphQuery\n    __typename\n  }\n  latestNodes(pagination: {limit: 2}) {\n    ...Node\n    __typename\n  }\n  __typename\n}\n\nmutation CreateGraph($input: GraphInput!) {\n  createGraph(input: $input) {\n    ...Graph\n    __typename\n  }\n}"


class PinGraphMutation(BaseModel):
    """No documentation found for this operation."""

    pin_graph: Graph = Field(alias="pinGraph")
    "Pin or unpin a graph"

    class Arguments(BaseModel):
        """Arguments for PinGraph"""

        input: PinGraphInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for PinGraph"""

        document = "fragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment BaseListNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ListProtocolEventCategory on ProtocolEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListRelationCategory on RelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureRelationCategory on StructureRelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureCategory on StructureCategory {\n  ...BaseListCategory\n  ...BaseListNodeCategory\n  identifier\n  __typename\n}\n\nfragment ListMetricCategory on MetricCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  metricKind\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment ListNaturalEventCategory on NaturalEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment Graph on Graph {\n  id\n  name\n  description\n  structureCategories {\n    ...ListStructureCategory\n    __typename\n  }\n  entityCategories {\n    ...ListEntityCategory\n    __typename\n  }\n  metricCategories {\n    ...ListMetricCategory\n    __typename\n  }\n  protocolEventCategories {\n    ...ListProtocolEventCategory\n    __typename\n  }\n  naturalEventCategories {\n    ...ListNaturalEventCategory\n    __typename\n  }\n  relationCategories {\n    ...ListRelationCategory\n    __typename\n  }\n  measurementCategories {\n    ...ListMeasurementCategory\n    __typename\n  }\n  structureRelationCategories {\n    ...ListStructureRelationCategory\n    __typename\n  }\n  graphQueries(pagination: {limit: 0}) {\n    ...GraphQuery\n    __typename\n  }\n  latestNodes(pagination: {limit: 2}) {\n    ...Node\n    __typename\n  }\n  __typename\n}\n\nmutation PinGraph($input: PinGraphInput!) {\n  pinGraph(input: $input) {\n    ...Graph\n    __typename\n  }\n}"


class DeleteGraphMutation(BaseModel):
    """No documentation found for this operation."""

    delete_graph: ID = Field(alias="deleteGraph")
    "Delete an existing graph"

    class Arguments(BaseModel):
        """Arguments for DeleteGraph"""

        input: DeleteGraphInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DeleteGraph"""

        document = "mutation DeleteGraph($input: DeleteGraphInput!) {\n  deleteGraph(input: $input)\n}"


class UpdateGraphMutation(BaseModel):
    """No documentation found for this operation."""

    update_graph: Graph = Field(alias="updateGraph")
    "Update an existing graph"

    class Arguments(BaseModel):
        """Arguments for UpdateGraph"""

        input: UpdateGraphInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateGraph"""

        document = "fragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment BaseListNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ListProtocolEventCategory on ProtocolEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListRelationCategory on RelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureRelationCategory on StructureRelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureCategory on StructureCategory {\n  ...BaseListCategory\n  ...BaseListNodeCategory\n  identifier\n  __typename\n}\n\nfragment ListMetricCategory on MetricCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  metricKind\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment ListNaturalEventCategory on NaturalEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment Graph on Graph {\n  id\n  name\n  description\n  structureCategories {\n    ...ListStructureCategory\n    __typename\n  }\n  entityCategories {\n    ...ListEntityCategory\n    __typename\n  }\n  metricCategories {\n    ...ListMetricCategory\n    __typename\n  }\n  protocolEventCategories {\n    ...ListProtocolEventCategory\n    __typename\n  }\n  naturalEventCategories {\n    ...ListNaturalEventCategory\n    __typename\n  }\n  relationCategories {\n    ...ListRelationCategory\n    __typename\n  }\n  measurementCategories {\n    ...ListMeasurementCategory\n    __typename\n  }\n  structureRelationCategories {\n    ...ListStructureRelationCategory\n    __typename\n  }\n  graphQueries(pagination: {limit: 0}) {\n    ...GraphQuery\n    __typename\n  }\n  latestNodes(pagination: {limit: 2}) {\n    ...Node\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateGraph($input: UpdateGraphInput!) {\n  updateGraph(input: $input) {\n    ...Graph\n    __typename\n  }\n}"


class CreateGraphQueryMutation(BaseModel):
    """No documentation found for this operation."""

    create_graph_query: GraphQuery = Field(alias="createGraphQuery")
    "Create a new graph query"

    class Arguments(BaseModel):
        """Arguments for CreateGraphQuery"""

        input: GraphQueryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateGraphQuery"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nmutation CreateGraphQuery($input: GraphQueryInput!) {\n  createGraphQuery(input: $input) {\n    ...GraphQuery\n    __typename\n  }\n}"


class PinGraphQueryMutation(BaseModel):
    """No documentation found for this operation."""

    pin_graph_query: GraphQuery = Field(alias="pinGraphQuery")
    "Pin or unpin a graph query"

    class Arguments(BaseModel):
        """Arguments for PinGraphQuery"""

        input: PinGraphQueryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for PinGraphQuery"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nmutation PinGraphQuery($input: PinGraphQueryInput!) {\n  pinGraphQuery(input: $input) {\n    ...GraphQuery\n    __typename\n  }\n}"


class CreateMeasurementMutation(BaseModel):
    """No documentation found for this operation."""

    create_measurement: Measurement = Field(alias="createMeasurement")
    "Create a new measurement edge"

    class Arguments(BaseModel):
        """Arguments for CreateMeasurement"""

        input: MeasurementInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateMeasurement"""

        document = "fragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nmutation CreateMeasurement($input: MeasurementInput!) {\n  createMeasurement(input: $input) {\n    ...Measurement\n    __typename\n  }\n}"


class CreateMetricMutation(BaseModel):
    """No documentation found for this operation."""

    create_metric: Metric = Field(alias="createMetric")
    "Create a new metric for an entity"

    class Arguments(BaseModel):
        """Arguments for CreateMetric"""

        input: MetricInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateMetric"""

        document = "fragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nmutation CreateMetric($input: MetricInput!) {\n  createMetric(input: $input) {\n    ...Metric\n    __typename\n  }\n}"


class CreateModelMutation(BaseModel):
    """No documentation found for this operation."""

    create_model: Model = Field(alias="createModel")
    "Create a new model"

    class Arguments(BaseModel):
        """Arguments for CreateModel"""

        input: CreateModelInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateModel"""

        document = "fragment MediaStore on MediaStore {\n  id\n  presignedUrl\n  key\n  __typename\n}\n\nfragment Model on Model {\n  id\n  name\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}\n\nmutation CreateModel($input: CreateModelInput!) {\n  createModel(input: $input) {\n    ...Model\n    __typename\n  }\n}"


class RecordNaturalEventMutation(BaseModel):
    """No documentation found for this operation."""

    record_natural_event: NaturalEvent = Field(alias="recordNaturalEvent")
    "Record a new natural event"

    class Arguments(BaseModel):
        """Arguments for RecordNaturalEvent"""

        input: RecordNaturalEventInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RecordNaturalEvent"""

        document = "fragment NaturalEvent on NaturalEvent {\n  id\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nmutation RecordNaturalEvent($input: RecordNaturalEventInput!) {\n  recordNaturalEvent(input: $input) {\n    ...NaturalEvent\n    __typename\n  }\n}"


class CreateNaturalEventCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_natural_event_category: NaturalEventCategory = Field(
        alias="createNaturalEventCategory"
    )
    "Create a new natural event category"

    class Arguments(BaseModel):
        """Arguments for CreateNaturalEventCategory"""

        input: NaturalEventCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateNaturalEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment NaturalEventCategory on NaturalEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nmutation CreateNaturalEventCategory($input: NaturalEventCategoryInput!) {\n  createNaturalEventCategory(input: $input) {\n    ...NaturalEventCategory\n    __typename\n  }\n}"


class UpdateNaturalEventCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    update_natural_event_category: NaturalEventCategory = Field(
        alias="updateNaturalEventCategory"
    )
    "Update an existing natural event category"

    class Arguments(BaseModel):
        """Arguments for UpdateNaturalEventCategory"""

        input: UpdateNaturalEventCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateNaturalEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment NaturalEventCategory on NaturalEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateNaturalEventCategory($input: UpdateNaturalEventCategoryInput!) {\n  updateNaturalEventCategory(input: $input) {\n    ...NaturalEventCategory\n    __typename\n  }\n}"


class CreateNodeQueryMutation(BaseModel):
    """No documentation found for this operation."""

    create_node_query: NodeQuery = Field(alias="createNodeQuery")
    "Create a new node query"

    class Arguments(BaseModel):
        """Arguments for CreateNodeQuery"""

        input: NodeQueryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateNodeQuery"""

        document = "fragment NodeQuery on NodeQuery {\n  id\n  name\n  pinned\n  __typename\n}\n\nmutation CreateNodeQuery($input: NodeQueryInput!) {\n  createNodeQuery(input: $input) {\n    ...NodeQuery\n    __typename\n  }\n}"


class PinNodeQueryMutation(BaseModel):
    """No documentation found for this operation."""

    pin_node_query: NodeQuery = Field(alias="pinNodeQuery")
    "Pin or unpin a node query"

    class Arguments(BaseModel):
        """Arguments for PinNodeQuery"""

        input: PinNodeQueryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for PinNodeQuery"""

        document = "fragment NodeQuery on NodeQuery {\n  id\n  name\n  pinned\n  __typename\n}\n\nmutation PinNodeQuery($input: PinNodeQueryInput!) {\n  pinNodeQuery(input: $input) {\n    ...NodeQuery\n    __typename\n  }\n}"


class RecordProtocolEventMutation(BaseModel):
    """No documentation found for this operation."""

    record_protocol_event: ProtocolEvent = Field(alias="recordProtocolEvent")
    "Record a new protocol event"

    class Arguments(BaseModel):
        """Arguments for RecordProtocolEvent"""

        input: RecordProtocolEventInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RecordProtocolEvent"""

        document = "fragment ProtocolEvent on ProtocolEvent {\n  id\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nmutation RecordProtocolEvent($input: RecordProtocolEventInput!) {\n  recordProtocolEvent(input: $input) {\n    ...ProtocolEvent\n    __typename\n  }\n}"


class CreateProtocolEventCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_protocol_event_category: ProtocolEventCategory = Field(
        alias="createProtocolEventCategory"
    )
    "Create a new protocol event category"

    class Arguments(BaseModel):
        """Arguments for CreateProtocolEventCategory"""

        input: ProtocolEventCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateProtocolEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment VariableDefinition on VariableDefinition {\n  param\n  valueKind\n  default\n  optional\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ProtocolEventCategory on ProtocolEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  variableDefinitions {\n    ...VariableDefinition\n    __typename\n  }\n  __typename\n}\n\nmutation CreateProtocolEventCategory($input: ProtocolEventCategoryInput!) {\n  createProtocolEventCategory(input: $input) {\n    ...ProtocolEventCategory\n    __typename\n  }\n}"


class UpdateProtocolEventCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    update_protocol_event_category: ProtocolEventCategory = Field(
        alias="updateProtocolEventCategory"
    )
    "Update an existing protocol event category"

    class Arguments(BaseModel):
        """Arguments for UpdateProtocolEventCategory"""

        input: UpdateProtocolEventCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateProtocolEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment VariableDefinition on VariableDefinition {\n  param\n  valueKind\n  default\n  optional\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ProtocolEventCategory on ProtocolEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  variableDefinitions {\n    ...VariableDefinition\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateProtocolEventCategory($input: UpdateProtocolEventCategoryInput!) {\n  updateProtocolEventCategory(input: $input) {\n    ...ProtocolEventCategory\n    __typename\n  }\n}"


class CreateReagentMutation(BaseModel):
    """No documentation found for this operation."""

    create_reagent: Reagent = Field(alias="createReagent")
    "Create a new entity"

    class Arguments(BaseModel):
        """Arguments for CreateReagent"""

        input: ReagentInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateReagent"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nmutation CreateReagent($input: ReagentInput!) {\n  createReagent(input: $input) {\n    ...Reagent\n    __typename\n  }\n}"


class CreateRelationMutation(BaseModel):
    """No documentation found for this operation."""

    create_relation: Relation = Field(alias="createRelation")
    "Create a new relation between entities"

    class Arguments(BaseModel):
        """Arguments for CreateRelation"""

        input: RelationInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateRelation"""

        document = "fragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nmutation CreateRelation($input: RelationInput!) {\n  createRelation(input: $input) {\n    ...Relation\n    __typename\n  }\n}"


class CreateScatterPlotMutation(BaseModel):
    """No documentation found for this operation."""

    create_scatter_plot: ScatterPlot = Field(alias="createScatterPlot")
    "Create a new scatter plot"

    class Arguments(BaseModel):
        """Arguments for CreateScatterPlot"""

        input: ScatterPlotInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateScatterPlot"""

        document = "fragment ScatterPlot on ScatterPlot {\n  id\n  name\n  description\n  xColumn\n  yColumn\n  __typename\n}\n\nmutation CreateScatterPlot($input: ScatterPlotInput!) {\n  createScatterPlot(input: $input) {\n    ...ScatterPlot\n    __typename\n  }\n}"


class DeleteScatterPlotMutation(BaseModel):
    """No documentation found for this operation."""

    delete_scatter_plot: ID = Field(alias="deleteScatterPlot")
    "Delete an existing scatter plot"

    class Arguments(BaseModel):
        """Arguments for DeleteScatterPlot"""

        input: DeleteScatterPlotInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DeleteScatterPlot"""

        document = "mutation DeleteScatterPlot($input: DeleteScatterPlotInput!) {\n  deleteScatterPlot(input: $input)\n}"


class CreateStructureMutation(BaseModel):
    """No documentation found for this operation."""

    create_structure: Structure = Field(alias="createStructure")
    "Create a new structure"

    class Arguments(BaseModel):
        """Arguments for CreateStructure"""

        input: StructureInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateStructure"""

        document = "fragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nmutation CreateStructure($input: StructureInput!) {\n  createStructure(input: $input) {\n    ...Structure\n    __typename\n  }\n}"


class CreateStructureCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_structure_category: StructureCategory = Field(
        alias="createStructureCategory"
    )
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateStructureCategory"""

        input: StructureCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateStructureCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureCategory on StructureCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  identifier\n  __typename\n}\n\nmutation CreateStructureCategory($input: StructureCategoryInput!) {\n  createStructureCategory(input: $input) {\n    ...StructureCategory\n    __typename\n  }\n}"


class UpdateStructureCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    update_structure_category: StructureCategory = Field(
        alias="updateStructureCategory"
    )
    "Update an existing expression"

    class Arguments(BaseModel):
        """Arguments for UpdateStructureCategory"""

        input: UpdateStructureCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateStructureCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureCategory on StructureCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  identifier\n  __typename\n}\n\nmutation UpdateStructureCategory($input: UpdateStructureCategoryInput!) {\n  updateStructureCategory(input: $input) {\n    ...StructureCategory\n    __typename\n  }\n}"


class CreateStructureRelationMutation(BaseModel):
    """No documentation found for this operation."""

    create_structure_relation: StructureRelation = Field(
        alias="createStructureRelation"
    )
    "Create a new relation between entities"

    class Arguments(BaseModel):
        """Arguments for CreateStructureRelation"""

        input: StructureRelationInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateStructureRelation"""

        document = "fragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nmutation CreateStructureRelation($input: StructureRelationInput!) {\n  createStructureRelation(input: $input) {\n    ...StructureRelation\n    __typename\n  }\n}"


class CreateStructureRelationCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    create_structure_relation_category: StructureRelationCategory = Field(
        alias="createStructureRelationCategory"
    )
    "Create a new expression"

    class Arguments(BaseModel):
        """Arguments for CreateStructureRelationCategory"""

        input: StructureRelationCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateStructureRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelationCategory on StructureRelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nmutation CreateStructureRelationCategory($input: StructureRelationCategoryInput!) {\n  createStructureRelationCategory(input: $input) {\n    ...StructureRelationCategory\n    __typename\n  }\n}"


class UpdateStructureRelationCategoryMutation(BaseModel):
    """No documentation found for this operation."""

    update_structure_relation_category: StructureRelationCategory = Field(
        alias="updateStructureRelationCategory"
    )
    "Update an existing expression"

    class Arguments(BaseModel):
        """Arguments for UpdateStructureRelationCategory"""

        input: UpdateStructureRelationCategoryInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateStructureRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelationCategory on StructureRelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateStructureRelationCategory($input: UpdateStructureRelationCategoryInput!) {\n  updateStructureRelationCategory(input: $input) {\n    ...StructureRelationCategory\n    __typename\n  }\n}"


class CreateToldyousoMutation(BaseModel):
    """No documentation found for this operation."""

    create_toldyouso: Structure = Field(alias="createToldyouso")
    "Create a new 'told you so' supporting structure"

    class Arguments(BaseModel):
        """Arguments for CreateToldyouso"""

        input: ToldYouSoInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateToldyouso"""

        document = "fragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nmutation CreateToldyouso($input: ToldYouSoInput!) {\n  createToldyouso(input: $input) {\n    ...Structure\n    __typename\n  }\n}"


class RequestUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_upload: PresignedPostCredentials = Field(alias="requestUpload")
    "Request a new file upload"

    class Arguments(BaseModel):
        """Arguments for RequestUpload"""

        input: RequestMediaUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestUpload"""

        document = "fragment PresignedPostCredentials on PresignedPostCredentials {\n  key\n  xAmzCredential\n  xAmzAlgorithm\n  xAmzDate\n  xAmzSignature\n  policy\n  datalayer\n  bucket\n  store\n  __typename\n}\n\nmutation RequestUpload($input: RequestMediaUploadInput!) {\n  requestUpload(input: $input) {\n    ...PresignedPostCredentials\n    __typename\n  }\n}"


class GetEntityQuery(BaseModel):
    """No documentation found for this operation."""

    entity: Entity

    class Arguments(BaseModel):
        """Arguments for GetEntity"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetEntity"""

        document = "fragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nquery GetEntity($id: ID!) {\n  entity(id: $id) {\n    ...Entity\n    __typename\n  }\n}"


class GetEntityForCategoryAndExternalIDQuery(BaseModel):
    """No documentation found for this operation."""

    get_entity_by_category_and_external_id: Entity = Field(
        alias="getEntityByCategoryAndExternalId"
    )

    class Arguments(BaseModel):
        """Arguments for GetEntityForCategoryAndExternalID"""

        category: ID
        external_id: str = Field(alias="externalId")
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetEntityForCategoryAndExternalID"""

        document = "fragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nquery GetEntityForCategoryAndExternalID($category: ID!, $externalId: String!) {\n  getEntityByCategoryAndExternalId(category: $category, externalId: $externalId) {\n    ...Entity\n    __typename\n  }\n}"


class SearchEntitiesQueryOptions(EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchEntitiesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchEntitiesQueryOptions, ...]
    "List of all entities in the system"

    class Arguments(BaseModel):
        """Arguments for SearchEntities"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchEntities"""

        document = "query SearchEntities($search: String, $values: [ID!]) {\n  options: nodes(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListEntitiesQuery(BaseModel):
    """No documentation found for this operation."""

    entities: Tuple[ListEntity, ...]

    class Arguments(BaseModel):
        """Arguments for ListEntities"""

        filters: Optional[EntityFilter] = Field(default=None)
        pagination: Optional[GraphPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListEntities"""

        document = "fragment ListEntity on Entity {\n  id\n  label\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nquery ListEntities($filters: EntityFilter, $pagination: GraphPaginationInput) {\n  entities(filters: $filters, pagination: $pagination) {\n    ...ListEntity\n    __typename\n  }\n}"


class GetEntityCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    entity_category: EntityCategory = Field(alias="entityCategory")

    class Arguments(BaseModel):
        """Arguments for GetEntityCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetEntityCategory"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment EntityCategory on EntityCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  instanceKind\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  bestQuery {\n    ...GraphQuery\n    __typename\n  }\n  __typename\n}\n\nquery GetEntityCategory($id: ID!) {\n  entityCategory(id: $id) {\n    ...EntityCategory\n    __typename\n  }\n}"


class SearchEntityCategoryQueryOptions(EntityCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchEntityCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchEntityCategoryQueryOptions, ...]
    "List of all generic categories"

    class Arguments(BaseModel):
        """Arguments for SearchEntityCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchEntityCategory"""

        document = "query SearchEntityCategory($search: String, $values: [ID!]) {\n  options: entityCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListEntityCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    entity_categories: Tuple[ListEntityCategory, ...] = Field(alias="entityCategories")
    "List of all generic categories"

    class Arguments(BaseModel):
        """Arguments for ListEntityCategory"""

        filters: Optional[EntityCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListEntityCategory"""

        document = "fragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nquery ListEntityCategory($filters: EntityCategoryFilter, $pagination: OffsetPaginationInput) {\n  entityCategories(filters: $filters, pagination: $pagination) {\n    ...ListEntityCategory\n    __typename\n  }\n}"


class GlobalSearchQuery(BaseModel):
    """No documentation found for this operation."""

    entity_categories: Tuple[ListEntityCategory, ...] = Field(alias="entityCategories")
    "List of all generic categories"
    relation_categories: Tuple[ListRelationCategory, ...] = Field(
        alias="relationCategories"
    )
    "List of all relation categories"
    measurement_categories: Tuple[ListMeasurementCategory, ...] = Field(
        alias="measurementCategories"
    )
    "List of all measurement categories"
    structure_categories: Tuple[ListStructureCategory, ...] = Field(
        alias="structureCategories"
    )
    "List of all structure categories"

    class Arguments(BaseModel):
        """Arguments for GlobalSearch"""

        search: str
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GlobalSearch"""

        document = "fragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseListNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment ListRelationCategory on RelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureCategory on StructureCategory {\n  ...BaseListCategory\n  ...BaseListNodeCategory\n  identifier\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nquery GlobalSearch($search: String!) {\n  entityCategories(filters: {search: $search}, pagination: {limit: 10}) {\n    ...ListEntityCategory\n    __typename\n  }\n  relationCategories(filters: {search: $search}, pagination: {limit: 10}) {\n    ...ListRelationCategory\n    __typename\n  }\n  measurementCategories(filters: {search: $search}, pagination: {limit: 10}) {\n    ...ListMeasurementCategory\n    __typename\n  }\n  structureCategories(filters: {search: $search}, pagination: {limit: 10}) {\n    ...ListStructureCategory\n    __typename\n  }\n}"


class GetGraphQuery(BaseModel):
    """No documentation found for this operation."""

    graph: Graph

    class Arguments(BaseModel):
        """Arguments for GetGraph"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetGraph"""

        document = "fragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment BaseListNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ListProtocolEventCategory on ProtocolEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListRelationCategory on RelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureRelationCategory on StructureRelationCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment ListStructureCategory on StructureCategory {\n  ...BaseListCategory\n  ...BaseListNodeCategory\n  identifier\n  __typename\n}\n\nfragment ListMetricCategory on MetricCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  metricKind\n  __typename\n}\n\nfragment ListEntityCategory on EntityCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment ListNaturalEventCategory on NaturalEventCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  label\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment Graph on Graph {\n  id\n  name\n  description\n  structureCategories {\n    ...ListStructureCategory\n    __typename\n  }\n  entityCategories {\n    ...ListEntityCategory\n    __typename\n  }\n  metricCategories {\n    ...ListMetricCategory\n    __typename\n  }\n  protocolEventCategories {\n    ...ListProtocolEventCategory\n    __typename\n  }\n  naturalEventCategories {\n    ...ListNaturalEventCategory\n    __typename\n  }\n  relationCategories {\n    ...ListRelationCategory\n    __typename\n  }\n  measurementCategories {\n    ...ListMeasurementCategory\n    __typename\n  }\n  structureRelationCategories {\n    ...ListStructureRelationCategory\n    __typename\n  }\n  graphQueries(pagination: {limit: 0}) {\n    ...GraphQuery\n    __typename\n  }\n  latestNodes(pagination: {limit: 2}) {\n    ...Node\n    __typename\n  }\n  __typename\n}\n\nquery GetGraph($id: ID!) {\n  graph(id: $id) {\n    ...Graph\n    __typename\n  }\n}"


class SearchGraphsQueryOptions(GraphTrait, BaseModel):
    """A graph, that contains entities and relations."""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchGraphsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchGraphsQueryOptions, ...]
    "List of all knowledge graphs"

    class Arguments(BaseModel):
        """Arguments for SearchGraphs"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchGraphs"""

        document = "query SearchGraphs($search: String, $values: [ID!]) {\n  options: graphs(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListGraphsQuery(BaseModel):
    """No documentation found for this operation."""

    graphs: Tuple[ListGraph, ...]
    "List of all knowledge graphs"

    class Arguments(BaseModel):
        """Arguments for ListGraphs"""

        filters: Optional[GraphFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListGraphs"""

        document = "fragment ListGraph on Graph {\n  id\n  name\n  description\n  pinned\n  __typename\n}\n\nquery ListGraphs($filters: GraphFilter, $pagination: OffsetPaginationInput) {\n  graphs(filters: $filters, pagination: $pagination) {\n    ...ListGraph\n    __typename\n  }\n}"


class GetGraphQueryQuery(BaseModel):
    """No documentation found for this operation."""

    graph_query: GraphQuery = Field(alias="graphQuery")

    class Arguments(BaseModel):
        """Arguments for GetGraphQuery"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetGraphQuery"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nquery GetGraphQuery($id: ID!) {\n  graphQuery(id: $id) {\n    ...GraphQuery\n    __typename\n  }\n}"


class SearchGraphQueriesQueryOptions(BaseModel):
    """A view of a graph, that contains entities and relations."""

    typename: Literal["GraphQuery"] = Field(
        alias="__typename", default="GraphQuery", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchGraphQueriesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchGraphQueriesQueryOptions, ...]
    "List of all graph queries"

    class Arguments(BaseModel):
        """Arguments for SearchGraphQueries"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchGraphQueries"""

        document = "query SearchGraphQueries($search: String, $values: [ID!]) {\n  options: graphQueries(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListGraphQueriesQuery(BaseModel):
    """No documentation found for this operation."""

    graph_queries: Tuple[ListGraphQuery, ...] = Field(alias="graphQueries")
    "List of all graph queries"

    class Arguments(BaseModel):
        """Arguments for ListGraphQueries"""

        filters: Optional[GraphQueryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListGraphQueries"""

        document = "fragment ListGraphQuery on GraphQuery {\n  id\n  name\n  query\n  description\n  pinned\n  __typename\n}\n\nquery ListGraphQueries($filters: GraphQueryFilter, $pagination: OffsetPaginationInput) {\n  graphQueries(filters: $filters, pagination: $pagination) {\n    ...ListGraphQuery\n    __typename\n  }\n}"


class ListPrerenderedGraphQueriesQuery(BaseModel):
    """No documentation found for this operation."""

    graph_queries: Tuple[GraphQuery, ...] = Field(alias="graphQueries")
    "List of all graph queries"

    class Arguments(BaseModel):
        """Arguments for ListPrerenderedGraphQueries"""

        filters: Optional[GraphQueryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListPrerenderedGraphQueries"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nquery ListPrerenderedGraphQueries($filters: GraphQueryFilter, $pagination: OffsetPaginationInput) {\n  graphQueries(filters: $filters, pagination: $pagination) {\n    ...GraphQuery\n    __typename\n  }\n}"


class GetMeasurementQuery(BaseModel):
    """No documentation found for this operation."""

    measurement: Measurement

    class Arguments(BaseModel):
        """Arguments for GetMeasurement"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetMeasurement"""

        document = "fragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nquery GetMeasurement($id: ID!) {\n  measurement(id: $id) {\n    ...Measurement\n    __typename\n  }\n}"


class SearchMeasurementsQueryOptions(BaseModel):
    """A measurement is an edge from a structure to an entity. Importantly Measurement are always directed from the structure to the entity, and never the other way around."""

    typename: Literal["Measurement"] = Field(
        alias="__typename", default="Measurement", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchMeasurementsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchMeasurementsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchMeasurements"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchMeasurements"""

        document = "query SearchMeasurements($search: String, $values: [ID!]) {\n  options: measurements(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetMeasurmentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    measurement_category: MeasurementCategory = Field(alias="measurementCategory")

    class Arguments(BaseModel):
        """Arguments for GetMeasurmentCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetMeasurmentCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MeasurementCategory on MeasurementCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nquery GetMeasurmentCategory($id: ID!) {\n  measurementCategory(id: $id) {\n    ...MeasurementCategory\n    __typename\n  }\n}"


class SearchMeasurmentCategoryQueryOptions(MeasurementCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["MeasurementCategory"] = Field(
        alias="__typename", default="MeasurementCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchMeasurmentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchMeasurmentCategoryQueryOptions, ...]
    "List of all measurement categories"

    class Arguments(BaseModel):
        """Arguments for SearchMeasurmentCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchMeasurmentCategory"""

        document = "query SearchMeasurmentCategory($search: String, $values: [ID!]) {\n  options: measurementCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListMeasurmentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    measurement_categories: Tuple[ListMeasurementCategory, ...] = Field(
        alias="measurementCategories"
    )
    "List of all measurement categories"

    class Arguments(BaseModel):
        """Arguments for ListMeasurmentCategory"""

        filters: Optional[MeasurementCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListMeasurmentCategory"""

        document = "fragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment BaseListEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment ListMeasurementCategory on MeasurementCategory {\n  ...BaseListCategory\n  ...BaseListEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  label\n  __typename\n}\n\nquery ListMeasurmentCategory($filters: MeasurementCategoryFilter, $pagination: OffsetPaginationInput) {\n  measurementCategories(filters: $filters, pagination: $pagination) {\n    ...ListMeasurementCategory\n    __typename\n  }\n}"


class GetMetricQuery(BaseModel):
    """No documentation found for this operation."""

    metric: Metric

    class Arguments(BaseModel):
        """Arguments for GetMetric"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetMetric"""

        document = "fragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nquery GetMetric($id: ID!) {\n  metric(id: $id) {\n    ...Metric\n    __typename\n  }\n}"


class SearchMetricsQueryOptions(MetricTrait, BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchMetricsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchMetricsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchMetrics"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchMetrics"""

        document = "query SearchMetrics($search: String, $values: [ID!]) {\n  options: metrics(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListMetricsQuery(BaseModel):
    """No documentation found for this operation."""

    metrics: Tuple[ListMetric, ...]

    class Arguments(BaseModel):
        """Arguments for ListMetrics"""

        filters: Optional[MetricFilter] = Field(default=None)
        pagination: Optional[GraphPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListMetrics"""

        document = "fragment ListMetric on Metric {\n  id\n  value\n  label\n  __typename\n}\n\nquery ListMetrics($filters: MetricFilter, $pagination: GraphPaginationInput) {\n  metrics(filters: $filters, pagination: $pagination) {\n    ...ListMetric\n    __typename\n  }\n}"


class GetMetricCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    metric_category: MetricCategory = Field(alias="metricCategory")

    class Arguments(BaseModel):
        """Arguments for GetMetricCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetMetricCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MetricCategory on MetricCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  metricKind\n  __typename\n}\n\nquery GetMetricCategory($id: ID!) {\n  metricCategory(id: $id) {\n    ...MetricCategory\n    __typename\n  }\n}"


class SearchMetricCategoryQueryOptions(MetricCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchMetricCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchMetricCategoryQueryOptions, ...]
    "List of all metric categories"

    class Arguments(BaseModel):
        """Arguments for SearchMetricCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchMetricCategory"""

        document = "query SearchMetricCategory($search: String, $values: [ID!]) {\n  options: metricCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetModelQuery(BaseModel):
    """No documentation found for this operation."""

    model: Model

    class Arguments(BaseModel):
        """Arguments for GetModel"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetModel"""

        document = "fragment MediaStore on MediaStore {\n  id\n  presignedUrl\n  key\n  __typename\n}\n\nfragment Model on Model {\n  id\n  name\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}\n\nquery GetModel($id: ID!) {\n  model(id: $id) {\n    ...Model\n    __typename\n  }\n}"


class SearchModelsQueryOptions(BaseModel):
    """A model represents a trained machine learning model that can be used for analysis."""

    typename: Literal["Model"] = Field(
        alias="__typename", default="Model", exclude=True
    )
    value: ID
    "The unique identifier of the model"
    label: str
    "The name of the model"
    model_config = ConfigDict(frozen=True)


class SearchModelsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchModelsQueryOptions, ...]
    "List of all deep learning models (e.g. neural networks)"

    class Arguments(BaseModel):
        """Arguments for SearchModels"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchModels"""

        document = "query SearchModels($search: String, $values: [ID!]) {\n  options: models(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetNaturalEventQuery(BaseModel):
    """No documentation found for this operation."""

    natural_event: NaturalEvent = Field(alias="naturalEvent")

    class Arguments(BaseModel):
        """Arguments for GetNaturalEvent"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetNaturalEvent"""

        document = "fragment NaturalEvent on NaturalEvent {\n  id\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nquery GetNaturalEvent($id: ID!) {\n  naturalEvent(id: $id) {\n    ...NaturalEvent\n    __typename\n  }\n}"


class SearchNaturalEventsQueryOptions(BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchNaturalEventsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchNaturalEventsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchNaturalEvents"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchNaturalEvents"""

        document = "query SearchNaturalEvents($search: String, $values: [ID!]) {\n  options: naturalEvents(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetNaturalEventCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    natural_event_category: NaturalEventCategory = Field(alias="naturalEventCategory")

    class Arguments(BaseModel):
        """Arguments for GetNaturalEventCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetNaturalEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment NaturalEventCategory on NaturalEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nquery GetNaturalEventCategory($id: ID!) {\n  naturalEventCategory(id: $id) {\n    ...NaturalEventCategory\n    __typename\n  }\n}"


class SearchNaturalEventCategoriesQueryOptions(NaturalEventCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchNaturalEventCategoriesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchNaturalEventCategoriesQueryOptions, ...]
    "List of all natural event categories"

    class Arguments(BaseModel):
        """Arguments for SearchNaturalEventCategories"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchNaturalEventCategories"""

        document = "query SearchNaturalEventCategories($search: String, $values: [ID!]) {\n  options: naturalEventCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListNaturalEventCategoriesQuery(BaseModel):
    """No documentation found for this operation."""

    natural_event_categories: Tuple[NaturalEventCategory, ...] = Field(
        alias="naturalEventCategories"
    )
    "List of all natural event categories"

    class Arguments(BaseModel):
        """Arguments for ListNaturalEventCategories"""

        filters: Optional[NaturalEventCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListNaturalEventCategories"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment NaturalEventCategory on NaturalEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nquery ListNaturalEventCategories($filters: NaturalEventCategoryFilter, $pagination: OffsetPaginationInput) {\n  naturalEventCategories(filters: $filters, pagination: $pagination) {\n    ...NaturalEventCategory\n    __typename\n  }\n}"


class GetNodeQueryNodeBase(NodeTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class GetNodeQueryNodeBaseEntity(
    DetailNodeEntity, GetNodeQueryNodeBase, EntityTrait, BaseModel
):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )


class GetNodeQueryNodeBaseStructure(
    DetailNodeStructure, GetNodeQueryNodeBase, StructureTrait, BaseModel
):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )


class GetNodeQueryNodeBaseMetric(
    DetailNodeMetric, GetNodeQueryNodeBase, MetricTrait, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Metric"] = Field(
        alias="__typename", default="Metric", exclude=True
    )


class GetNodeQueryNodeBaseProtocolEvent(
    DetailNodeProtocolEvent, GetNodeQueryNodeBase, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )


class GetNodeQueryNodeBaseNaturalEvent(
    DetailNodeNaturalEvent, GetNodeQueryNodeBase, BaseModel
):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["NaturalEvent"] = Field(
        alias="__typename", default="NaturalEvent", exclude=True
    )


class GetNodeQueryNodeBaseReagent(DetailNodeReagent, GetNodeQueryNodeBase, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Reagent"] = Field(
        alias="__typename", default="Reagent", exclude=True
    )


class GetNodeQueryNodeBaseCatchAll(GetNodeQueryNodeBase, BaseModel):
    """Catch all class for GetNodeQueryNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)


class GetNodeQuery(BaseModel):
    """No documentation found for this operation."""

    node: Union[
        Annotated[
            Union[
                GetNodeQueryNodeBaseEntity,
                GetNodeQueryNodeBaseStructure,
                GetNodeQueryNodeBaseMetric,
                GetNodeQueryNodeBaseProtocolEvent,
                GetNodeQueryNodeBaseNaturalEvent,
                GetNodeQueryNodeBaseReagent,
            ],
            Field(discriminator="typename"),
        ],
        GetNodeQueryNodeBaseCatchAll,
    ]

    class Arguments(BaseModel):
        """Arguments for GetNode"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetNode"""

        document = "fragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment DetailNode on Node {\n  ...Node\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nquery GetNode($id: ID!) {\n  node(id: $id) {\n    ...DetailNode\n    __typename\n  }\n}"


class SearchNodesQueryOptions(EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchNodesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchNodesQueryOptions, ...]
    "List of all entities in the system"

    class Arguments(BaseModel):
        """Arguments for SearchNodes"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchNodes"""

        document = "query SearchNodes($search: String, $values: [ID!]) {\n  options: nodes(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class NodeCategoriesQueryNodecategoriesBase(NodeCategoryTrait, BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class NodeCategoriesQueryNodecategoriesBaseMetricCategory(
    NodeCategoryMetricCategory,
    NodeCategoriesQueryNodecategoriesBase,
    MetricCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["MetricCategory"] = Field(
        alias="__typename", default="MetricCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseStructureCategory(
    NodeCategoryStructureCategory,
    NodeCategoriesQueryNodecategoriesBase,
    StructureCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseProtocolEventCategory(
    NodeCategoryProtocolEventCategory,
    NodeCategoriesQueryNodecategoriesBase,
    ProtocolEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseEntityCategory(
    NodeCategoryEntityCategory,
    NodeCategoriesQueryNodecategoriesBase,
    EntityCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["EntityCategory"] = Field(
        alias="__typename", default="EntityCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseReagentCategory(
    NodeCategoryReagentCategory,
    NodeCategoriesQueryNodecategoriesBase,
    ReagentCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseNaturalEventCategory(
    NodeCategoryNaturalEventCategory,
    NodeCategoriesQueryNodecategoriesBase,
    NaturalEventCategoryTrait,
    BaseModel,
):
    """No documentation"""

    typename: Literal["NaturalEventCategory"] = Field(
        alias="__typename", default="NaturalEventCategory", exclude=True
    )


class NodeCategoriesQueryNodecategoriesBaseCatchAll(
    NodeCategoriesQueryNodecategoriesBase, BaseModel
):
    """Catch all class for NodeCategoriesQueryNodecategoriesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class NodeCategoriesQuery(BaseModel):
    """No documentation found for this operation."""

    node_categories: Tuple[
        Union[
            Annotated[
                Union[
                    NodeCategoriesQueryNodecategoriesBaseMetricCategory,
                    NodeCategoriesQueryNodecategoriesBaseStructureCategory,
                    NodeCategoriesQueryNodecategoriesBaseProtocolEventCategory,
                    NodeCategoriesQueryNodecategoriesBaseEntityCategory,
                    NodeCategoriesQueryNodecategoriesBaseReagentCategory,
                    NodeCategoriesQueryNodecategoriesBaseNaturalEventCategory,
                ],
                Field(discriminator="typename"),
            ],
            NodeCategoriesQueryNodecategoriesBaseCatchAll,
        ],
        ...,
    ] = Field(alias="nodeCategories")

    class Arguments(BaseModel):
        """Arguments for NodeCategories"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for NodeCategories"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment ListScatterPlot on ScatterPlot {\n  id\n  name\n  xColumn\n  yColumn\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment VariableDefinition on VariableDefinition {\n  param\n  valueKind\n  default\n  optional\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment GraphQuery on GraphQuery {\n  id\n  query\n  name\n  graph {\n    id\n    name\n    __typename\n  }\n  scatterPlots(pagination: {limit: 1}) {\n    ...ListScatterPlot\n    __typename\n  }\n  render {\n    ...Path\n    ...Pairs\n    ...Table\n    __typename\n  }\n  pinned\n  __typename\n}\n\nfragment StructureCategory on StructureCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  identifier\n  __typename\n}\n\nfragment NaturalEventCategory on NaturalEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment EntityCategory on EntityCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  instanceKind\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  bestQuery {\n    ...GraphQuery\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentCategory on ReagentCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  __typename\n}\n\nfragment MetricCategory on MetricCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  metricKind\n  __typename\n}\n\nfragment ProtocolEventCategory on ProtocolEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  variableDefinitions {\n    ...VariableDefinition\n    __typename\n  }\n  __typename\n}\n\nfragment NodeCategory on NodeCategory {\n  ...StructureCategory\n  ...EntityCategory\n  ...ProtocolEventCategory\n  ...NaturalEventCategory\n  ...MetricCategory\n  ...ReagentCategory\n  __typename\n}\n\nquery NodeCategories {\n  nodeCategories {\n    ...NodeCategory\n    __typename\n  }\n}"


class GetNodeQueryQuery(BaseModel):
    """No documentation found for this operation."""

    node_query: NodeQuery = Field(alias="nodeQuery")

    class Arguments(BaseModel):
        """Arguments for GetNodeQuery"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetNodeQuery"""

        document = "fragment NodeQuery on NodeQuery {\n  id\n  name\n  pinned\n  __typename\n}\n\nquery GetNodeQuery($id: ID!) {\n  nodeQuery(id: $id) {\n    ...NodeQuery\n    __typename\n  }\n}"


class RenderNodeQueryQuery(BaseModel):
    """No documentation found for this operation."""

    render_node_query: Union[Path, Table, Pairs] = Field(alias="renderNodeQuery")
    "Render a node query"

    class Arguments(BaseModel):
        """Arguments for RenderNodeQuery"""

        id: ID
        node_id: ID = Field(alias="nodeId")
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RenderNodeQuery"""

        document = "fragment Measurement on Measurement {\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Metric on Metric {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  value\n  __typename\n}\n\nfragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nfragment BaseEdge on Edge {\n  id\n  leftId\n  rightId\n  __typename\n}\n\nfragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nfragment StructureRelation on StructureRelation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nfragment Entity on Entity {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  label\n  __typename\n}\n\nfragment BaseNode on Node {\n  id\n  label\n  __typename\n}\n\nfragment Node on Node {\n  ...BaseNode\n  ...Entity\n  ...Structure\n  ...Metric\n  ...Reagent\n  __typename\n}\n\nfragment Column on Column {\n  name\n  kind\n  valueKind\n  label\n  description\n  category\n  searchable\n  idfor\n  preferhidden\n  __typename\n}\n\nfragment Edge on Edge {\n  ...BaseEdge\n  ...Measurement\n  ...Relation\n  ...Participant\n  ...StructureRelation\n  __typename\n}\n\nfragment Path on Path {\n  nodes {\n    ...Node\n    __typename\n  }\n  edges {\n    ...Edge\n    __typename\n  }\n  __typename\n}\n\nfragment Table on Table {\n  graph {\n    ageName\n    __typename\n  }\n  rows\n  columns {\n    ...Column\n    __typename\n  }\n  __typename\n}\n\nfragment Pairs on Pairs {\n  pairs {\n    source {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    target {\n      ... on Structure {\n        identifier\n        object\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery RenderNodeQuery($id: ID!, $nodeId: ID!) {\n  renderNodeQuery(id: $id, nodeId: $nodeId) {\n    ...Path\n    ...Table\n    ...Pairs\n    __typename\n  }\n}"


class SearchNodeQueriesQueryOptions(BaseModel):
    """A view of a node entities and relations."""

    typename: Literal["NodeQuery"] = Field(
        alias="__typename", default="NodeQuery", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchNodeQueriesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchNodeQueriesQueryOptions, ...]
    "List of all node queries"

    class Arguments(BaseModel):
        """Arguments for SearchNodeQueries"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchNodeQueries"""

        document = "query SearchNodeQueries($search: String, $values: [ID!]) {\n  options: nodeQueries(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListNodeQueriesQuery(BaseModel):
    """No documentation found for this operation."""

    node_queries: Tuple[ListNodeQuery, ...] = Field(alias="nodeQueries")
    "List of all node queries"

    class Arguments(BaseModel):
        """Arguments for ListNodeQueries"""

        filters: Optional[NodeQueryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListNodeQueries"""

        document = "fragment ListNodeQuery on NodeQuery {\n  id\n  name\n  query\n  description\n  pinned\n  __typename\n}\n\nquery ListNodeQueries($filters: NodeQueryFilter, $pagination: OffsetPaginationInput) {\n  nodeQueries(filters: $filters, pagination: $pagination) {\n    ...ListNodeQuery\n    __typename\n  }\n}"


class GetParticipantQuery(BaseModel):
    """No documentation found for this operation."""

    participant: Participant

    class Arguments(BaseModel):
        """Arguments for GetParticipant"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetParticipant"""

        document = "fragment Participant on Participant {\n  role\n  quantity\n  __typename\n}\n\nquery GetParticipant($id: ID!) {\n  participant(id: $id) {\n    ...Participant\n    __typename\n  }\n}"


class SearchParticipantsQueryOptions(BaseModel):
    """A participant edge maps bioentitiy to an event (valid from is not necessary)"""

    typename: Literal["Participant"] = Field(
        alias="__typename", default="Participant", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchParticipantsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchParticipantsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchParticipants"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchParticipants"""

        document = "query SearchParticipants($search: String, $values: [ID!]) {\n  options: participants(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetProtocolEventQuery(BaseModel):
    """No documentation found for this operation."""

    protocol_event: ProtocolEvent = Field(alias="protocolEvent")

    class Arguments(BaseModel):
        """Arguments for GetProtocolEvent"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetProtocolEvent"""

        document = "fragment ProtocolEvent on ProtocolEvent {\n  id\n  validFrom\n  validTo\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nquery GetProtocolEvent($id: ID!) {\n  protocolEvent(id: $id) {\n    ...ProtocolEvent\n    __typename\n  }\n}"


class SearchProtocolEventsQueryOptions(BaseModel):
    """A Metric is a recorded data point in a graph. It always describes a structure and through the structure it can bring meaning to the measured entity. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["ProtocolEvent"] = Field(
        alias="__typename", default="ProtocolEvent", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchProtocolEventsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchProtocolEventsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchProtocolEvents"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchProtocolEvents"""

        document = "query SearchProtocolEvents($search: String, $values: [ID!]) {\n  options: protocolEvents(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetProtocolEventCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    protocol_event_category: ProtocolEventCategory = Field(
        alias="protocolEventCategory"
    )

    class Arguments(BaseModel):
        """Arguments for GetProtocolEventCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetProtocolEventCategory"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment VariableDefinition on VariableDefinition {\n  param\n  valueKind\n  default\n  optional\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ProtocolEventCategory on ProtocolEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  variableDefinitions {\n    ...VariableDefinition\n    __typename\n  }\n  __typename\n}\n\nquery GetProtocolEventCategory($id: ID!) {\n  protocolEventCategory(id: $id) {\n    ...ProtocolEventCategory\n    __typename\n  }\n}"


class SearchProtocolEventCategoriesQueryOptions(ProtocolEventCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["ProtocolEventCategory"] = Field(
        alias="__typename", default="ProtocolEventCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchProtocolEventCategoriesQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchProtocolEventCategoriesQueryOptions, ...]
    "List of all protocol event categories"

    class Arguments(BaseModel):
        """Arguments for SearchProtocolEventCategories"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchProtocolEventCategories"""

        document = "query SearchProtocolEventCategories($search: String, $values: [ID!]) {\n  options: protocolEventCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListProtocolEventCategoriesQuery(BaseModel):
    """No documentation found for this operation."""

    protocol_event_categories: Tuple[ProtocolEventCategory, ...] = Field(
        alias="protocolEventCategories"
    )
    "List of all protocol event categories"

    class Arguments(BaseModel):
        """Arguments for ListProtocolEventCategories"""

        filters: Optional[ProtocolEventCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListProtocolEventCategories"""

        document = "fragment EntityCategoryDefinition on EntityCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment ReagentCategoryDefinition on ReagentCategoryDefinition {\n  tagFilters\n  categoryFilters\n  __typename\n}\n\nfragment EntityRoleDefinition on EntityRoleDefinition {\n  role\n  categoryDefinition {\n    ...EntityCategoryDefinition\n    __typename\n  }\n  optional\n  allowMultiple\n  __typename\n}\n\nfragment VariableDefinition on VariableDefinition {\n  param\n  valueKind\n  default\n  optional\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentRoleDefinition on ReagentRoleDefinition {\n  role\n  categoryDefinition {\n    ...ReagentCategoryDefinition\n    __typename\n  }\n  needsQuantity\n  optional\n  __typename\n}\n\nfragment ProtocolEventCategory on ProtocolEventCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  plateChildren\n  label\n  ageName\n  label\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  sourceEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  targetEntityRoles {\n    ...EntityRoleDefinition\n    __typename\n  }\n  sourceReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  targetReagentRoles {\n    ...ReagentRoleDefinition\n    __typename\n  }\n  variableDefinitions {\n    ...VariableDefinition\n    __typename\n  }\n  __typename\n}\n\nquery ListProtocolEventCategories($filters: ProtocolEventCategoryFilter, $pagination: OffsetPaginationInput) {\n  protocolEventCategories(filters: $filters, pagination: $pagination) {\n    ...ProtocolEventCategory\n    __typename\n  }\n}"


class GetReagentQuery(BaseModel):
    """No documentation found for this operation."""

    reagent: Reagent

    class Arguments(BaseModel):
        """Arguments for GetReagent"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetReagent"""

        document = "fragment Reagent on Reagent {\n  id\n  category {\n    id\n    label\n    __typename\n  }\n  externalId\n  label\n  __typename\n}\n\nquery GetReagent($id: ID!) {\n  reagent(id: $id) {\n    ...Reagent\n    __typename\n  }\n}"


class SearchReagentsQueryOptions(EntityTrait, BaseModel):
    """A Entity is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Entity"] = Field(
        alias="__typename", default="Entity", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchReagentsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchReagentsQueryOptions, ...]
    "List of all entities in the system"

    class Arguments(BaseModel):
        """Arguments for SearchReagents"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchReagents"""

        document = "query SearchReagents($search: String, $values: [ID!]) {\n  options: nodes(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListReagentsQuery(BaseModel):
    """No documentation found for this operation."""

    reagents: Tuple[ListReagent, ...]

    class Arguments(BaseModel):
        """Arguments for ListReagents"""

        filters: Optional[ReagentFilter] = Field(default=None)
        pagination: Optional[GraphPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListReagents"""

        document = "fragment ListReagent on Reagent {\n  id\n  label\n  __typename\n}\n\nquery ListReagents($filters: ReagentFilter, $pagination: GraphPaginationInput) {\n  reagents(filters: $filters, pagination: $pagination) {\n    ...ListReagent\n    __typename\n  }\n}"


class GetReagentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    reagent_category: ReagentCategory = Field(alias="reagentCategory")

    class Arguments(BaseModel):
        """Arguments for GetReagentCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetReagentCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ReagentCategory on ReagentCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  __typename\n}\n\nquery GetReagentCategory($id: ID!) {\n  reagentCategory(id: $id) {\n    ...ReagentCategory\n    __typename\n  }\n}"


class SearchReagentCategoryQueryOptions(ReagentCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["ReagentCategory"] = Field(
        alias="__typename", default="ReagentCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchReagentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchReagentCategoryQueryOptions, ...]
    "List of all reagent categories"

    class Arguments(BaseModel):
        """Arguments for SearchReagentCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchReagentCategory"""

        document = "query SearchReagentCategory($search: String, $values: [ID!]) {\n  options: reagentCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListReagentCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    reagent_categories: Tuple[ListReagentCategory, ...] = Field(
        alias="reagentCategories"
    )
    "List of all reagent categories"

    class Arguments(BaseModel):
        """Arguments for ListReagentCategory"""

        filters: Optional[ReagentCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListReagentCategory"""

        document = "fragment BaseListCategory on BaseCategory {\n  id\n  description\n  store {\n    presignedUrl\n    __typename\n  }\n  tags {\n    id\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment ListReagentCategory on ReagentCategory {\n  ...BaseListCategory\n  ...BaseNodeCategory\n  instanceKind\n  label\n  __typename\n}\n\nquery ListReagentCategory($filters: ReagentCategoryFilter, $pagination: OffsetPaginationInput) {\n  reagentCategories(filters: $filters, pagination: $pagination) {\n    ...ListReagentCategory\n    __typename\n  }\n}"


class GetRelationQuery(BaseModel):
    """No documentation found for this operation."""

    relation: Relation

    class Arguments(BaseModel):
        """Arguments for GetRelation"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRelation"""

        document = "fragment Relation on Relation {\n  category {\n    id\n    label\n    __typename\n  }\n  __typename\n}\n\nquery GetRelation($id: ID!) {\n  relation(id: $id) {\n    ...Relation\n    __typename\n  }\n}"


class SearchRelationsQueryOptions(BaseModel):
    """A relation is an edge between two entities. It is a directed edge, that connects two entities and established a relationship
    that is not a measurement between them. I.e. when they are an subjective assertion about the entities.



    """

    typename: Literal["Relation"] = Field(
        alias="__typename", default="Relation", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchRelationsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchRelationsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchRelations"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchRelations"""

        document = "query SearchRelations($search: String, $values: [ID!]) {\n  options: relations(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    relation_category: RelationCategory = Field(alias="relationCategory")

    class Arguments(BaseModel):
        """Arguments for GetRelationCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment RelationCategory on RelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nquery GetRelationCategory($id: ID!) {\n  relationCategory(id: $id) {\n    ...RelationCategory\n    __typename\n  }\n}"


class SearchRelationCategoryQueryOptions(RelationCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["RelationCategory"] = Field(
        alias="__typename", default="RelationCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchRelationCategoryQueryOptions, ...]
    "List of all relation categories"

    class Arguments(BaseModel):
        """Arguments for SearchRelationCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchRelationCategory"""

        document = "query SearchRelationCategory($search: String, $values: [ID!]) {\n  options: relationCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    relation_categories: Tuple[RelationCategory, ...] = Field(
        alias="relationCategories"
    )
    "List of all relation categories"

    class Arguments(BaseModel):
        """Arguments for ListRelationCategory"""

        filters: Optional[RelationCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment RelationCategory on RelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nquery ListRelationCategory($filters: RelationCategoryFilter, $pagination: OffsetPaginationInput) {\n  relationCategories(filters: $filters, pagination: $pagination) {\n    ...RelationCategory\n    __typename\n  }\n}"


class GetStructureQuery(BaseModel):
    """No documentation found for this operation."""

    structure: Structure

    class Arguments(BaseModel):
        """Arguments for GetStructure"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetStructure"""

        document = "fragment Structure on Structure {\n  id\n  object\n  identifier\n  __typename\n}\n\nquery GetStructure($id: ID!) {\n  structure(id: $id) {\n    ...Structure\n    __typename\n  }\n}"


class SearchStructuresQueryOptions(StructureTrait, BaseModel):
    """A Structure is a recorded data point in a graph. It can measure a property of an entity through a direct measurement edge, that connects the entity to the structure. It of course can relate to other structures through relation edges."""

    typename: Literal["Structure"] = Field(
        alias="__typename", default="Structure", exclude=True
    )
    value: NodeID
    "The unique identifier of the entity within its graph"
    label: str
    model_config = ConfigDict(frozen=True)


class SearchStructuresQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchStructuresQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchStructures"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchStructures"""

        document = "query SearchStructures($search: String, $values: [ID!]) {\n  options: structures(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class GetInformedStructureQuery(BaseModel):
    """No documentation found for this operation."""

    structure_by_identifier: InformedStructure = Field(alias="structureByIdentifier")

    class Arguments(BaseModel):
        """Arguments for GetInformedStructure"""

        graph: ID
        identifier: StructureIdentifier
        object: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetInformedStructure"""

        document = "fragment InformedStructure on Structure {\n  id\n  category {\n    id\n    identifier\n    __typename\n  }\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nquery GetInformedStructure($graph: ID!, $identifier: StructureIdentifier!, $object: ID!) {\n  structureByIdentifier(graph: $graph, identifier: $identifier, object: $object) {\n    ...InformedStructure\n    __typename\n  }\n}"


class ListStructuresQuery(BaseModel):
    """No documentation found for this operation."""

    structures: Tuple[ListStructure, ...]

    class Arguments(BaseModel):
        """Arguments for ListStructures"""

        filters: Optional[StructureFilter] = Field(default=None)
        pagination: Optional[GraphPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListStructures"""

        document = "fragment ListStructure on Structure {\n  id\n  category {\n    identifier\n    id\n    __typename\n  }\n  __typename\n}\n\nquery ListStructures($filters: StructureFilter, $pagination: GraphPaginationInput) {\n  structures(filters: $filters, pagination: $pagination) {\n    ...ListStructure\n    __typename\n  }\n}"


class GetStructureCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    structure_category: StructureCategory = Field(alias="structureCategory")

    class Arguments(BaseModel):
        """Arguments for GetStructureCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetStructureCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureCategory on StructureCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  identifier\n  __typename\n}\n\nquery GetStructureCategory($id: ID!) {\n  structureCategory(id: $id) {\n    ...StructureCategory\n    __typename\n  }\n}"


class SearchStructureCategoryQueryOptions(StructureCategoryTrait, BaseModel):
    """No documentation"""

    typename: Literal["StructureCategory"] = Field(
        alias="__typename", default="StructureCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The structure that this class represents"
    model_config = ConfigDict(frozen=True)


class SearchStructureCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchStructureCategoryQueryOptions, ...]
    "List of all structure categories"

    class Arguments(BaseModel):
        """Arguments for SearchStructureCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchStructureCategory"""

        document = "query SearchStructureCategory($search: String, $values: [ID!]) {\n  options: structureCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: identifier\n    __typename\n  }\n}"


class ListStructureCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    structure_categories: Tuple[StructureCategory, ...] = Field(
        alias="structureCategories"
    )
    "List of all structure categories"

    class Arguments(BaseModel):
        """Arguments for ListStructureCategory"""

        filters: Optional[StructureCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListStructureCategory"""

        document = "fragment BaseNodeCategory on NodeCategory {\n  id\n  positionX\n  positionY\n  width\n  height\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureCategory on StructureCategory {\n  ...BaseCategory\n  ...BaseNodeCategory\n  identifier\n  __typename\n}\n\nquery ListStructureCategory($filters: StructureCategoryFilter, $pagination: OffsetPaginationInput) {\n  structureCategories(filters: $filters, pagination: $pagination) {\n    ...StructureCategory\n    __typename\n  }\n}"


class GetStructureRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    structure_relation_category: StructureRelationCategory = Field(
        alias="structureRelationCategory"
    )

    class Arguments(BaseModel):
        """Arguments for GetStructureRelationCategory"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetStructureRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelationCategory on StructureRelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nquery GetStructureRelationCategory($id: ID!) {\n  structureRelationCategory(id: $id) {\n    ...StructureRelationCategory\n    __typename\n  }\n}"


class SearchStructureRelationCategoryQueryOptions(
    StructureRelationCategoryTrait, BaseModel
):
    """No documentation"""

    typename: Literal["StructureRelationCategory"] = Field(
        alias="__typename", default="StructureRelationCategory", exclude=True
    )
    value: ID
    "The unique identifier of the expression within its graph"
    label: str
    "The label of the expression"
    model_config = ConfigDict(frozen=True)


class SearchStructureRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchStructureRelationCategoryQueryOptions, ...]
    "List of all structure relation categories"

    class Arguments(BaseModel):
        """Arguments for SearchStructureRelationCategory"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchStructureRelationCategory"""

        document = "query SearchStructureRelationCategory($search: String, $values: [ID!]) {\n  options: structureRelationCategories(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListStructureRelationCategoryQuery(BaseModel):
    """No documentation found for this operation."""

    structure_relation_categories: Tuple[StructureRelationCategory, ...] = Field(
        alias="structureRelationCategories"
    )
    "List of all structure relation categories"

    class Arguments(BaseModel):
        """Arguments for ListStructureRelationCategory"""

        filters: Optional[StructureRelationCategoryFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListStructureRelationCategory"""

        document = "fragment BaseEdgeCategory on EdgeCategory {\n  id\n  __typename\n}\n\nfragment BaseCategory on BaseCategory {\n  id\n  graph {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureRelationCategory on StructureRelationCategory {\n  ...BaseCategory\n  ...BaseEdgeCategory\n  sourceDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  targetDefinition {\n    tagFilters\n    categoryFilters\n    __typename\n  }\n  __typename\n}\n\nquery ListStructureRelationCategory($filters: StructureRelationCategoryFilter, $pagination: OffsetPaginationInput) {\n  structureRelationCategories(filters: $filters, pagination: $pagination) {\n    ...StructureRelationCategory\n    __typename\n  }\n}"


class SearchTagsQueryOptions(BaseModel):
    """A tag is a label that can be assigned to entities and relations."""

    typename: Literal["Tag"] = Field(alias="__typename", default="Tag", exclude=True)
    value: str
    label: str
    model_config = ConfigDict(frozen=True)


class SearchTagsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchTagsQueryOptions, ...]
    "List of all tags in the system"

    class Arguments(BaseModel):
        """Arguments for SearchTags"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[str]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchTags"""

        document = "query SearchTags($search: String, $values: [String!]) {\n  options: tags(\n    filters: {search: $search, values: $values}\n    pagination: {limit: 10}\n  ) {\n    value: value\n    label: value\n    __typename\n  }\n}"


async def acreate_measurement_category(
    graph: IDCoercible,
    label: str,
    structure_definition: StructureCategoryDefinitionInput,
    entity_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> MeasurementCategory:
    """CreateMeasurementCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        structure_definition: The source definition for this expression
        entity_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MeasurementCategory
    """
    return (
        await aexecute(
            CreateMeasurementCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "label": label,
                    "structureDefinition": structure_definition,
                    "entityDefinition": entity_definition,
                }
            },
            rath=rath,
        )
    ).create_measurement_category


def create_measurement_category(
    graph: IDCoercible,
    label: str,
    structure_definition: StructureCategoryDefinitionInput,
    entity_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> MeasurementCategory:
    """CreateMeasurementCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        structure_definition: The source definition for this expression
        entity_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MeasurementCategory
    """
    return execute(
        CreateMeasurementCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "label": label,
                "structureDefinition": structure_definition,
                "entityDefinition": entity_definition,
            }
        },
        rath=rath,
    ).create_measurement_category


async def acreate_metric_category(
    graph: IDCoercible,
    structure_definition: CategoryDefinitionInput,
    label: str,
    kind: MetricKind,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> MetricCategory:
    """CreateMetricCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        structure_definition: The structure category for this expression
        label: The label/name of the expression
        kind: The type of metric data this expression represents
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MetricCategory
    """
    return (
        await aexecute(
            CreateMetricCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "structureDefinition": structure_definition,
                    "label": label,
                    "kind": kind,
                }
            },
            rath=rath,
        )
    ).create_metric_category


def create_metric_category(
    graph: IDCoercible,
    structure_definition: CategoryDefinitionInput,
    label: str,
    kind: MetricKind,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> MetricCategory:
    """CreateMetricCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        structure_definition: The structure category for this expression
        label: The label/name of the expression
        kind: The type of metric data this expression represents
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MetricCategory
    """
    return execute(
        CreateMetricCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "structureDefinition": structure_definition,
                "label": label,
                "kind": kind,
            }
        },
        rath=rath,
    ).create_metric_category


async def acreate_reagent_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> ReagentCategory:
    """CreateReagentCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ReagentCategory
    """
    return (
        await aexecute(
            CreateReagentCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "label": label,
                }
            },
            rath=rath,
        )
    ).create_reagent_category


def create_reagent_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> ReagentCategory:
    """CreateReagentCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ReagentCategory
    """
    return execute(
        CreateReagentCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "label": label,
            }
        },
        rath=rath,
    ).create_reagent_category


async def acreate_relation_category(
    graph: IDCoercible,
    label: str,
    source_definition: CategoryDefinitionInput,
    target_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> RelationCategory:
    """CreateRelationCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        source_definition: The source definition for this expression
        target_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RelationCategory
    """
    return (
        await aexecute(
            CreateRelationCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "label": label,
                    "sourceDefinition": source_definition,
                    "targetDefinition": target_definition,
                }
            },
            rath=rath,
        )
    ).create_relation_category


def create_relation_category(
    graph: IDCoercible,
    label: str,
    source_definition: CategoryDefinitionInput,
    target_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> RelationCategory:
    """CreateRelationCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        source_definition: The source definition for this expression
        target_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RelationCategory
    """
    return execute(
        CreateRelationCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "label": label,
                "sourceDefinition": source_definition,
                "targetDefinition": target_definition,
            }
        },
        rath=rath,
    ).create_relation_category


async def acreate_entity(
    entity_category: IDCoercible,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> Entity:
    """CreateEntity

    Create a new entity

    Args:
        entity_category: The ID of the kind (LinkedExpression) to create the entity from
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return (
        await aexecute(
            CreateEntityMutation,
            {
                "input": {
                    "entityCategory": entity_category,
                    "name": name,
                    "externalId": external_id,
                }
            },
            rath=rath,
        )
    ).create_entity


def create_entity(
    entity_category: IDCoercible,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> Entity:
    """CreateEntity

    Create a new entity

    Args:
        entity_category: The ID of the kind (LinkedExpression) to create the entity from
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return execute(
        CreateEntityMutation,
        {
            "input": {
                "entityCategory": entity_category,
                "name": name,
                "externalId": external_id,
            }
        },
        rath=rath,
    ).create_entity


async def acreate_entity_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> EntityCategory:
    """CreateEntityCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return (
        await aexecute(
            CreateEntityCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "label": label,
                }
            },
            rath=rath,
        )
    ).create_entity_category


def create_entity_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    rath: Optional[KraphRath] = None,
) -> EntityCategory:
    """CreateEntityCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return execute(
        CreateEntityCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "label": label,
            }
        },
        rath=rath,
    ).create_entity_category


async def aupdate_entity_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> EntityCategory:
    """UpdateEntityCategory

    Update an existing expression

    Args:
        description: New description for the expression
        purl: New permanent URL for the expression
        color: New RGBA color values as list of 3 or 4 integers
        image: New image ID for the expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: New label for the generic category
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return (
        await aexecute(
            UpdateEntityCategoryMutation,
            {
                "input": {
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "id": id,
                    "label": label,
                }
            },
            rath=rath,
        )
    ).update_entity_category


def update_entity_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> EntityCategory:
    """UpdateEntityCategory

    Update an existing expression

    Args:
        description: New description for the expression
        purl: New permanent URL for the expression
        color: New RGBA color values as list of 3 or 4 integers
        image: New image ID for the expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: New label for the generic category
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return execute(
        UpdateEntityCategoryMutation,
        {
            "input": {
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "id": id,
                "label": label,
            }
        },
        rath=rath,
    ).update_entity_category


async def acreate_graph(
    name: str,
    description: Optional[str] = None,
    image: Optional[IDCoercible] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Graph:
    """CreateGraph

    Create a new graph

    Args:
        name: The name of the ontology (will be converted to snake_case)
        description: An optional description of the ontology
        image: An optional ID reference to an associated image
        pin: Whether this ontology should be pinned or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return (
        await aexecute(
            CreateGraphMutation,
            {
                "input": {
                    "name": name,
                    "description": description,
                    "image": image,
                    "pin": pin,
                }
            },
            rath=rath,
        )
    ).create_graph


def create_graph(
    name: str,
    description: Optional[str] = None,
    image: Optional[IDCoercible] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Graph:
    """CreateGraph

    Create a new graph

    Args:
        name: The name of the ontology (will be converted to snake_case)
        description: An optional description of the ontology
        image: An optional ID reference to an associated image
        pin: Whether this ontology should be pinned or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return execute(
        CreateGraphMutation,
        {
            "input": {
                "name": name,
                "description": description,
                "image": image,
                "pin": pin,
            }
        },
        rath=rath,
    ).create_graph


async def apin_graph(
    id: IDCoercible, pinned: bool, rath: Optional[KraphRath] = None
) -> Graph:
    """PinGraph

    Pin or unpin a graph

    Args:
        id: The ID of the ontology to pin
        pinned: Whether to pin the ontology or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return (
        await aexecute(
            PinGraphMutation, {"input": {"id": id, "pinned": pinned}}, rath=rath
        )
    ).pin_graph


def pin_graph(id: IDCoercible, pinned: bool, rath: Optional[KraphRath] = None) -> Graph:
    """PinGraph

    Pin or unpin a graph

    Args:
        id: The ID of the ontology to pin
        pinned: Whether to pin the ontology or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return execute(
        PinGraphMutation, {"input": {"id": id, "pinned": pinned}}, rath=rath
    ).pin_graph


async def adelete_graph(id: IDCoercible, rath: Optional[KraphRath] = None) -> ID:
    """DeleteGraph

    Delete an existing graph

    Args:
        id: The ID of the ontology to delete
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ID
    """
    return (
        await aexecute(DeleteGraphMutation, {"input": {"id": id}}, rath=rath)
    ).delete_graph


def delete_graph(id: IDCoercible, rath: Optional[KraphRath] = None) -> ID:
    """DeleteGraph

    Delete an existing graph

    Args:
        id: The ID of the ontology to delete
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ID
    """
    return execute(DeleteGraphMutation, {"input": {"id": id}}, rath=rath).delete_graph


async def aupdate_graph(
    id: IDCoercible,
    name: Optional[str] = None,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[IDCoercible] = None,
    nodes: Optional[Iterable[GraphNodeInput]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Graph:
    """UpdateGraph

    Update an existing graph

    Args:
        id: The ID of the ontology to update
        name: New name for the ontology (will be converted to snake_case)
        purl: A new PURL for the ontology (will be converted to snake_case)
        description: New description for the ontology
        image: New ID reference to an associated image
        nodes: New nodes for the ontology
        pin: Whether this ontology should be pinned or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return (
        await aexecute(
            UpdateGraphMutation,
            {
                "input": {
                    "id": id,
                    "name": name,
                    "purl": purl,
                    "description": description,
                    "image": image,
                    "nodes": nodes,
                    "pin": pin,
                }
            },
            rath=rath,
        )
    ).update_graph


def update_graph(
    id: IDCoercible,
    name: Optional[str] = None,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[IDCoercible] = None,
    nodes: Optional[Iterable[GraphNodeInput]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Graph:
    """UpdateGraph

    Update an existing graph

    Args:
        id: The ID of the ontology to update
        name: New name for the ontology (will be converted to snake_case)
        purl: A new PURL for the ontology (will be converted to snake_case)
        description: New description for the ontology
        image: New ID reference to an associated image
        nodes: New nodes for the ontology
        pin: Whether this ontology should be pinned or not
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return execute(
        UpdateGraphMutation,
        {
            "input": {
                "id": id,
                "name": name,
                "purl": purl,
                "description": description,
                "image": image,
                "nodes": nodes,
                "pin": pin,
            }
        },
        rath=rath,
    ).update_graph


async def acreate_graph_query(
    graph: IDCoercible,
    name: str,
    query: CypherCoercible,
    kind: ViewKind,
    description: Optional[str] = None,
    columns: Optional[Iterable[ColumnInput]] = None,
    relevant_for: Optional[Iterable[IDCoercible]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> GraphQuery:
    """CreateGraphQuery

    Create a new graph query

    Args:
        graph: The ID of the ontology this expression belongs to. If not provided, uses default ontology
        name: The label/name of the expression
        query: The label/name of the expression
        description: A detailed description of the expression
        kind: The kind/type of this expression
        columns: The columns (if ViewKind is Table)
        relevant_for: A list of categories where this query is releveant and should be shown
        pin: Whether to pin this expression for the current user
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return (
        await aexecute(
            CreateGraphQueryMutation,
            {
                "input": {
                    "graph": graph,
                    "name": name,
                    "query": query,
                    "description": description,
                    "kind": kind,
                    "columns": columns,
                    "relevantFor": relevant_for,
                    "pin": pin,
                }
            },
            rath=rath,
        )
    ).create_graph_query


def create_graph_query(
    graph: IDCoercible,
    name: str,
    query: CypherCoercible,
    kind: ViewKind,
    description: Optional[str] = None,
    columns: Optional[Iterable[ColumnInput]] = None,
    relevant_for: Optional[Iterable[IDCoercible]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> GraphQuery:
    """CreateGraphQuery

    Create a new graph query

    Args:
        graph: The ID of the ontology this expression belongs to. If not provided, uses default ontology
        name: The label/name of the expression
        query: The label/name of the expression
        description: A detailed description of the expression
        kind: The kind/type of this expression
        columns: The columns (if ViewKind is Table)
        relevant_for: A list of categories where this query is releveant and should be shown
        pin: Whether to pin this expression for the current user
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return execute(
        CreateGraphQueryMutation,
        {
            "input": {
                "graph": graph,
                "name": name,
                "query": query,
                "description": description,
                "kind": kind,
                "columns": columns,
                "relevantFor": relevant_for,
                "pin": pin,
            }
        },
        rath=rath,
    ).create_graph_query


async def apin_graph_query(
    id: IDCoercible, pin: bool, rath: Optional[KraphRath] = None
) -> GraphQuery:
    """PinGraphQuery

    Pin or unpin a graph query

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        pin: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return (
        await aexecute(
            PinGraphQueryMutation, {"input": {"id": id, "pin": pin}}, rath=rath
        )
    ).pin_graph_query


def pin_graph_query(
    id: IDCoercible, pin: bool, rath: Optional[KraphRath] = None
) -> GraphQuery:
    """PinGraphQuery

    Pin or unpin a graph query

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        pin: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return execute(
        PinGraphQueryMutation, {"input": {"id": id, "pin": pin}}, rath=rath
    ).pin_graph_query


async def acreate_measurement(
    category: IDCoercible,
    structure: NodeID,
    entity: NodeID,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Measurement:
    """CreateMeasurement

    Create a new measurement edge

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        structure: The `NodeID` scalar type represents a graph node ID (required)
        entity: The `NodeID` scalar type represents a graph node ID (required)
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Measurement
    """
    return (
        await aexecute(
            CreateMeasurementMutation,
            {
                "input": {
                    "category": category,
                    "structure": structure,
                    "entity": entity,
                    "validFrom": valid_from,
                    "validTo": valid_to,
                    "context": context,
                }
            },
            rath=rath,
        )
    ).create_measurement


def create_measurement(
    category: IDCoercible,
    structure: NodeID,
    entity: NodeID,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Measurement:
    """CreateMeasurement

    Create a new measurement edge

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        structure: The `NodeID` scalar type represents a graph node ID (required)
        entity: The `NodeID` scalar type represents a graph node ID (required)
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Measurement
    """
    return execute(
        CreateMeasurementMutation,
        {
            "input": {
                "category": category,
                "structure": structure,
                "entity": entity,
                "validFrom": valid_from,
                "validTo": valid_to,
                "context": context,
            }
        },
        rath=rath,
    ).create_measurement


async def acreate_metric(
    structure: NodeID,
    category: IDCoercible,
    value: Any,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Metric:
    """CreateMetric

    Create a new metric for an entity

    Args:
        structure: The `NodeID` scalar type represents a graph node ID (required)
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        value: The value of the measurement
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Metric
    """
    return (
        await aexecute(
            CreateMetricMutation,
            {
                "input": {
                    "structure": structure,
                    "category": category,
                    "value": value,
                    "context": context,
                }
            },
            rath=rath,
        )
    ).create_metric


def create_metric(
    structure: NodeID,
    category: IDCoercible,
    value: Any,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Metric:
    """CreateMetric

    Create a new metric for an entity

    Args:
        structure: The `NodeID` scalar type represents a graph node ID (required)
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        value: The value of the measurement
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Metric
    """
    return execute(
        CreateMetricMutation,
        {
            "input": {
                "structure": structure,
                "category": category,
                "value": value,
                "context": context,
            }
        },
        rath=rath,
    ).create_metric


async def acreate_model(
    name: str,
    model: RemoteUpload,
    view: Optional[IDCoercible] = None,
    rath: Optional[KraphRath] = None,
) -> Model:
    """CreateModel

    Create a new model

    Args:
        name: The name of the model
        model: The uploaded model file (e.g. .h5, .onnx, .pt)
        view: Optional view ID to associate with the model
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Model
    """
    return (
        await aexecute(
            CreateModelMutation,
            {"input": {"name": name, "model": model, "view": view}},
            rath=rath,
        )
    ).create_model


def create_model(
    name: str,
    model: RemoteUpload,
    view: Optional[IDCoercible] = None,
    rath: Optional[KraphRath] = None,
) -> Model:
    """CreateModel

    Create a new model

    Args:
        name: The name of the model
        model: The uploaded model file (e.g. .h5, .onnx, .pt)
        view: Optional view ID to associate with the model
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Model
    """
    return execute(
        CreateModelMutation,
        {"input": {"name": name, "model": model, "view": view}},
        rath=rath,
    ).create_model


async def arecord_natural_event(
    category: IDCoercible,
    entity_sources: Optional[Iterable[NodeMapping]] = None,
    entity_targets: Optional[Iterable[NodeMapping]] = None,
    supporting_structure: Optional[IDCoercible] = None,
    external_id: Optional[str] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEvent:
    """RecordNaturalEvent

    Record a new natural event

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        entity_sources:  (required) (list)
        entity_targets:  (required) (list)
        supporting_structure: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        external_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEvent
    """
    return (
        await aexecute(
            RecordNaturalEventMutation,
            {
                "input": {
                    "category": category,
                    "entitySources": entity_sources,
                    "entityTargets": entity_targets,
                    "supportingStructure": supporting_structure,
                    "externalId": external_id,
                    "validFrom": valid_from,
                    "validTo": valid_to,
                }
            },
            rath=rath,
        )
    ).record_natural_event


def record_natural_event(
    category: IDCoercible,
    entity_sources: Optional[Iterable[NodeMapping]] = None,
    entity_targets: Optional[Iterable[NodeMapping]] = None,
    supporting_structure: Optional[IDCoercible] = None,
    external_id: Optional[str] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEvent:
    """RecordNaturalEvent

    Record a new natural event

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        entity_sources:  (required) (list)
        entity_targets:  (required) (list)
        supporting_structure: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        external_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEvent
    """
    return execute(
        RecordNaturalEventMutation,
        {
            "input": {
                "category": category,
                "entitySources": entity_sources,
                "entityTargets": entity_targets,
                "supportingStructure": supporting_structure,
                "externalId": external_id,
                "validFrom": valid_from,
                "validTo": valid_to,
            }
        },
        rath=rath,
    ).record_natural_event


async def acreate_natural_event_category(
    graph: IDCoercible,
    label: str,
    source_entity_roles: Iterable[EntityRoleDefinitionInput],
    target_entity_roles: Iterable[EntityRoleDefinitionInput],
    support_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEventCategory:
    """CreateNaturalEventCategory

    Create a new natural event category

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        source_entity_roles: The source definitions for this expression
        target_entity_roles: The target definitions for this expression
        support_definition: The support definition for this expression
        plate_children: A list of children for the plate
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return (
        await aexecute(
            CreateNaturalEventCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "label": label,
                    "sourceEntityRoles": source_entity_roles,
                    "targetEntityRoles": target_entity_roles,
                    "supportDefinition": support_definition,
                    "plateChildren": plate_children,
                }
            },
            rath=rath,
        )
    ).create_natural_event_category


def create_natural_event_category(
    graph: IDCoercible,
    label: str,
    source_entity_roles: Iterable[EntityRoleDefinitionInput],
    target_entity_roles: Iterable[EntityRoleDefinitionInput],
    support_definition: CategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEventCategory:
    """CreateNaturalEventCategory

    Create a new natural event category

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        source_entity_roles: The source definitions for this expression
        target_entity_roles: The target definitions for this expression
        support_definition: The support definition for this expression
        plate_children: A list of children for the plate
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return execute(
        CreateNaturalEventCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "label": label,
                "sourceEntityRoles": source_entity_roles,
                "targetEntityRoles": target_entity_roles,
                "supportDefinition": support_definition,
                "plateChildren": plate_children,
            }
        },
        rath=rath,
    ).create_natural_event_category


async def aupdate_natural_event_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    support_definition: Optional[CategoryDefinitionInput] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEventCategory:
    """UpdateNaturalEventCategory

    Update an existing natural event category

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional ID reference to an associated image
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: The label/name of the expression
        source_entity_roles: The source definitions for this expression
        target_entity_roles: The target definitions for this expression
        support_definition: The support definition for this expression
        plate_children: A list of children for the plate
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return (
        await aexecute(
            UpdateNaturalEventCategoryMutation,
            {
                "input": {
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "id": id,
                    "label": label,
                    "sourceEntityRoles": source_entity_roles,
                    "targetEntityRoles": target_entity_roles,
                    "supportDefinition": support_definition,
                    "plateChildren": plate_children,
                }
            },
            rath=rath,
        )
    ).update_natural_event_category


def update_natural_event_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    support_definition: Optional[CategoryDefinitionInput] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    rath: Optional[KraphRath] = None,
) -> NaturalEventCategory:
    """UpdateNaturalEventCategory

    Update an existing natural event category

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional ID reference to an associated image
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: The label/name of the expression
        source_entity_roles: The source definitions for this expression
        target_entity_roles: The target definitions for this expression
        support_definition: The support definition for this expression
        plate_children: A list of children for the plate
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return execute(
        UpdateNaturalEventCategoryMutation,
        {
            "input": {
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "id": id,
                "label": label,
                "sourceEntityRoles": source_entity_roles,
                "targetEntityRoles": target_entity_roles,
                "supportDefinition": support_definition,
                "plateChildren": plate_children,
            }
        },
        rath=rath,
    ).update_natural_event_category


async def acreate_node_query(
    graph: IDCoercible,
    name: str,
    query: CypherCoercible,
    kind: ViewKind,
    description: Optional[str] = None,
    columns: Optional[Iterable[ColumnInput]] = None,
    test_against: Optional[IDCoercible] = None,
    relevant_for: Optional[Iterable[IDCoercible]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> NodeQuery:
    """CreateNodeQuery

    Create a new node query

    Args:
        graph: The ID of the ontology this expression belongs to. If not provided, uses default ontology
        name: The label/name of the expression
        query: The label/name of the expression
        description: A detailed description of the expression
        kind: The kind/type of this expression
        columns: The columns (if ViewKind is Table)
        test_against: The node to test against
        relevant_for: The list of categories this expression is relevant for
        pin: Whether to pin this expression for the current user
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return (
        await aexecute(
            CreateNodeQueryMutation,
            {
                "input": {
                    "graph": graph,
                    "name": name,
                    "query": query,
                    "description": description,
                    "kind": kind,
                    "columns": columns,
                    "testAgainst": test_against,
                    "relevantFor": relevant_for,
                    "pin": pin,
                }
            },
            rath=rath,
        )
    ).create_node_query


def create_node_query(
    graph: IDCoercible,
    name: str,
    query: CypherCoercible,
    kind: ViewKind,
    description: Optional[str] = None,
    columns: Optional[Iterable[ColumnInput]] = None,
    test_against: Optional[IDCoercible] = None,
    relevant_for: Optional[Iterable[IDCoercible]] = None,
    pin: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> NodeQuery:
    """CreateNodeQuery

    Create a new node query

    Args:
        graph: The ID of the ontology this expression belongs to. If not provided, uses default ontology
        name: The label/name of the expression
        query: The label/name of the expression
        description: A detailed description of the expression
        kind: The kind/type of this expression
        columns: The columns (if ViewKind is Table)
        test_against: The node to test against
        relevant_for: The list of categories this expression is relevant for
        pin: Whether to pin this expression for the current user
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return execute(
        CreateNodeQueryMutation,
        {
            "input": {
                "graph": graph,
                "name": name,
                "query": query,
                "description": description,
                "kind": kind,
                "columns": columns,
                "testAgainst": test_against,
                "relevantFor": relevant_for,
                "pin": pin,
            }
        },
        rath=rath,
    ).create_node_query


async def apin_node_query(
    id: IDCoercible, pin: bool, rath: Optional[KraphRath] = None
) -> NodeQuery:
    """PinNodeQuery

    Pin or unpin a node query

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        pin: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return (
        await aexecute(
            PinNodeQueryMutation, {"input": {"id": id, "pin": pin}}, rath=rath
        )
    ).pin_node_query


def pin_node_query(
    id: IDCoercible, pin: bool, rath: Optional[KraphRath] = None
) -> NodeQuery:
    """PinNodeQuery

    Pin or unpin a node query

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        pin: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return execute(
        PinNodeQueryMutation, {"input": {"id": id, "pin": pin}}, rath=rath
    ).pin_node_query


async def arecord_protocol_event(
    category: IDCoercible,
    external_id: Optional[str] = None,
    entity_sources: Optional[Iterable[NodeMapping]] = None,
    entity_targets: Optional[Iterable[NodeMapping]] = None,
    reagent_sources: Optional[Iterable[NodeMapping]] = None,
    reagent_targets: Optional[Iterable[NodeMapping]] = None,
    variables: Optional[Iterable[VariableMappingInput]] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEvent:
    """RecordProtocolEvent

    Record a new protocol event

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        external_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        entity_sources:  (required) (list)
        entity_targets:  (required) (list)
        reagent_sources:  (required) (list)
        reagent_targets:  (required) (list)
        variables:  (required) (list)
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEvent
    """
    return (
        await aexecute(
            RecordProtocolEventMutation,
            {
                "input": {
                    "category": category,
                    "externalId": external_id,
                    "entitySources": entity_sources,
                    "entityTargets": entity_targets,
                    "reagentSources": reagent_sources,
                    "reagentTargets": reagent_targets,
                    "variables": variables,
                    "validFrom": valid_from,
                    "validTo": valid_to,
                }
            },
            rath=rath,
        )
    ).record_protocol_event


def record_protocol_event(
    category: IDCoercible,
    external_id: Optional[str] = None,
    entity_sources: Optional[Iterable[NodeMapping]] = None,
    entity_targets: Optional[Iterable[NodeMapping]] = None,
    reagent_sources: Optional[Iterable[NodeMapping]] = None,
    reagent_targets: Optional[Iterable[NodeMapping]] = None,
    variables: Optional[Iterable[VariableMappingInput]] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEvent:
    """RecordProtocolEvent

    Record a new protocol event

    Args:
        category: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        external_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        entity_sources:  (required) (list)
        entity_targets:  (required) (list)
        reagent_sources:  (required) (list)
        reagent_targets:  (required) (list)
        variables:  (required) (list)
        valid_from: Date with time (isoformat)
        valid_to: Date with time (isoformat)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEvent
    """
    return execute(
        RecordProtocolEventMutation,
        {
            "input": {
                "category": category,
                "externalId": external_id,
                "entitySources": entity_sources,
                "entityTargets": entity_targets,
                "reagentSources": reagent_sources,
                "reagentTargets": reagent_targets,
                "variables": variables,
                "validFrom": valid_from,
                "validTo": valid_to,
            }
        },
        rath=rath,
    ).record_protocol_event


async def acreate_protocol_event_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    source_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    variable_definitions: Optional[Iterable[VariableDefinitionInput]] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEventCategory:
    """CreateProtocolEventCategory

    Create a new protocol event category

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        plate_children: A list of children for the plate
        source_entity_roles: The source definitions for this expression
        source_reagent_roles: The target definitions for this expression
        target_entity_roles: The target definitions for this expression
        target_reagent_roles: The target definitions for this expression
        variable_definitions: The variable definitions for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return (
        await aexecute(
            CreateProtocolEventCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "label": label,
                    "plateChildren": plate_children,
                    "sourceEntityRoles": source_entity_roles,
                    "sourceReagentRoles": source_reagent_roles,
                    "targetEntityRoles": target_entity_roles,
                    "targetReagentRoles": target_reagent_roles,
                    "variableDefinitions": variable_definitions,
                }
            },
            rath=rath,
        )
    ).create_protocol_event_category


def create_protocol_event_category(
    graph: IDCoercible,
    label: str,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    source_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    variable_definitions: Optional[Iterable[VariableDefinitionInput]] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEventCategory:
    """CreateProtocolEventCategory

    Create a new protocol event category

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        label: The label/name of the expression
        plate_children: A list of children for the plate
        source_entity_roles: The source definitions for this expression
        source_reagent_roles: The target definitions for this expression
        target_entity_roles: The target definitions for this expression
        target_reagent_roles: The target definitions for this expression
        variable_definitions: The variable definitions for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return execute(
        CreateProtocolEventCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "label": label,
                "plateChildren": plate_children,
                "sourceEntityRoles": source_entity_roles,
                "sourceReagentRoles": source_reagent_roles,
                "targetEntityRoles": target_entity_roles,
                "targetReagentRoles": target_reagent_roles,
                "variableDefinitions": variable_definitions,
            }
        },
        rath=rath,
    ).create_protocol_event_category


async def aupdate_protocol_event_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    source_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    variable_definitions: Optional[Iterable[VariableDefinitionInput]] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEventCategory:
    """UpdateProtocolEventCategory

    Update an existing protocol event category

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional ID reference to an associated image
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: The label/name of the expression
        plate_children: A list of children for the plate
        source_entity_roles: The source definitions for this expression
        source_reagent_roles: The target definitions for this expression
        target_entity_roles: The target definitions for this expression
        target_reagent_roles: The target definitions for this expression
        variable_definitions: The variable definitions for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return (
        await aexecute(
            UpdateProtocolEventCategoryMutation,
            {
                "input": {
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "positionX": position_x,
                    "positionY": position_y,
                    "height": height,
                    "width": width,
                    "id": id,
                    "label": label,
                    "plateChildren": plate_children,
                    "sourceEntityRoles": source_entity_roles,
                    "sourceReagentRoles": source_reagent_roles,
                    "targetEntityRoles": target_entity_roles,
                    "targetReagentRoles": target_reagent_roles,
                    "variableDefinitions": variable_definitions,
                }
            },
            rath=rath,
        )
    ).update_protocol_event_category


def update_protocol_event_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    position_x: Optional[float] = None,
    position_y: Optional[float] = None,
    height: Optional[float] = None,
    width: Optional[float] = None,
    label: Optional[str] = None,
    plate_children: Optional[Iterable[PlateChildInput]] = None,
    source_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    source_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    target_entity_roles: Optional[Iterable[EntityRoleDefinitionInput]] = None,
    target_reagent_roles: Optional[Iterable[ReagentRoleDefinitionInput]] = None,
    variable_definitions: Optional[Iterable[VariableDefinitionInput]] = None,
    rath: Optional[KraphRath] = None,
) -> ProtocolEventCategory:
    """UpdateProtocolEventCategory

    Update an existing protocol event category

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional ID reference to an associated image
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        position_x: An optional x position for the ontology node
        position_y: An optional y position for the ontology node
        height: An optional height for the ontology node
        width: An optional width for the ontology node
        id: The ID of the expression to update
        label: The label/name of the expression
        plate_children: A list of children for the plate
        source_entity_roles: The source definitions for this expression
        source_reagent_roles: The target definitions for this expression
        target_entity_roles: The target definitions for this expression
        target_reagent_roles: The target definitions for this expression
        variable_definitions: The variable definitions for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return execute(
        UpdateProtocolEventCategoryMutation,
        {
            "input": {
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "positionX": position_x,
                "positionY": position_y,
                "height": height,
                "width": width,
                "id": id,
                "label": label,
                "plateChildren": plate_children,
                "sourceEntityRoles": source_entity_roles,
                "sourceReagentRoles": source_reagent_roles,
                "targetEntityRoles": target_entity_roles,
                "targetReagentRoles": target_reagent_roles,
                "variableDefinitions": variable_definitions,
            }
        },
        rath=rath,
    ).update_protocol_event_category


async def acreate_reagent(
    reagent_category: IDCoercible,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    set_active: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Reagent:
    """CreateReagent

    Create a new entity

    Args:
        reagent_category: The ID of the kind (LinkedExpression) to create the entity from
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        set_active: Set the reagent as active
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Reagent
    """
    return (
        await aexecute(
            CreateReagentMutation,
            {
                "input": {
                    "reagentCategory": reagent_category,
                    "name": name,
                    "externalId": external_id,
                    "setActive": set_active,
                }
            },
            rath=rath,
        )
    ).create_reagent


def create_reagent(
    reagent_category: IDCoercible,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    set_active: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> Reagent:
    """CreateReagent

    Create a new entity

    Args:
        reagent_category: The ID of the kind (LinkedExpression) to create the entity from
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        set_active: Set the reagent as active
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Reagent
    """
    return execute(
        CreateReagentMutation,
        {
            "input": {
                "reagentCategory": reagent_category,
                "name": name,
                "externalId": external_id,
                "setActive": set_active,
            }
        },
        rath=rath,
    ).create_reagent


async def acreate_relation(
    source: IDCoercible,
    target: IDCoercible,
    category: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Relation:
    """CreateRelation

    Create a new relation between entities

    Args:
        source: ID of the left entity (format: graph:id)
        target: ID of the right entity (format: graph:id)
        category: ID of the relation category (LinkedExpression)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Relation
    """
    return (
        await aexecute(
            CreateRelationMutation,
            {
                "input": {
                    "source": source,
                    "target": target,
                    "category": category,
                    "context": context,
                }
            },
            rath=rath,
        )
    ).create_relation


def create_relation(
    source: IDCoercible,
    target: IDCoercible,
    category: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Relation:
    """CreateRelation

    Create a new relation between entities

    Args:
        source: ID of the left entity (format: graph:id)
        target: ID of the right entity (format: graph:id)
        category: ID of the relation category (LinkedExpression)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Relation
    """
    return execute(
        CreateRelationMutation,
        {
            "input": {
                "source": source,
                "target": target,
                "category": category,
                "context": context,
            }
        },
        rath=rath,
    ).create_relation


async def acreate_scatter_plot(
    query: IDCoercible,
    name: str,
    id_column: str,
    x_column: str,
    y_column: str,
    description: Optional[str] = None,
    x_id_column: Optional[str] = None,
    y_id_column: Optional[str] = None,
    size_column: Optional[str] = None,
    color_column: Optional[str] = None,
    shape_column: Optional[str] = None,
    test_against: Optional[IDCoercible] = None,
    rath: Optional[KraphRath] = None,
) -> ScatterPlot:
    """CreateScatterPlot

    Create a new scatter plot

    Args:
        query: The query to use
        name: The label/name of the expression
        description: A detailed description of the expression
        id_column: The column to use for the ID of the points
        x_column: The column to use for the x-axis
        x_id_column: The column to use for the x-axis ID (node, or edge)
        y_column: The column to use for the y-axis
        y_id_column: The column to use for the y-axis ID (node, or edge)
        size_column: The column to use for the size of the points
        color_column: The column to use for the color of the points
        shape_column: The column to use for the shape of the points
        test_against: The graph to test against
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ScatterPlot
    """
    return (
        await aexecute(
            CreateScatterPlotMutation,
            {
                "input": {
                    "query": query,
                    "name": name,
                    "description": description,
                    "idColumn": id_column,
                    "xColumn": x_column,
                    "xIdColumn": x_id_column,
                    "yColumn": y_column,
                    "yIdColumn": y_id_column,
                    "sizeColumn": size_column,
                    "colorColumn": color_column,
                    "shapeColumn": shape_column,
                    "testAgainst": test_against,
                }
            },
            rath=rath,
        )
    ).create_scatter_plot


def create_scatter_plot(
    query: IDCoercible,
    name: str,
    id_column: str,
    x_column: str,
    y_column: str,
    description: Optional[str] = None,
    x_id_column: Optional[str] = None,
    y_id_column: Optional[str] = None,
    size_column: Optional[str] = None,
    color_column: Optional[str] = None,
    shape_column: Optional[str] = None,
    test_against: Optional[IDCoercible] = None,
    rath: Optional[KraphRath] = None,
) -> ScatterPlot:
    """CreateScatterPlot

    Create a new scatter plot

    Args:
        query: The query to use
        name: The label/name of the expression
        description: A detailed description of the expression
        id_column: The column to use for the ID of the points
        x_column: The column to use for the x-axis
        x_id_column: The column to use for the x-axis ID (node, or edge)
        y_column: The column to use for the y-axis
        y_id_column: The column to use for the y-axis ID (node, or edge)
        size_column: The column to use for the size of the points
        color_column: The column to use for the color of the points
        shape_column: The column to use for the shape of the points
        test_against: The graph to test against
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ScatterPlot
    """
    return execute(
        CreateScatterPlotMutation,
        {
            "input": {
                "query": query,
                "name": name,
                "description": description,
                "idColumn": id_column,
                "xColumn": x_column,
                "xIdColumn": x_id_column,
                "yColumn": y_column,
                "yIdColumn": y_id_column,
                "sizeColumn": size_column,
                "colorColumn": color_column,
                "shapeColumn": shape_column,
                "testAgainst": test_against,
            }
        },
        rath=rath,
    ).create_scatter_plot


async def adelete_scatter_plot(id: IDCoercible, rath: Optional[KraphRath] = None) -> ID:
    """DeleteScatterPlot

    Delete an existing scatter plot

    Args:
        id: The ID of the expression to delete
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ID
    """
    return (
        await aexecute(DeleteScatterPlotMutation, {"input": {"id": id}}, rath=rath)
    ).delete_scatter_plot


def delete_scatter_plot(id: IDCoercible, rath: Optional[KraphRath] = None) -> ID:
    """DeleteScatterPlot

    Delete an existing scatter plot

    Args:
        id: The ID of the expression to delete
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ID
    """
    return execute(
        DeleteScatterPlotMutation, {"input": {"id": id}}, rath=rath
    ).delete_scatter_plot


async def acreate_structure(
    structure: StructureString,
    graph: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Structure:
    """CreateStructure

    Create a new structure

    Args:
        structure: The `StructureString` scalar type represents a string with a structure (required)
        graph: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return (
        await aexecute(
            CreateStructureMutation,
            {"input": {"structure": structure, "graph": graph, "context": context}},
            rath=rath,
        )
    ).create_structure


def create_structure(
    structure: StructureString,
    graph: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> Structure:
    """CreateStructure

    Create a new structure

    Args:
        structure: The `StructureString` scalar type represents a string with a structure (required)
        graph: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return execute(
        CreateStructureMutation,
        {"input": {"structure": structure, "graph": graph, "context": context}},
        rath=rath,
    ).create_structure


async def acreate_structure_category(
    graph: IDCoercible,
    identifier: StructureIdentifierCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[RemoteUpload] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> StructureCategory:
    """CreateStructureCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        identifier: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return (
        await aexecute(
            CreateStructureCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "identifier": identifier,
                }
            },
            rath=rath,
        )
    ).create_structure_category


def create_structure_category(
    graph: IDCoercible,
    identifier: StructureIdentifierCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[RemoteUpload] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> StructureCategory:
    """CreateStructureCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        identifier: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return execute(
        CreateStructureCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "identifier": identifier,
            }
        },
        rath=rath,
    ).create_structure_category


async def aupdate_structure_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    identifier: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> StructureCategory:
    """UpdateStructureCategory

    Update an existing expression

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        id: The ID of the expression to update
        identifier: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return (
        await aexecute(
            UpdateStructureCategoryMutation,
            {
                "input": {
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "id": id,
                    "identifier": identifier,
                }
            },
            rath=rath,
        )
    ).update_structure_category


def update_structure_category(
    id: IDCoercible,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    identifier: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> StructureCategory:
    """UpdateStructureCategory

    Update an existing expression

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        id: The ID of the expression to update
        identifier: The label/name of the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return execute(
        UpdateStructureCategoryMutation,
        {
            "input": {
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "id": id,
                "identifier": identifier,
            }
        },
        rath=rath,
    ).update_structure_category


async def acreate_structure_relation(
    source: IDCoercible,
    target: IDCoercible,
    category: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelation:
    """CreateStructureRelation

    Create a new relation between entities

    Args:
        source: ID of the left entity (format: graph:id)
        target: ID of the right entity (format: graph:id)
        category: ID of the relation category (LinkedExpression)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelation
    """
    return (
        await aexecute(
            CreateStructureRelationMutation,
            {
                "input": {
                    "source": source,
                    "target": target,
                    "category": category,
                    "context": context,
                }
            },
            rath=rath,
        )
    ).create_structure_relation


def create_structure_relation(
    source: IDCoercible,
    target: IDCoercible,
    category: IDCoercible,
    context: Optional[ContextInput] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelation:
    """CreateStructureRelation

    Create a new relation between entities

    Args:
        source: ID of the left entity (format: graph:id)
        target: ID of the right entity (format: graph:id)
        category: ID of the relation category (LinkedExpression)
        context: The context of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelation
    """
    return execute(
        CreateStructureRelationMutation,
        {
            "input": {
                "source": source,
                "target": target,
                "category": category,
                "context": context,
            }
        },
        rath=rath,
    ).create_structure_relation


async def acreate_structure_relation_category(
    graph: IDCoercible,
    label: str,
    source_definition: StructureCategoryDefinitionInput,
    target_definition: StructureCategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelationCategory:
    """CreateStructureRelationCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        source_definition: The source definition for this expression
        target_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return (
        await aexecute(
            CreateStructureRelationCategoryMutation,
            {
                "input": {
                    "graph": graph,
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "sequence": sequence,
                    "autoCreateSequence": auto_create_sequence,
                    "label": label,
                    "sourceDefinition": source_definition,
                    "targetDefinition": target_definition,
                }
            },
            rath=rath,
        )
    ).create_structure_relation_category


def create_structure_relation_category(
    graph: IDCoercible,
    label: str,
    source_definition: StructureCategoryDefinitionInput,
    target_definition: StructureCategoryDefinitionInput,
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    sequence: Optional[IDCoercible] = None,
    auto_create_sequence: Optional[bool] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelationCategory:
    """CreateStructureRelationCategory

    Create a new expression

    Args:
        graph: The ID of the graph this expression belongs to. If not provided, uses default ontology
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        sequence: The ID of the sequence this category will get internal_ids from
        auto_create_sequence: Whether to create a sequence if it does not exist
        label: The label/name of the expression
        source_definition: The source definition for this expression
        target_definition: The target definition for this expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return execute(
        CreateStructureRelationCategoryMutation,
        {
            "input": {
                "graph": graph,
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "sequence": sequence,
                "autoCreateSequence": auto_create_sequence,
                "label": label,
                "sourceDefinition": source_definition,
                "targetDefinition": target_definition,
            }
        },
        rath=rath,
    ).create_structure_relation_category


async def aupdate_structure_relation_category(
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    label: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelationCategory:
    """UpdateStructureRelationCategory

    Update an existing expression

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        label: New label for the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return (
        await aexecute(
            UpdateStructureRelationCategoryMutation,
            {
                "input": {
                    "description": description,
                    "purl": purl,
                    "color": color,
                    "image": image,
                    "tags": tags,
                    "pin": pin,
                    "label": label,
                }
            },
            rath=rath,
        )
    ).update_structure_relation_category


def update_structure_relation_category(
    description: Optional[str] = None,
    purl: Optional[str] = None,
    color: Optional[Iterable[int]] = None,
    image: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    pin: Optional[bool] = None,
    label: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> StructureRelationCategory:
    """UpdateStructureRelationCategory

    Update an existing expression

    Args:
        description: A detailed description of the expression
        purl: Permanent URL identifier for the expression
        color: RGBA color values as list of 3 or 4 integers
        image: An optional image associated with this expression
        tags: A list of tags associated with this expression
        pin: Whether this expression should be pinned or not
        label: New label for the expression
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return execute(
        UpdateStructureRelationCategoryMutation,
        {
            "input": {
                "description": description,
                "purl": purl,
                "color": color,
                "image": image,
                "tags": tags,
                "pin": pin,
                "label": label,
            }
        },
        rath=rath,
    ).update_structure_relation_category


async def acreate_toldyouso(
    reason: Optional[str] = None,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    context: Optional[ContextInput] = None,
    valid_from: Optional[str] = None,
    valid_to: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> Structure:
    """CreateToldyouso

    Create a new 'told you so' supporting structure

    Args:
        reason: The reason why you made this assumption
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        context: The context of the measurement
        valid_from: The start date of the measurement
        valid_to: The end date of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return (
        await aexecute(
            CreateToldyousoMutation,
            {
                "input": {
                    "reason": reason,
                    "name": name,
                    "externalId": external_id,
                    "context": context,
                    "validFrom": valid_from,
                    "validTo": valid_to,
                }
            },
            rath=rath,
        )
    ).create_toldyouso


def create_toldyouso(
    reason: Optional[str] = None,
    name: Optional[str] = None,
    external_id: Optional[str] = None,
    context: Optional[ContextInput] = None,
    valid_from: Optional[str] = None,
    valid_to: Optional[str] = None,
    rath: Optional[KraphRath] = None,
) -> Structure:
    """CreateToldyouso

    Create a new 'told you so' supporting structure

    Args:
        reason: The reason why you made this assumption
        name: Optional name for the entity
        external_id: An optional external ID for the entity (will upsert if exists)
        context: The context of the measurement
        valid_from: The start date of the measurement
        valid_to: The end date of the measurement
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return execute(
        CreateToldyousoMutation,
        {
            "input": {
                "reason": reason,
                "name": name,
                "externalId": external_id,
                "context": context,
                "validFrom": valid_from,
                "validTo": valid_to,
            }
        },
        rath=rath,
    ).create_toldyouso


async def arequest_upload(
    key: str, datalayer: str, rath: Optional[KraphRath] = None
) -> PresignedPostCredentials:
    """RequestUpload

    Request a new file upload

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        PresignedPostCredentials
    """
    return (
        await aexecute(
            RequestUploadMutation,
            {"input": {"key": key, "datalayer": datalayer}},
            rath=rath,
        )
    ).request_upload


def request_upload(
    key: str, datalayer: str, rath: Optional[KraphRath] = None
) -> PresignedPostCredentials:
    """RequestUpload

    Request a new file upload

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        PresignedPostCredentials
    """
    return execute(
        RequestUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_upload


async def aget_entity(id: ID, rath: Optional[KraphRath] = None) -> Entity:
    """GetEntity


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return (await aexecute(GetEntityQuery, {"id": id}, rath=rath)).entity


def get_entity(id: ID, rath: Optional[KraphRath] = None) -> Entity:
    """GetEntity


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return execute(GetEntityQuery, {"id": id}, rath=rath).entity


async def aget_entity_for_category_and_external_id(
    category: ID, external_id: str, rath: Optional[KraphRath] = None
) -> Entity:
    """GetEntityForCategoryAndExternalID


    Args:
        category (ID): No description
        external_id (str): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return (
        await aexecute(
            GetEntityForCategoryAndExternalIDQuery,
            {"category": category, "externalId": external_id},
            rath=rath,
        )
    ).get_entity_by_category_and_external_id


def get_entity_for_category_and_external_id(
    category: ID, external_id: str, rath: Optional[KraphRath] = None
) -> Entity:
    """GetEntityForCategoryAndExternalID


    Args:
        category (ID): No description
        external_id (str): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Entity
    """
    return execute(
        GetEntityForCategoryAndExternalIDQuery,
        {"category": category, "externalId": external_id},
        rath=rath,
    ).get_entity_by_category_and_external_id


async def asearch_entities(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchEntitiesQueryOptions, ...]:
    """SearchEntities

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchEntitiesQueryNodes]
    """
    return (
        await aexecute(
            SearchEntitiesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_entities(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchEntitiesQueryOptions, ...]:
    """SearchEntities

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchEntitiesQueryNodes]
    """
    return execute(
        SearchEntitiesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_entities(
    filters: Optional[EntityFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListEntity, ...]:
    """ListEntities


    Args:
        filters (Optional[EntityFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListEntity]
    """
    return (
        await aexecute(
            ListEntitiesQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).entities


def list_entities(
    filters: Optional[EntityFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListEntity, ...]:
    """ListEntities


    Args:
        filters (Optional[EntityFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListEntity]
    """
    return execute(
        ListEntitiesQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).entities


async def aget_entity_category(
    id: ID, rath: Optional[KraphRath] = None
) -> EntityCategory:
    """GetEntityCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return (
        await aexecute(GetEntityCategoryQuery, {"id": id}, rath=rath)
    ).entity_category


def get_entity_category(id: ID, rath: Optional[KraphRath] = None) -> EntityCategory:
    """GetEntityCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        EntityCategory
    """
    return execute(GetEntityCategoryQuery, {"id": id}, rath=rath).entity_category


async def asearch_entity_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchEntityCategoryQueryOptions, ...]:
    """SearchEntityCategory

    List of all generic categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchEntityCategoryQueryEntitycategories]
    """
    return (
        await aexecute(
            SearchEntityCategoryQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_entity_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchEntityCategoryQueryOptions, ...]:
    """SearchEntityCategory

    List of all generic categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchEntityCategoryQueryEntitycategories]
    """
    return execute(
        SearchEntityCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_entity_category(
    filters: Optional[EntityCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListEntityCategory, ...]:
    """ListEntityCategory

    List of all generic categories

    Args:
        filters (Optional[EntityCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListEntityCategory]
    """
    return (
        await aexecute(
            ListEntityCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).entity_categories


def list_entity_category(
    filters: Optional[EntityCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListEntityCategory, ...]:
    """ListEntityCategory

    List of all generic categories

    Args:
        filters (Optional[EntityCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListEntityCategory]
    """
    return execute(
        ListEntityCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).entity_categories


async def aglobal_search(
    search: str, rath: Optional[KraphRath] = None
) -> GlobalSearchQuery:
    """GlobalSearch

    entityCategories: List of all generic categories
    relationCategories: List of all relation categories
    measurementCategories: List of all measurement categories
    structureCategories: List of all structure categories

    Args:
        search (str): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GlobalSearchQuery
    """
    return await aexecute(GlobalSearchQuery, {"search": search}, rath=rath)


def global_search(search: str, rath: Optional[KraphRath] = None) -> GlobalSearchQuery:
    """GlobalSearch

    entityCategories: List of all generic categories
    relationCategories: List of all relation categories
    measurementCategories: List of all measurement categories
    structureCategories: List of all structure categories

    Args:
        search (str): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GlobalSearchQuery
    """
    return execute(GlobalSearchQuery, {"search": search}, rath=rath)


async def aget_graph(id: ID, rath: Optional[KraphRath] = None) -> Graph:
    """GetGraph


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return (await aexecute(GetGraphQuery, {"id": id}, rath=rath)).graph


def get_graph(id: ID, rath: Optional[KraphRath] = None) -> Graph:
    """GetGraph


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Graph
    """
    return execute(GetGraphQuery, {"id": id}, rath=rath).graph


async def asearch_graphs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchGraphsQueryOptions, ...]:
    """SearchGraphs

    List of all knowledge graphs

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchGraphsQueryGraphs]
    """
    return (
        await aexecute(
            SearchGraphsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_graphs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchGraphsQueryOptions, ...]:
    """SearchGraphs

    List of all knowledge graphs

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchGraphsQueryGraphs]
    """
    return execute(
        SearchGraphsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_graphs(
    filters: Optional[GraphFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListGraph, ...]:
    """ListGraphs

    List of all knowledge graphs

    Args:
        filters (Optional[GraphFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListGraph]
    """
    return (
        await aexecute(
            ListGraphsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).graphs


def list_graphs(
    filters: Optional[GraphFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListGraph, ...]:
    """ListGraphs

    List of all knowledge graphs

    Args:
        filters (Optional[GraphFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListGraph]
    """
    return execute(
        ListGraphsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).graphs


async def aget_graph_query(id: ID, rath: Optional[KraphRath] = None) -> GraphQuery:
    """GetGraphQuery


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return (await aexecute(GetGraphQueryQuery, {"id": id}, rath=rath)).graph_query


def get_graph_query(id: ID, rath: Optional[KraphRath] = None) -> GraphQuery:
    """GetGraphQuery


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        GraphQuery
    """
    return execute(GetGraphQueryQuery, {"id": id}, rath=rath).graph_query


async def asearch_graph_queries(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchGraphQueriesQueryOptions, ...]:
    """SearchGraphQueries

    List of all graph queries

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchGraphQueriesQueryGraphqueries]
    """
    return (
        await aexecute(
            SearchGraphQueriesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_graph_queries(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchGraphQueriesQueryOptions, ...]:
    """SearchGraphQueries

    List of all graph queries

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchGraphQueriesQueryGraphqueries]
    """
    return execute(
        SearchGraphQueriesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_graph_queries(
    filters: Optional[GraphQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListGraphQuery, ...]:
    """ListGraphQueries

    List of all graph queries

    Args:
        filters (Optional[GraphQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListGraphQuery]
    """
    return (
        await aexecute(
            ListGraphQueriesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).graph_queries


def list_graph_queries(
    filters: Optional[GraphQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListGraphQuery, ...]:
    """ListGraphQueries

    List of all graph queries

    Args:
        filters (Optional[GraphQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListGraphQuery]
    """
    return execute(
        ListGraphQueriesQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).graph_queries


async def alist_prerendered_graph_queries(
    filters: Optional[GraphQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[GraphQuery, ...]:
    """ListPrerenderedGraphQueries

    List of all graph queries

    Args:
        filters (Optional[GraphQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[GraphQuery]
    """
    return (
        await aexecute(
            ListPrerenderedGraphQueriesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).graph_queries


def list_prerendered_graph_queries(
    filters: Optional[GraphQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[GraphQuery, ...]:
    """ListPrerenderedGraphQueries

    List of all graph queries

    Args:
        filters (Optional[GraphQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[GraphQuery]
    """
    return execute(
        ListPrerenderedGraphQueriesQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).graph_queries


async def aget_measurement(id: ID, rath: Optional[KraphRath] = None) -> Measurement:
    """GetMeasurement


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Measurement
    """
    return (await aexecute(GetMeasurementQuery, {"id": id}, rath=rath)).measurement


def get_measurement(id: ID, rath: Optional[KraphRath] = None) -> Measurement:
    """GetMeasurement


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Measurement
    """
    return execute(GetMeasurementQuery, {"id": id}, rath=rath).measurement


async def asearch_measurements(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMeasurementsQueryOptions, ...]:
    """SearchMeasurements


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMeasurementsQueryMeasurements]
    """
    return (
        await aexecute(
            SearchMeasurementsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_measurements(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMeasurementsQueryOptions, ...]:
    """SearchMeasurements


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMeasurementsQueryMeasurements]
    """
    return execute(
        SearchMeasurementsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_measurment_category(
    id: ID, rath: Optional[KraphRath] = None
) -> MeasurementCategory:
    """GetMeasurmentCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MeasurementCategory
    """
    return (
        await aexecute(GetMeasurmentCategoryQuery, {"id": id}, rath=rath)
    ).measurement_category


def get_measurment_category(
    id: ID, rath: Optional[KraphRath] = None
) -> MeasurementCategory:
    """GetMeasurmentCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MeasurementCategory
    """
    return execute(
        GetMeasurmentCategoryQuery, {"id": id}, rath=rath
    ).measurement_category


async def asearch_measurment_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMeasurmentCategoryQueryOptions, ...]:
    """SearchMeasurmentCategory

    List of all measurement categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMeasurmentCategoryQueryMeasurementcategories]
    """
    return (
        await aexecute(
            SearchMeasurmentCategoryQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_measurment_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMeasurmentCategoryQueryOptions, ...]:
    """SearchMeasurmentCategory

    List of all measurement categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMeasurmentCategoryQueryMeasurementcategories]
    """
    return execute(
        SearchMeasurmentCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_measurment_category(
    filters: Optional[MeasurementCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListMeasurementCategory, ...]:
    """ListMeasurmentCategory

    List of all measurement categories

    Args:
        filters (Optional[MeasurementCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListMeasurementCategory]
    """
    return (
        await aexecute(
            ListMeasurmentCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).measurement_categories


def list_measurment_category(
    filters: Optional[MeasurementCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListMeasurementCategory, ...]:
    """ListMeasurmentCategory

    List of all measurement categories

    Args:
        filters (Optional[MeasurementCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListMeasurementCategory]
    """
    return execute(
        ListMeasurmentCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).measurement_categories


async def aget_metric(id: ID, rath: Optional[KraphRath] = None) -> Metric:
    """GetMetric


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Metric
    """
    return (await aexecute(GetMetricQuery, {"id": id}, rath=rath)).metric


def get_metric(id: ID, rath: Optional[KraphRath] = None) -> Metric:
    """GetMetric


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Metric
    """
    return execute(GetMetricQuery, {"id": id}, rath=rath).metric


async def asearch_metrics(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMetricsQueryOptions, ...]:
    """SearchMetrics


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMetricsQueryMetrics]
    """
    return (
        await aexecute(
            SearchMetricsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_metrics(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMetricsQueryOptions, ...]:
    """SearchMetrics


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMetricsQueryMetrics]
    """
    return execute(
        SearchMetricsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_metrics(
    filters: Optional[MetricFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListMetric, ...]:
    """ListMetrics


    Args:
        filters (Optional[MetricFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListMetric]
    """
    return (
        await aexecute(
            ListMetricsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).metrics


def list_metrics(
    filters: Optional[MetricFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListMetric, ...]:
    """ListMetrics


    Args:
        filters (Optional[MetricFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListMetric]
    """
    return execute(
        ListMetricsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).metrics


async def aget_metric_category(
    id: ID, rath: Optional[KraphRath] = None
) -> MetricCategory:
    """GetMetricCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MetricCategory
    """
    return (
        await aexecute(GetMetricCategoryQuery, {"id": id}, rath=rath)
    ).metric_category


def get_metric_category(id: ID, rath: Optional[KraphRath] = None) -> MetricCategory:
    """GetMetricCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        MetricCategory
    """
    return execute(GetMetricCategoryQuery, {"id": id}, rath=rath).metric_category


async def asearch_metric_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMetricCategoryQueryOptions, ...]:
    """SearchMetricCategory

    List of all metric categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMetricCategoryQueryMetriccategories]
    """
    return (
        await aexecute(
            SearchMetricCategoryQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_metric_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchMetricCategoryQueryOptions, ...]:
    """SearchMetricCategory

    List of all metric categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchMetricCategoryQueryMetriccategories]
    """
    return execute(
        SearchMetricCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_model(id: ID, rath: Optional[KraphRath] = None) -> Model:
    """GetModel


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Model
    """
    return (await aexecute(GetModelQuery, {"id": id}, rath=rath)).model


def get_model(id: ID, rath: Optional[KraphRath] = None) -> Model:
    """GetModel


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Model
    """
    return execute(GetModelQuery, {"id": id}, rath=rath).model


async def asearch_models(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchModelsQueryOptions, ...]:
    """SearchModels

    List of all deep learning models (e.g. neural networks)

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchModelsQueryModels]
    """
    return (
        await aexecute(
            SearchModelsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_models(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchModelsQueryOptions, ...]:
    """SearchModels

    List of all deep learning models (e.g. neural networks)

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchModelsQueryModels]
    """
    return execute(
        SearchModelsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_natural_event(id: ID, rath: Optional[KraphRath] = None) -> NaturalEvent:
    """GetNaturalEvent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEvent
    """
    return (await aexecute(GetNaturalEventQuery, {"id": id}, rath=rath)).natural_event


def get_natural_event(id: ID, rath: Optional[KraphRath] = None) -> NaturalEvent:
    """GetNaturalEvent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEvent
    """
    return execute(GetNaturalEventQuery, {"id": id}, rath=rath).natural_event


async def asearch_natural_events(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNaturalEventsQueryOptions, ...]:
    """SearchNaturalEvents


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNaturalEventsQueryNaturalevents]
    """
    return (
        await aexecute(
            SearchNaturalEventsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_natural_events(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNaturalEventsQueryOptions, ...]:
    """SearchNaturalEvents


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNaturalEventsQueryNaturalevents]
    """
    return execute(
        SearchNaturalEventsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_natural_event_category(
    id: ID, rath: Optional[KraphRath] = None
) -> NaturalEventCategory:
    """GetNaturalEventCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return (
        await aexecute(GetNaturalEventCategoryQuery, {"id": id}, rath=rath)
    ).natural_event_category


def get_natural_event_category(
    id: ID, rath: Optional[KraphRath] = None
) -> NaturalEventCategory:
    """GetNaturalEventCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NaturalEventCategory
    """
    return execute(
        GetNaturalEventCategoryQuery, {"id": id}, rath=rath
    ).natural_event_category


async def asearch_natural_event_categories(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNaturalEventCategoriesQueryOptions, ...]:
    """SearchNaturalEventCategories

    List of all natural event categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNaturalEventCategoriesQueryNaturaleventcategories]
    """
    return (
        await aexecute(
            SearchNaturalEventCategoriesQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_natural_event_categories(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNaturalEventCategoriesQueryOptions, ...]:
    """SearchNaturalEventCategories

    List of all natural event categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNaturalEventCategoriesQueryNaturaleventcategories]
    """
    return execute(
        SearchNaturalEventCategoriesQuery,
        {"search": search, "values": values},
        rath=rath,
    ).options


async def alist_natural_event_categories(
    filters: Optional[NaturalEventCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[NaturalEventCategory, ...]:
    """ListNaturalEventCategories

    List of all natural event categories

    Args:
        filters (Optional[NaturalEventCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[NaturalEventCategory]
    """
    return (
        await aexecute(
            ListNaturalEventCategoriesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).natural_event_categories


def list_natural_event_categories(
    filters: Optional[NaturalEventCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[NaturalEventCategory, ...]:
    """ListNaturalEventCategories

    List of all natural event categories

    Args:
        filters (Optional[NaturalEventCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[NaturalEventCategory]
    """
    return execute(
        ListNaturalEventCategoriesQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).natural_event_categories


async def aget_node(id: ID, rath: Optional[KraphRath] = None) -> Union[
    Annotated[
        Union[
            GetNodeQueryNodeBaseEntity,
            GetNodeQueryNodeBaseStructure,
            GetNodeQueryNodeBaseMetric,
            GetNodeQueryNodeBaseProtocolEvent,
            GetNodeQueryNodeBaseNaturalEvent,
            GetNodeQueryNodeBaseReagent,
        ],
        Field(discriminator="typename"),
    ],
    GetNodeQueryNodeBaseCatchAll,
]:
    """GetNode


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        DetailNode
    """
    return (await aexecute(GetNodeQuery, {"id": id}, rath=rath)).node


def get_node(id: ID, rath: Optional[KraphRath] = None) -> Union[
    Annotated[
        Union[
            GetNodeQueryNodeBaseEntity,
            GetNodeQueryNodeBaseStructure,
            GetNodeQueryNodeBaseMetric,
            GetNodeQueryNodeBaseProtocolEvent,
            GetNodeQueryNodeBaseNaturalEvent,
            GetNodeQueryNodeBaseReagent,
        ],
        Field(discriminator="typename"),
    ],
    GetNodeQueryNodeBaseCatchAll,
]:
    """GetNode


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        DetailNode
    """
    return execute(GetNodeQuery, {"id": id}, rath=rath).node


async def asearch_nodes(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNodesQueryOptions, ...]:
    """SearchNodes

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNodesQueryNodes]
    """
    return (
        await aexecute(
            SearchNodesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_nodes(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNodesQueryOptions, ...]:
    """SearchNodes

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNodesQueryNodes]
    """
    return execute(
        SearchNodesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def anode_categories(
    rath: Optional[KraphRath] = None,
) -> Tuple[
    Union[
        Annotated[
            Union[
                NodeCategoriesQueryNodecategoriesBaseMetricCategory,
                NodeCategoriesQueryNodecategoriesBaseStructureCategory,
                NodeCategoriesQueryNodecategoriesBaseProtocolEventCategory,
                NodeCategoriesQueryNodecategoriesBaseEntityCategory,
                NodeCategoriesQueryNodecategoriesBaseReagentCategory,
                NodeCategoriesQueryNodecategoriesBaseNaturalEventCategory,
            ],
            Field(discriminator="typename"),
        ],
        NodeCategoriesQueryNodecategoriesBaseCatchAll,
    ],
    ...,
]:
    """NodeCategories


    Args:
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[NodeCategory]
    """
    return (await aexecute(NodeCategoriesQuery, {}, rath=rath)).node_categories


def node_categories(
    rath: Optional[KraphRath] = None,
) -> Tuple[
    Union[
        Annotated[
            Union[
                NodeCategoriesQueryNodecategoriesBaseMetricCategory,
                NodeCategoriesQueryNodecategoriesBaseStructureCategory,
                NodeCategoriesQueryNodecategoriesBaseProtocolEventCategory,
                NodeCategoriesQueryNodecategoriesBaseEntityCategory,
                NodeCategoriesQueryNodecategoriesBaseReagentCategory,
                NodeCategoriesQueryNodecategoriesBaseNaturalEventCategory,
            ],
            Field(discriminator="typename"),
        ],
        NodeCategoriesQueryNodecategoriesBaseCatchAll,
    ],
    ...,
]:
    """NodeCategories


    Args:
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[NodeCategory]
    """
    return execute(NodeCategoriesQuery, {}, rath=rath).node_categories


async def aget_node_query(id: ID, rath: Optional[KraphRath] = None) -> NodeQuery:
    """GetNodeQuery


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return (await aexecute(GetNodeQueryQuery, {"id": id}, rath=rath)).node_query


def get_node_query(id: ID, rath: Optional[KraphRath] = None) -> NodeQuery:
    """GetNodeQuery


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        NodeQuery
    """
    return execute(GetNodeQueryQuery, {"id": id}, rath=rath).node_query


async def arender_node_query(
    id: ID, node_id: ID, rath: Optional[KraphRath] = None
) -> Union[Path, Table, Pairs]:
    """RenderNodeQuery

    Render a node query

    Args:
        id (ID): No description
        node_id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RenderNodeQueryQueryRendernodequery
    """
    return (
        await aexecute(RenderNodeQueryQuery, {"id": id, "nodeId": node_id}, rath=rath)
    ).render_node_query


def render_node_query(
    id: ID, node_id: ID, rath: Optional[KraphRath] = None
) -> Union[Path, Table, Pairs]:
    """RenderNodeQuery

    Render a node query

    Args:
        id (ID): No description
        node_id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RenderNodeQueryQueryRendernodequery
    """
    return execute(
        RenderNodeQueryQuery, {"id": id, "nodeId": node_id}, rath=rath
    ).render_node_query


async def asearch_node_queries(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNodeQueriesQueryOptions, ...]:
    """SearchNodeQueries

    List of all node queries

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNodeQueriesQueryNodequeries]
    """
    return (
        await aexecute(
            SearchNodeQueriesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_node_queries(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchNodeQueriesQueryOptions, ...]:
    """SearchNodeQueries

    List of all node queries

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchNodeQueriesQueryNodequeries]
    """
    return execute(
        SearchNodeQueriesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_node_queries(
    filters: Optional[NodeQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListNodeQuery, ...]:
    """ListNodeQueries

    List of all node queries

    Args:
        filters (Optional[NodeQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListNodeQuery]
    """
    return (
        await aexecute(
            ListNodeQueriesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).node_queries


def list_node_queries(
    filters: Optional[NodeQueryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListNodeQuery, ...]:
    """ListNodeQueries

    List of all node queries

    Args:
        filters (Optional[NodeQueryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListNodeQuery]
    """
    return execute(
        ListNodeQueriesQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).node_queries


async def aget_participant(id: ID, rath: Optional[KraphRath] = None) -> Participant:
    """GetParticipant


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Participant
    """
    return (await aexecute(GetParticipantQuery, {"id": id}, rath=rath)).participant


def get_participant(id: ID, rath: Optional[KraphRath] = None) -> Participant:
    """GetParticipant


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Participant
    """
    return execute(GetParticipantQuery, {"id": id}, rath=rath).participant


async def asearch_participants(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchParticipantsQueryOptions, ...]:
    """SearchParticipants


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchParticipantsQueryParticipants]
    """
    return (
        await aexecute(
            SearchParticipantsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_participants(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchParticipantsQueryOptions, ...]:
    """SearchParticipants


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchParticipantsQueryParticipants]
    """
    return execute(
        SearchParticipantsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_protocol_event(
    id: ID, rath: Optional[KraphRath] = None
) -> ProtocolEvent:
    """GetProtocolEvent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEvent
    """
    return (await aexecute(GetProtocolEventQuery, {"id": id}, rath=rath)).protocol_event


def get_protocol_event(id: ID, rath: Optional[KraphRath] = None) -> ProtocolEvent:
    """GetProtocolEvent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEvent
    """
    return execute(GetProtocolEventQuery, {"id": id}, rath=rath).protocol_event


async def asearch_protocol_events(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchProtocolEventsQueryOptions, ...]:
    """SearchProtocolEvents


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolEventsQueryProtocolevents]
    """
    return (
        await aexecute(
            SearchProtocolEventsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_protocol_events(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchProtocolEventsQueryOptions, ...]:
    """SearchProtocolEvents


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolEventsQueryProtocolevents]
    """
    return execute(
        SearchProtocolEventsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_protocol_event_category(
    id: ID, rath: Optional[KraphRath] = None
) -> ProtocolEventCategory:
    """GetProtocolEventCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return (
        await aexecute(GetProtocolEventCategoryQuery, {"id": id}, rath=rath)
    ).protocol_event_category


def get_protocol_event_category(
    id: ID, rath: Optional[KraphRath] = None
) -> ProtocolEventCategory:
    """GetProtocolEventCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ProtocolEventCategory
    """
    return execute(
        GetProtocolEventCategoryQuery, {"id": id}, rath=rath
    ).protocol_event_category


async def asearch_protocol_event_categories(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchProtocolEventCategoriesQueryOptions, ...]:
    """SearchProtocolEventCategories

    List of all protocol event categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolEventCategoriesQueryProtocoleventcategories]
    """
    return (
        await aexecute(
            SearchProtocolEventCategoriesQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_protocol_event_categories(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchProtocolEventCategoriesQueryOptions, ...]:
    """SearchProtocolEventCategories

    List of all protocol event categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolEventCategoriesQueryProtocoleventcategories]
    """
    return execute(
        SearchProtocolEventCategoriesQuery,
        {"search": search, "values": values},
        rath=rath,
    ).options


async def alist_protocol_event_categories(
    filters: Optional[ProtocolEventCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ProtocolEventCategory, ...]:
    """ListProtocolEventCategories

    List of all protocol event categories

    Args:
        filters (Optional[ProtocolEventCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ProtocolEventCategory]
    """
    return (
        await aexecute(
            ListProtocolEventCategoriesQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).protocol_event_categories


def list_protocol_event_categories(
    filters: Optional[ProtocolEventCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ProtocolEventCategory, ...]:
    """ListProtocolEventCategories

    List of all protocol event categories

    Args:
        filters (Optional[ProtocolEventCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ProtocolEventCategory]
    """
    return execute(
        ListProtocolEventCategoriesQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).protocol_event_categories


async def aget_reagent(id: ID, rath: Optional[KraphRath] = None) -> Reagent:
    """GetReagent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Reagent
    """
    return (await aexecute(GetReagentQuery, {"id": id}, rath=rath)).reagent


def get_reagent(id: ID, rath: Optional[KraphRath] = None) -> Reagent:
    """GetReagent


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Reagent
    """
    return execute(GetReagentQuery, {"id": id}, rath=rath).reagent


async def asearch_reagents(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchReagentsQueryOptions, ...]:
    """SearchReagents

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchReagentsQueryNodes]
    """
    return (
        await aexecute(
            SearchReagentsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_reagents(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchReagentsQueryOptions, ...]:
    """SearchReagents

    List of all entities in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchReagentsQueryNodes]
    """
    return execute(
        SearchReagentsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_reagents(
    filters: Optional[ReagentFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListReagent, ...]:
    """ListReagents


    Args:
        filters (Optional[ReagentFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListReagent]
    """
    return (
        await aexecute(
            ListReagentsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).reagents


def list_reagents(
    filters: Optional[ReagentFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListReagent, ...]:
    """ListReagents


    Args:
        filters (Optional[ReagentFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListReagent]
    """
    return execute(
        ListReagentsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).reagents


async def aget_reagent_category(
    id: ID, rath: Optional[KraphRath] = None
) -> ReagentCategory:
    """GetReagentCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ReagentCategory
    """
    return (
        await aexecute(GetReagentCategoryQuery, {"id": id}, rath=rath)
    ).reagent_category


def get_reagent_category(id: ID, rath: Optional[KraphRath] = None) -> ReagentCategory:
    """GetReagentCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        ReagentCategory
    """
    return execute(GetReagentCategoryQuery, {"id": id}, rath=rath).reagent_category


async def asearch_reagent_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchReagentCategoryQueryOptions, ...]:
    """SearchReagentCategory

    List of all reagent categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchReagentCategoryQueryReagentcategories]
    """
    return (
        await aexecute(
            SearchReagentCategoryQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_reagent_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchReagentCategoryQueryOptions, ...]:
    """SearchReagentCategory

    List of all reagent categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchReagentCategoryQueryReagentcategories]
    """
    return execute(
        SearchReagentCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_reagent_category(
    filters: Optional[ReagentCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListReagentCategory, ...]:
    """ListReagentCategory

    List of all reagent categories

    Args:
        filters (Optional[ReagentCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListReagentCategory]
    """
    return (
        await aexecute(
            ListReagentCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).reagent_categories


def list_reagent_category(
    filters: Optional[ReagentCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListReagentCategory, ...]:
    """ListReagentCategory

    List of all reagent categories

    Args:
        filters (Optional[ReagentCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListReagentCategory]
    """
    return execute(
        ListReagentCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).reagent_categories


async def aget_relation(id: ID, rath: Optional[KraphRath] = None) -> Relation:
    """GetRelation


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Relation
    """
    return (await aexecute(GetRelationQuery, {"id": id}, rath=rath)).relation


def get_relation(id: ID, rath: Optional[KraphRath] = None) -> Relation:
    """GetRelation


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Relation
    """
    return execute(GetRelationQuery, {"id": id}, rath=rath).relation


async def asearch_relations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchRelationsQueryOptions, ...]:
    """SearchRelations


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchRelationsQueryRelations]
    """
    return (
        await aexecute(
            SearchRelationsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_relations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchRelationsQueryOptions, ...]:
    """SearchRelations


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchRelationsQueryRelations]
    """
    return execute(
        SearchRelationsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_relation_category(
    id: ID, rath: Optional[KraphRath] = None
) -> RelationCategory:
    """GetRelationCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RelationCategory
    """
    return (
        await aexecute(GetRelationCategoryQuery, {"id": id}, rath=rath)
    ).relation_category


def get_relation_category(id: ID, rath: Optional[KraphRath] = None) -> RelationCategory:
    """GetRelationCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        RelationCategory
    """
    return execute(GetRelationCategoryQuery, {"id": id}, rath=rath).relation_category


async def asearch_relation_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchRelationCategoryQueryOptions, ...]:
    """SearchRelationCategory

    List of all relation categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchRelationCategoryQueryRelationcategories]
    """
    return (
        await aexecute(
            SearchRelationCategoryQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_relation_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchRelationCategoryQueryOptions, ...]:
    """SearchRelationCategory

    List of all relation categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchRelationCategoryQueryRelationcategories]
    """
    return execute(
        SearchRelationCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_relation_category(
    filters: Optional[RelationCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[RelationCategory, ...]:
    """ListRelationCategory

    List of all relation categories

    Args:
        filters (Optional[RelationCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[RelationCategory]
    """
    return (
        await aexecute(
            ListRelationCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).relation_categories


def list_relation_category(
    filters: Optional[RelationCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[RelationCategory, ...]:
    """ListRelationCategory

    List of all relation categories

    Args:
        filters (Optional[RelationCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[RelationCategory]
    """
    return execute(
        ListRelationCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).relation_categories


async def aget_structure(id: ID, rath: Optional[KraphRath] = None) -> Structure:
    """GetStructure


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return (await aexecute(GetStructureQuery, {"id": id}, rath=rath)).structure


def get_structure(id: ID, rath: Optional[KraphRath] = None) -> Structure:
    """GetStructure


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        Structure
    """
    return execute(GetStructureQuery, {"id": id}, rath=rath).structure


async def asearch_structures(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructuresQueryOptions, ...]:
    """SearchStructures


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructuresQueryStructures]
    """
    return (
        await aexecute(
            SearchStructuresQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_structures(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructuresQueryOptions, ...]:
    """SearchStructures


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructuresQueryStructures]
    """
    return execute(
        SearchStructuresQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_informed_structure(
    graph: ID,
    identifier: StructureIdentifier,
    object: ID,
    rath: Optional[KraphRath] = None,
) -> InformedStructure:
    """GetInformedStructure


    Args:
        graph (ID): No description
        identifier (StructureIdentifier): No description
        object (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        InformedStructure
    """
    return (
        await aexecute(
            GetInformedStructureQuery,
            {"graph": graph, "identifier": identifier, "object": object},
            rath=rath,
        )
    ).structure_by_identifier


def get_informed_structure(
    graph: ID,
    identifier: StructureIdentifier,
    object: ID,
    rath: Optional[KraphRath] = None,
) -> InformedStructure:
    """GetInformedStructure


    Args:
        graph (ID): No description
        identifier (StructureIdentifier): No description
        object (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        InformedStructure
    """
    return execute(
        GetInformedStructureQuery,
        {"graph": graph, "identifier": identifier, "object": object},
        rath=rath,
    ).structure_by_identifier


async def alist_structures(
    filters: Optional[StructureFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListStructure, ...]:
    """ListStructures


    Args:
        filters (Optional[StructureFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListStructure]
    """
    return (
        await aexecute(
            ListStructuresQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).structures


def list_structures(
    filters: Optional[StructureFilter] = None,
    pagination: Optional[GraphPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[ListStructure, ...]:
    """ListStructures


    Args:
        filters (Optional[StructureFilter], optional): No description.
        pagination (Optional[GraphPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[ListStructure]
    """
    return execute(
        ListStructuresQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).structures


async def aget_structure_category(
    id: ID, rath: Optional[KraphRath] = None
) -> StructureCategory:
    """GetStructureCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return (
        await aexecute(GetStructureCategoryQuery, {"id": id}, rath=rath)
    ).structure_category


def get_structure_category(
    id: ID, rath: Optional[KraphRath] = None
) -> StructureCategory:
    """GetStructureCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureCategory
    """
    return execute(GetStructureCategoryQuery, {"id": id}, rath=rath).structure_category


async def asearch_structure_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructureCategoryQueryOptions, ...]:
    """SearchStructureCategory

    List of all structure categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructureCategoryQueryStructurecategories]
    """
    return (
        await aexecute(
            SearchStructureCategoryQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_structure_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructureCategoryQueryOptions, ...]:
    """SearchStructureCategory

    List of all structure categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructureCategoryQueryStructurecategories]
    """
    return execute(
        SearchStructureCategoryQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_structure_category(
    filters: Optional[StructureCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[StructureCategory, ...]:
    """ListStructureCategory

    List of all structure categories

    Args:
        filters (Optional[StructureCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[StructureCategory]
    """
    return (
        await aexecute(
            ListStructureCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).structure_categories


def list_structure_category(
    filters: Optional[StructureCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[StructureCategory, ...]:
    """ListStructureCategory

    List of all structure categories

    Args:
        filters (Optional[StructureCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[StructureCategory]
    """
    return execute(
        ListStructureCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).structure_categories


async def aget_structure_relation_category(
    id: ID, rath: Optional[KraphRath] = None
) -> StructureRelationCategory:
    """GetStructureRelationCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return (
        await aexecute(GetStructureRelationCategoryQuery, {"id": id}, rath=rath)
    ).structure_relation_category


def get_structure_relation_category(
    id: ID, rath: Optional[KraphRath] = None
) -> StructureRelationCategory:
    """GetStructureRelationCategory


    Args:
        id (ID): No description
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        StructureRelationCategory
    """
    return execute(
        GetStructureRelationCategoryQuery, {"id": id}, rath=rath
    ).structure_relation_category


async def asearch_structure_relation_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructureRelationCategoryQueryOptions, ...]:
    """SearchStructureRelationCategory

    List of all structure relation categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructureRelationCategoryQueryStructurerelationcategories]
    """
    return (
        await aexecute(
            SearchStructureRelationCategoryQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_structure_relation_category(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchStructureRelationCategoryQueryOptions, ...]:
    """SearchStructureRelationCategory

    List of all structure relation categories

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchStructureRelationCategoryQueryStructurerelationcategories]
    """
    return execute(
        SearchStructureRelationCategoryQuery,
        {"search": search, "values": values},
        rath=rath,
    ).options


async def alist_structure_relation_category(
    filters: Optional[StructureRelationCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[StructureRelationCategory, ...]:
    """ListStructureRelationCategory

    List of all structure relation categories

    Args:
        filters (Optional[StructureRelationCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[StructureRelationCategory]
    """
    return (
        await aexecute(
            ListStructureRelationCategoryQuery,
            {"filters": filters, "pagination": pagination},
            rath=rath,
        )
    ).structure_relation_categories


def list_structure_relation_category(
    filters: Optional[StructureRelationCategoryFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[StructureRelationCategory, ...]:
    """ListStructureRelationCategory

    List of all structure relation categories

    Args:
        filters (Optional[StructureRelationCategoryFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[StructureRelationCategory]
    """
    return execute(
        ListStructureRelationCategoryQuery,
        {"filters": filters, "pagination": pagination},
        rath=rath,
    ).structure_relation_categories


async def asearch_tags(
    search: Optional[str] = None,
    values: Optional[List[str]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchTagsQueryOptions, ...]:
    """SearchTags

    List of all tags in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[str]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchTagsQueryTags]
    """
    return (
        await aexecute(SearchTagsQuery, {"search": search, "values": values}, rath=rath)
    ).options


def search_tags(
    search: Optional[str] = None,
    values: Optional[List[str]] = None,
    rath: Optional[KraphRath] = None,
) -> Tuple[SearchTagsQueryOptions, ...]:
    """SearchTags

    List of all tags in the system

    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[str]], optional): No description.
        rath (kraph.rath.KraphRath, optional): The mikro rath client

    Returns:
        List[SearchTagsQueryTags]
    """
    return execute(
        SearchTagsQuery, {"search": search, "values": values}, rath=rath
    ).options


EntityCategoryFilter.model_rebuild()
GraphFilter.model_rebuild()
GraphQueryFilter.model_rebuild()
GraphQueryInput.model_rebuild()
MeasurementCategoryFilter.model_rebuild()
MeasurementCategoryInput.model_rebuild()
MetricCategoryInput.model_rebuild()
NaturalEventCategoryFilter.model_rebuild()
NaturalEventCategoryInput.model_rebuild()
NodeQueryFilter.model_rebuild()
PlateChildInput.model_rebuild()
ProtocolEventCategoryFilter.model_rebuild()
ProtocolEventCategoryInput.model_rebuild()
ReagentCategoryFilter.model_rebuild()
RecordNaturalEventInput.model_rebuild()
RecordProtocolEventInput.model_rebuild()
RelationCategoryFilter.model_rebuild()
StructureCategoryFilter.model_rebuild()
StructureRelationCategoryFilter.model_rebuild()
ToldYouSoInput.model_rebuild()
UpdateGraphInput.model_rebuild()
VariableDefinitionInput.model_rebuild()
