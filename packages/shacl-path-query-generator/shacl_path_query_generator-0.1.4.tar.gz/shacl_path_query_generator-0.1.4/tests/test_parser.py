from rdflib import Graph, URIRef, BNode, RDF
from shacl_path_query.parser import parse_shacl_path, SHACLParseError
from shacl_path_query.model import PathExpr
from shacl_path_query.parser import (
    SH_ALTERNATIVE, SH_ZERO_OR_MORE, SH_ONE_OR_MORE,
    SH_ZERO_OR_ONE, SH_INVERSE
)


def test_predicate_path():
    g = Graph()
    p = URIRef("http://example.org/p")
    expr = parse_shacl_path(g, p)
    assert expr == PathExpr(predicate=str(p))


def test_sequence_path():
    g = Graph()
    p1 = URIRef("http://example.org/p1")
    p2 = URIRef("http://example.org/p2")
    seq_node = BNode()
    g.add((seq_node, RDF.first, p1))
    rest = BNode()
    g.add((seq_node, RDF.rest, rest))
    g.add((rest, RDF.first, p2))
    g.add((rest, RDF.rest, RDF.nil))
    expr = parse_shacl_path(g, seq_node)
    assert expr.seq and len(expr.seq) == 2
    assert expr.seq[0].predicate == str(p1)
    assert expr.seq[1].predicate == str(p2)


def test_alternative_path():
    g = Graph()
    alt_outer = BNode()
    alt_list = BNode()
    g.add((alt_outer, SH_ALTERNATIVE, alt_list))

    g.add((alt_list, RDF.first, URIRef("http://example.org/p1")))
    rest = BNode()
    g.add((alt_list, RDF.rest, rest))
    g.add((rest, RDF.first, URIRef("http://example.org/p2")))
    g.add((rest, RDF.rest, RDF.nil))

    expr = parse_shacl_path(g, alt_outer)
    assert expr.alt and len(expr.alt) == 2
    assert expr.alt[0].predicate == "http://example.org/p1"
    assert expr.alt[1].predicate == "http://example.org/p2"


def test_zero_or_more_path():
    g = Graph()
    outer = BNode()
    inner = URIRef("http://example.org/p")
    g.add((outer, SH_ZERO_OR_MORE, inner))
    expr = parse_shacl_path(g, outer)
    assert expr.zero_or_more and expr.zero_or_more.predicate == str(inner)


def test_one_or_more_path():
    g = Graph()
    outer = BNode()
    inner = URIRef("http://example.org/p")
    g.add((outer, SH_ONE_OR_MORE, inner))
    expr = parse_shacl_path(g, outer)
    assert expr.one_or_more and expr.one_or_more.predicate == str(inner)


def test_zero_or_one_path():
    g = Graph()
    outer = BNode()
    inner = URIRef("http://example.org/p")
    g.add((outer, SH_ZERO_OR_ONE, inner))
    expr = parse_shacl_path(g, outer)
    assert expr.zero_or_one and expr.zero_or_one.predicate == str(inner)


def test_inverse_path():
    g = Graph()
    outer = BNode()
    inner = URIRef("http://example.org/p")
    g.add((outer, SH_INVERSE, inner))
    expr = parse_shacl_path(g, outer)
    assert expr.inverse and expr.inverse.predicate == str(inner)


def test_invalid_path_raises():
    g = Graph()
    b = BNode()
    g.add((b, URIRef("http://example.org/fakePath"), BNode()))
    try:
        parse_shacl_path(g, b)
    except SHACLParseError as e:
        assert "Unknown" in str(e)
    else:
        assert False, "Expected SHACLParseError"

def test_one_or_more_sequence():
    g = Graph()

    # Construct a sequence list: p1 → p2
    p1 = URIRef("http://example.org/p1")
    p2 = URIRef("http://example.org/p2")
    seq_list = BNode()
    rest = BNode()
    g.add((seq_list, RDF.first, p1))
    g.add((seq_list, RDF.rest, rest))
    g.add((rest, RDF.first, p2))
    g.add((rest, RDF.rest, RDF.nil))

    # Wrap sequence in oneOrMorePath
    wrapper = BNode()
    g.add((wrapper, SH_ONE_OR_MORE, seq_list))

    expr = parse_shacl_path(g, wrapper)
    assert expr.one_or_more is not None
    assert expr.one_or_more.seq is not None
    assert len(expr.one_or_more.seq) == 2
    assert expr.one_or_more.seq[0].predicate == str(p1)
    assert expr.one_or_more.seq[1].predicate == str(p2)


def test_inverse_zero_or_more():
    g = Graph()

    # Inner predicate
    pred = URIRef("http://example.org/knows")
    inv = BNode()
    g.add((inv, SH_INVERSE, pred))

    # Outer: zeroOrMorePath
    outer = BNode()
    g.add((outer, SH_ZERO_OR_MORE, inv))

    expr = parse_shacl_path(g, outer)
    assert expr.zero_or_more is not None
    assert expr.zero_or_more.inverse is not None
    assert expr.zero_or_more.inverse.predicate == str(pred)


def test_nested_alt_with_sequence():
    g = Graph()

    # Left path: sequence of two predicates
    seq_list = BNode()
    rest = BNode()
    g.add((seq_list, RDF.first, URIRef("http://example.org/a")))
    g.add((seq_list, RDF.rest, rest))
    g.add((rest, RDF.first, URIRef("http://example.org/b")))
    g.add((rest, RDF.rest, RDF.nil))

    # Right path: one predicate
    p2 = URIRef("http://example.org/c")

    # Create alternativePath
    alt_list = BNode()
    g.add((alt_list, RDF.first, seq_list))
    rest2 = BNode()
    g.add((alt_list, RDF.rest, rest2))
    g.add((rest2, RDF.first, p2))
    g.add((rest2, RDF.rest, RDF.nil))

    alt_wrapper = BNode()
    g.add((alt_wrapper, SH_ALTERNATIVE, alt_list))

    expr = parse_shacl_path(g, alt_wrapper)
    assert expr.alt is not None and len(expr.alt) == 2
    assert expr.alt[0].seq is not None
    assert expr.alt[1].predicate == str(p2)
