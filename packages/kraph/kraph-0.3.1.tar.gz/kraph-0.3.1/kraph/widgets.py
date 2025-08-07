from rekuest_next.widgets import SearchWidget





def graphgenerics(graph_var: str) -> SearchWidget:
    
    widget = SearchWidget(
        """
        query SearchGenericCategory($search: String, $values: [ID!], $graph: ID!) {
            options: genericCategories(
                filters: { search: $search, ids: $values, graph: $graph },
                pagination: { limit: 10 }
            ) {
                value: id
                label: label
            }
        }
        """,
        ward="kraph",
        dependencies=[graph_var],
    )
    
    return widget


def graphmeasurments(graph_var: str) -> SearchWidget:
    
    widget = SearchWidget(
        """
        query SearchMeasurementCategory($search: String, $values: [ID!], $graph: ID!) {
            options: measurementCategories(
                filters: { search: $search, ids: $values, graph: $graph },
                pagination: { limit: 10 }
            ) {
                value: id
                label: label
            }
        }
        """,
        ward="kraph",
        dependencies=[graph_var],
    )
    
    return widget
    