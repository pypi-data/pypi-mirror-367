# __init__.py

__version__ = "0.1.3"


from .parser import parse_shacl_path, SHACLParseError
from .flatten import flatten_path
from .model import PathExpr


def path_to_sparql_pattern(path_node, shapes_graph, source_var="?s", target_var="?o", depth=3) -> str:
    try:
        path_expr = parse_shacl_path(shapes_graph, path_node)
    except SHACLParseError as e:
        print(f"[ERROR] Could not parse SHACL path: {e}")
        raise

    triples, _ = flatten_path(path_expr, source_var, target_var, depth)
    return "\n".join(triples)


__all__ = ["path_to_sparql_pattern", "__version__", "PathExpr"]
