"""Tools for compiling QGraph into Cypher query."""


def cypher_prop_string(value):
    """Convert property value to cypher string representation."""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        return f"'{value}'"
    else:
        raise ValueError(f'Unsupported property type: {type(value).__name__}.')


class NodeReference():
    """Node reference object."""

    def __init__(self, node, anonymous=False):
        """Create a node reference."""
        node = dict(node)
        node_id = node.pop("id")
        name = f'{node_id}' if not anonymous else ''
        labels = node.pop('type', 'named_thing')
        if not isinstance(labels, list):
            labels = [labels]
        props = {}

        curie = node.pop("curie", None)
        if curie is not None:
            if isinstance(curie, str):
                props['id'] = curie
                filters = ''
            elif isinstance(curie, list):
                filters = []
                for ci in curie:
                    # generate curie-matching condition
                    filters.append(f"{name}.id = '{ci}'")
                # union curie-matching filters together
                filters = ' OR '.join(filters)
            else:
                raise TypeError("Curie should be a string or list of strings.")
        else:
            filters = ''

        node.pop('name', None)
        node.pop('set', False)
        props.update(node)

        self.name = name
        self.labels = labels
        self.prop_string = ' {' + ', '.join([f"`{key}`: {cypher_prop_string(props[key])}" for key in props]) + '}'
        self._filters = filters
        if curie:
            self._extras = f' USING INDEX {name}:{labels[0]}(id)'
        else:
            self._extras = ''
        self._num = 0

    def __str__(self):
        """Return the cypher node reference."""
        self._num += 1
        if self._num == 1:
            return f'{self.name}' + \
                   ''.join(f':`{label}`' for label in self.labels) + \
                   f'{self.prop_string}'
        return self.name

    @property
    def filters(self):
        """Return filters for the cypher node reference.
        To be used in a WHERE clause following the MATCH clause.
        """
        if self._num == 1:
            return self._filters
        else:
            return ''

    @property
    def extras(self):
        """Return extras for the cypher node reference.
        To be appended to the MATCH clause.
        """
        if self._num == 1:
            return self._extras
        else:
            return ''


class EdgeReference():
    """Edge reference object."""

    def __init__(self, edge, anonymous=False):
        """Create an edge reference."""
        name = f'{edge["id"]}' if not anonymous else ''
        label = edge['type'] if 'type' in edge else None

        if 'type' in edge and edge['type'] is not None:
            if isinstance(edge['type'], str):
                label = edge['type']
                filters = ''
            elif isinstance(edge['type'], list):
                filters = []
                for predicate in edge['type']:
                    filters.append(f'type({name}) = "{predicate}"')
                filters = ' OR '.join(filters)
                label = None
        else:
            label = None
            filters = ''

        self.name = name
        self.label = label
        self._num = 0
        self._filters = filters
        has_type = 'type' in edge and edge['type']
        self.directed = edge.get('directed', has_type)

    def __str__(self):
        """Return the cypher edge reference."""
        self._num += 1
        if self._num == 1:
            innards = f'{self.name}{":" + self.label if self.label else ""}'
        else:
            innards = self.name
        if self.directed:
            return f'-[{innards}]->'
        else:
            return f'-[{innards}]-'

    @property
    def filters(self):
        """Return filters for the cypher node reference.
        To be used in a WHERE clause following the MATCH clause.
        """
        if self._num == 1:
            return self._filters
        else:
            return ''


def cypher_query_fragment_match(qgraph, max_connectivity=-1):
    """Generate a Cypher query fragment to match the nodes and edges that correspond to a question.
    This is used internally for cypher_query_answer_map and cypher_query_knowledge_graph
    Returns the query fragment as a string.
    """
    nodes, edges = qgraph['nodes'], qgraph['edges']

    # generate internal node and edge variable names
    node_references = {n['id']: NodeReference(n) for n in nodes}
    edge_references = [EdgeReference(e) for e in edges]

    match_strings = []

    # match orphaned nodes
    def flatten(l):
        return [e for sl in l for e in sl]
    all_nodes = {n['id'] for n in nodes}
    all_referenced_nodes = set(flatten([[e['source_id'], e['target_id']] for e in edges]))
    orphaned_nodes = all_nodes - all_referenced_nodes
    for n in orphaned_nodes:
        match_strings.append(f"MATCH ({node_references[n]})")
        match_strings[-1] += node_references[n].extras
        if node_references[n].filters:
            match_strings.append("WHERE " + node_references[n].filters)

    # match edges
    for e, eref in zip(edges, edge_references):
        source_node = node_references[e['source_id']]
        target_node = node_references[e['target_id']]
        match_strings.append(f"MATCH ({source_node}){eref}({target_node})")
        match_strings[-1] += source_node.extras + target_node.extras
        filters = [f'({c})' for c in [source_node.filters, target_node.filters, eref.filters] if c]
        if max_connectivity > -1:
            filters.append(f"(size( ({target_node})-[]-() ) < {max_connectivity})")
        if filters:
            match_strings.append("WHERE " + " AND ".join(filters))

    match_string = ' '.join(match_strings)

    return match_string


def cypher_query_answer_map(qgraph, **kwargs):
    """Generate a Cypher query to extract the answer maps for a question.
    Returns the query as a string.
    """
    clauses = []

    match_string = cypher_query_fragment_match(qgraph, max_connectivity=kwargs.pop('max_connectivity', -1))
    if match_string:
        clauses.append(match_string)

    nodes, edges = qgraph['nodes'], qgraph['edges']

    # generate internal node and edge variable names
    node_names = [f"{n['id']}" for n in nodes]
    edge_names = [f"{e['id']}" for e in edges]

    # deal with sets
    node_id_accessor = [f"collect(DISTINCT {n['id']}) AS {n['id']}" if 'set' in n and n['set'] else f"[{n['id']}] AS {n['id']}" for n in nodes]
    if kwargs.get('relationship_id', 'property') == 'internal':
        edge_id_accessor = [f"collect(DISTINCT toString(id({e['id']}))) AS {e['id']}" for e in edges]
    else:
        edge_id_accessor = [f"collect(DISTINCT {e['id']}) AS {e['id']}" for e in edges]
    if node_id_accessor or edge_id_accessor:
        with_string = f"WITH {', '.join(node_id_accessor+edge_id_accessor)}"
        clauses.append(with_string)

    # add bound fields and return map
    node_dicts = [f"[ni IN {n} | {{qg_id:'{n}', kg_id:ni.id, node: ni, type: labels(ni) }}]" for n in node_names]
    edge_dicts = [f"[ei IN {e} | {{qg_id:'{e}', kg_id:ei.id, edge: ei, type: type(ei) }}]" for e in edge_names]
    answer_return_string = f"RETURN {' + '.join(node_dicts) or '[]'} AS nodes, {' + '.join(edge_dicts) or '[]'} AS edges"
    clauses.append(answer_return_string)

    # return answer maps matching query
    query_string = ' '.join(clauses)
    if 'skip' in kwargs:
        query_string += f' SKIP {kwargs["skip"]}'
    if 'limit' in kwargs:
        query_string += f' LIMIT {kwargs["limit"]}'

    return query_string


def flatten_semilist(x):
    """Convert a semi-nested list - a list of (lists and scalars) - to a flat list."""
    # convert to a list of lists
    lists = [n if isinstance(n, list) else [n] for n in x]
    # flatten nested list
    return [e for el in lists for e in el]