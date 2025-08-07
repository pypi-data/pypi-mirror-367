from rdflib import URIRef
from shacl_path_query.model import PathExpr
from shacl_path_query.flatten import flatten_path


def render(triples):
    """Utility to normalize whitespace for test assertions."""
    return "\n".join(line.strip() for line in triples)


def test_flat_predicate():
    p = URIRef("http://ex.org/p")
    expr = PathExpr(predicate=str(p))
    triples, _ = flatten_path(expr, "?s", "?o")
    assert render(triples) == "?s <http://ex.org/p> ?o ."


def test_inverse_predicate():
    p = URIRef("http://ex.org/p")
    expr = PathExpr(inverse=PathExpr(predicate=str(p)))
    triples, _ = flatten_path(expr, "?s", "?o")
    assert render(triples) == "?o <http://ex.org/p> ?s ."


def test_sequence_path():
    p1 = URIRef("http://ex.org/p1")
    p2 = URIRef("http://ex.org/p2")
    expr = PathExpr(seq=(PathExpr(predicate=str(p1)), PathExpr(predicate=str(p2))))
    triples, _ = flatten_path(expr, "?s", "?o")
    assert render(triples) == (
        "?s <http://ex.org/p1> ?v0 .\n"
        "?v0 <http://ex.org/p2> ?o ."
    )


def test_alternative_path():
    p1 = URIRef("http://ex.org/p1")
    p2 = URIRef("http://ex.org/p2")
    expr = PathExpr(alt=(PathExpr(predicate=str(p1)), PathExpr(predicate=str(p2))))
    triples, _ = flatten_path(expr, "?s", "?o")
    text = triples[0].replace(" ", "").replace("\n", "")
    assert "?s<http://ex.org/p1>?o." in text
    assert "?s<http://ex.org/p2>?o." in text
    assert "UNION" in text



def test_zero_or_one_path():
    p = URIRef("http://ex.org/p")
    expr = PathExpr(zero_or_one=PathExpr(predicate=str(p)))
    triples, _ = flatten_path(expr, "?s", "?o")
    assert "FILTER(?s = ?o)" in triples[0]
    assert "?s <http://ex.org/p> ?o ." in triples[0]


def test_one_or_more_path_unroll():
    p = URIRef("http://ex.org/p")
    expr = PathExpr(one_or_more=PathExpr(predicate=str(p)))
    triples, _ = flatten_path(expr, "?s", "?o", depth=3)
    expected = [
        "?s <http://ex.org/p> ?v0 .",
        "?v0 <http://ex.org/p> ?v1 .",
        "?v1 <http://ex.org/p> ?o ."
    ]
    assert all(line in render(triples) for line in expected)


def test_zero_or_more_path_unroll():
    p = URIRef("http://ex.org/p")
    expr = PathExpr(zero_or_more=PathExpr(predicate=str(p)))
    triples, _ = flatten_path(expr, "?s", "?o", depth=2)
    assert "FILTER(?s = ?o)" in triples[0]
    assert "?s <http://ex.org/p> ?v0 ." in triples[0]
    assert "?v0 <http://ex.org/p> ?o ." in triples[0]


def test_nested_inverse_in_sequence():
    p1 = URIRef("http://ex.org/p1")
    p2 = URIRef("http://ex.org/p2")
    expr = PathExpr(seq=(PathExpr(inverse=PathExpr(predicate=str(p1))), PathExpr(predicate=str(p2))))
    triples, _ = flatten_path(expr, "?s", "?o")
    # First triple: ?v0 <p1> ?s  (inverse)
    # Second triple: ?v0 <p2> ?o
    assert triples[0] == "?v0 <http://ex.org/p1> ?s ."
    assert triples[1] == "?v0 <http://ex.org/p2> ?o ."

