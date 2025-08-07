# model.py

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class PathExpr:
    """
    Internal representation of a parsed SHACL path expression.

    Exactly one of the fields should be set, representing:
    - predicate: a simple IRI path
    - inverse: an inverse path
    - zero_or_more / one_or_more / zero_or_one: repetition modifiers
    - seq: a sequence of paths (ordered traversal)
    - alt: an alternative path (disjunction)
    """
    predicate: Optional[str] = None
    inverse: Optional["PathExpr"] = None
    zero_or_more: Optional["PathExpr"] = None
    one_or_more: Optional["PathExpr"] = None
    zero_or_one: Optional["PathExpr"] = None
    seq: Optional[Tuple["PathExpr", ...]] = None
    alt: Optional[Tuple["PathExpr", ...]] = None
