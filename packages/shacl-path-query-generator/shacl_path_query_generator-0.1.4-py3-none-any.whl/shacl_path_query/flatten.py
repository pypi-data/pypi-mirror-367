# flatten.py

from typing import Tuple, List
from .model import PathExpr


def fresh_var(counter: int) -> Tuple[str, int]:
    return f"?v{counter}", counter + 1


def flatten_path(path: PathExpr, src: str, dst: str, depth: int = 3, counter: int = 0) -> Tuple[List[str], int]:
    """
    Flattens a PathExpr tree into a list of SPARQL triple patterns that
    represent the full path including intermediate variables.

    Args:
        path: The parsed PathExpr object.
        src: Starting SPARQL variable.
        dst: Ending SPARQL variable.
        depth: Max unroll depth for oneOrMore and zeroOrMore.
        counter: Internal counter for fresh variable naming.

    Returns:
        A tuple of (list of triple strings, updated counter).
    """
    triples: List[str] = []

    if path.predicate:
        triples.append(f"{src} <{path.predicate}> {dst} .")
        return triples, counter

    if path.inverse:
        return flatten_path(path.inverse, dst, src, depth, counter)

    if path.seq:
        vars = [src]
        for _ in range(len(path.seq) - 1):
            v, counter = fresh_var(counter)
            vars.append(v)
        vars.append(dst)
        for i, sub in enumerate(path.seq):
            sub_triples, counter = flatten_path(sub, vars[i], vars[i + 1], depth, counter)
            triples.extend(sub_triples)
        return triples, counter

    if path.alt:
        union_blocks = []
        for sub in path.alt:
            block, counter = flatten_path(sub, src, dst, depth, counter)
            union_blocks.append("{\n  " + "\n  ".join(block) + "\n}")
        triples.append("{ " + " UNION ".join(union_blocks) + " }")
        return triples, counter

    if path.zero_or_one:
        t1, counter = flatten_path(path.zero_or_one, src, dst, depth, counter)
        identity = [f"FILTER({src} = {dst})"]
        union = "{ " + "\n  ".join(t1) + " } UNION { " + "\n  ".join(identity) + " }"
        triples.append("{ " + union + " }")
        return triples, counter

    if path.one_or_more:
        # Unroll to fixed depth
        current_src = src
        for i in range(depth):
            v, counter = fresh_var(counter) if i < depth - 1 else (dst, counter)
            sub_triples, counter = flatten_path(path.one_or_more, current_src, v, depth, counter)
            triples.extend(sub_triples)
            current_src = v
        return triples, counter

    if path.zero_or_more:
        # Add identity + unroll to depth
        identity = [f"FILTER({src} = {dst})"]
        t_chain, counter = flatten_path(PathExpr(one_or_more=path.zero_or_more), src, dst, depth, counter)
        union = "{ " + "\n  ".join(identity) + " } UNION { " + "\n  ".join(t_chain) + " }"
        triples.append("{ " + union + " }")
        return triples, counter

    raise ValueError("Unhandled PathExpr case")
