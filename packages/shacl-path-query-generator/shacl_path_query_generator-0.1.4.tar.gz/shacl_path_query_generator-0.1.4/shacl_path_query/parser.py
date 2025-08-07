# parser.py

from rdflib import URIRef, BNode, Graph
from rdflib.namespace import RDF
from typing import Union
from .model import PathExpr

# SHACL predicates
SH_PATH = URIRef("http://www.w3.org/ns/shacl#path")
SH_ALTERNATIVE = URIRef("http://www.w3.org/ns/shacl#alternativePath")
SH_ZERO_OR_MORE = URIRef("http://www.w3.org/ns/shacl#zeroOrMorePath")
SH_ONE_OR_MORE = URIRef("http://www.w3.org/ns/shacl#oneOrMorePath")
SH_ZERO_OR_ONE = URIRef("http://www.w3.org/ns/shacl#zeroOrOnePath")
SH_INVERSE = URIRef("http://www.w3.org/ns/shacl#inversePath")


class SHACLParseError(ValueError):
    """Raised when a SHACL path cannot be parsed due to missing or malformed structure."""
    pass


def must_get_value(g: Graph, s: Union[URIRef, BNode], p: URIRef) -> Union[URIRef, BNode]:
    v = g.value(s, p)
    if v is None:
        raise SHACLParseError(f"Missing {p} value for node {s}")
    return v


def parse_shacl_path(g: Graph, node: Union[URIRef, BNode]) -> PathExpr:
    """
    Parses a SHACL path node into a PathExpr tree structure.

    Args:
        g: The shapes graph containing SHACL path definitions.
        node: The SHACL path node (IRI or BNode).

    Returns:
        A PathExpr representing the parsed structure.

    Raises:
        SHACLParseError: if the node is not a valid SHACL path.
    """
    if isinstance(node, URIRef):
        return PathExpr(predicate=str(node))

    if (node, RDF.first, None) in g:
        items = tuple(parse_shacl_path(g, i) for i in g.items(node))
        return PathExpr(seq=items)

    if (node, SH_ALTERNATIVE, None) in g:
        alt_root = must_get_value(g, node, SH_ALTERNATIVE)
        alts = tuple(parse_shacl_path(g, i) for i in g.items(alt_root))
        return PathExpr(alt=alts)

    if (node, SH_ZERO_OR_MORE, None) in g:
        inner = must_get_value(g, node, SH_ZERO_OR_MORE)
        return PathExpr(zero_or_more=parse_shacl_path(g, inner))

    if (node, SH_ONE_OR_MORE, None) in g:
        inner = must_get_value(g, node, SH_ONE_OR_MORE)
        return PathExpr(one_or_more=parse_shacl_path(g, inner))

    if (node, SH_ZERO_OR_ONE, None) in g:
        inner = must_get_value(g, node, SH_ZERO_OR_ONE)
        return PathExpr(zero_or_one=parse_shacl_path(g, inner))

    if (node, SH_INVERSE, None) in g:
        inner = must_get_value(g, node, SH_INVERSE)
        return PathExpr(inverse=parse_shacl_path(g, inner))

    raise SHACLParseError(f"Unknown SHACL path expression at node: {node}")
