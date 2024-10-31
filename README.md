# telicent-validation-tool

A library for validating data before it is brought in to Telicent CORE.

## Install

```bash
pip install telicent-validation-tool
```

## Usage

### JSON Validation

The JSON validator loads a [json-schema](https://json-schema.org/) from a given file path, and uses the
[jsonschema](https://pypi.org/project/jsonschema/) library to validate the provided JSON.

```python
from telicent_validation_tool import TelicentValidationError, validate_json

my_json: str = '{"name: "John Smith"}'
schema_path: str = '/path/to/schema.json'

try:
    validate_json(my_json, schema_path)
except TelicentValidationError as e:
    print(f"Validation error: {e}")
```

The JSON schema file will only be loaded from disk on the first validation to improve the performance of subsequent validations. 

To force a validation to reload the schema file from disk, set `force_reload=True`.

```python
validate_json(my_json, schema_path, force_reload=True)
```

### SHACL Validation

The SHACL validator provides a wrapper around Telicent's own [shacl-tool](https://github.com/Telicent-io/shacl-tool). It validates a rdf graph against the shacl and 
ontology triples of the base ontology being used and any domain specific extensions. For example, you might be using the FOAF 
base ontology but have extended some of the classes; for example:
```
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix myont: <http://example.com/ontology/my-domain-specific-ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

myont:Child rdfs:subClassOf foaf:Person .
```

```shacl_parts``` and ```ontology_parts``` are lists of paths to turtle files. This allows us to fuse shacl and ontology 
files applicable to the graph requiring validation.

```python
from rdflib import Graph, URIRef, Literal, XSD
from telicent_validation_tool import TelicentValidationError, validate_rdf_turtle

graph: Graph = Graph()
graph.add(
    URIRef("http://example.com/data/nick_smith"),
    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
    URIRef("http://example.com/ontology/my-domain-specific-ontology#Child")
)
graph.add(
    URIRef("http://example.com/data/nick_smith"),
    URIRef("http://xmlns.com/foaf/0.1/name"),
    Literal("Nick Smith", datatype=XSD.string)
)

shacl_parts: list = [
    '/path/to/foaf-base-ontology.shacl.ttl'
    '/path/to/my-domain-specific.shacl.ttl'
]
ontology_parts: list = [
    '/path/to/foaf-base-ontology.ttl'
    '/path/to/my-domain-specific-ontology.ttl'
]

try:
    validate_rdf_turtle(graph, shacl_parts, ontology_parts)
except TelicentValidationError as e:
    print(f"Validation error: {e}")
```
