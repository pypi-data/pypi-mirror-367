from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.widgets import SearchWidget
from kraph.api.schema import (
    Graph,
    SearchEntitiesQuery,
    SearchStructureRelationCategoryQuery,
    aget_graph,
    Reagent,
    aget_reagent,
    StructureCategory,
    aget_structure_category,
    aget_structure_relation_category,
    EntityCategory,
    aget_entity_category,
    MeasurementCategory,
    aget_measurment_category,
    RelationCategory,
    aget_relation_category,
    StructureRelationCategory,
    GraphQuery,
    aget_graph_query,
    MetricCategory,
    aget_metric_category,
    Entity,
    aget_node,
    Structure,
    aget_structure,
    Metric,
    aget_metric,
    SearchGraphsQuery,
    SearchReagentsQuery,
    SearchStructureCategoryQuery,
    SearchEntityCategoryQuery,
    SearchMeasurmentCategoryQuery,
    SearchRelationCategoryQuery,
    SearchGraphQueriesQuery,
    SearchMetricsQuery,
    SearchStructuresQuery,
    SearchMetricCategoryQuery,
)

structure_reg = get_default_structure_registry()


structure_reg.register_as_structure(
    Graph,
    identifier="@kraph/graph",
    aexpand=aget_graph,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchGraphsQuery.Meta.document, ward="kraph"),
)
structure_reg.register_as_structure(
    Reagent,
    identifier="@kraph/reagent",
    aexpand=aget_reagent,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchReagentsQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    StructureCategory,
    identifier="@kraph/structurecategory",
    aexpand=aget_structure_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchStructureCategoryQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    EntityCategory,
    identifier="@kraph/entitycategory",
    aexpand=aget_entity_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchEntityCategoryQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    StructureRelationCategory,
    identifier="@kraph/structurerelationcategory",
    aexpand=aget_structure_relation_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(
        query=SearchStructureRelationCategoryQuery.Meta.document, ward="kraph"
    ),
)


structure_reg.register_as_structure(
    MeasurementCategory,
    identifier="@kraph/measurementcategory",
    aexpand=aget_measurment_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchMeasurmentCategoryQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    RelationCategory,
    identifier="@kraph/relationcategory",
    aexpand=aget_relation_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchRelationCategoryQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    GraphQuery,
    identifier="@kraph/graphquery",
    aexpand=aget_graph_query,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchGraphQueriesQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    MetricCategory,
    identifier="@kraph/metriccategory",
    aexpand=aget_metric_category,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchMetricCategoryQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    GraphQuery,
    identifier="@kraph/graphquery",
    aexpand=aget_graph_query,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchGraphQueriesQuery.Meta.document, ward="kraph"),
)


structure_reg.register_as_structure(
    Entity,
    identifier="@kraph/entity",
    aexpand=aget_node,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchEntitiesQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    Structure,
    identifier="@kraph/entity",
    aexpand=aget_structure,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchStructuresQuery.Meta.document, ward="kraph"),
)

structure_reg.register_as_structure(
    Metric,
    identifier="@kraph/metric",
    aexpand=aget_metric,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchMetricsQuery.Meta.document, ward="kraph"),
)
