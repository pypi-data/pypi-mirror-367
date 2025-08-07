---

# SHACL Path Query Generator

Parse and flatten SHACL path expressions into executable SPARQL triple patterns.

## Features

- ✅ Parses all standard SHACL path constructs:
  - `sh:path`
  - `sh:inversePath`
  - `sh:zeroOrMorePath`, `sh:oneOrMorePath`, `sh:zeroOrOnePath`
  - `sh:alternativePath`
  - sequences (`rdf:List`)
- ✅ Converts parsed paths into a list of triple patterns with fresh variables.
- ✅ Allows optional unrolling depth for repetitive paths (`*`, `+`).
- 🧪 Fully tested with nested and edge-case paths.
- 🧩 Outputs raw SPARQL triple patterns, ready for flexible usage (e.g. `WHERE`, `CONSTRUCT`, `INSERT`, etc.).

## Installation

```bash
pip install shacl-path-query-generator
````

Requires: `rdflib>=7.1.4`

## Example Usage

```python
from rdflib import Graph, Namespace
from shacl_path_query import path_to_sparql_pattern

EX = Namespace("http://ex.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")

turtle = """
PREFIX ex: <http://ex.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

[] a sh:NodeShape ;
   sh:targetClass ex:Thing ;
   sh:property [
     sh:path (
       ex:p1
       [ sh:inversePath ex:p2 ]
     ) ;
     sh:datatype xsd:string ;
   ] .
"""

g = Graph()
g.parse(data=turtle, format="turtle")

# Get the path node (blank node for the list)
path_node = g.value(predicate=SH.path)
pattern = path_to_sparql_pattern(path_node, g)
print(pattern)

```

## Sample Output

```
?s <http://ex.org/p1> ?v0 .
?o <http://ex.org/p2> ?v0 .
```

## Example in a SPARQL CONSTRUCT

```sparql
CONSTRUCT {
  ?s <http://ex.org/p1> ?v0 .
  ?o <http://ex.org/p2> ?v0 .
}
WHERE {
  VALUES ?s { <http://ex.org/a> <http://ex.org/b> }
  ?s <http://ex.org/p1> ?v0 .
  ?o <http://ex.org/p2> ?v0 .
}
```

## License

MIT

---

