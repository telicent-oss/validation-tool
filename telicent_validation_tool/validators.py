import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from rdflib import Graph
from shacltool.owl2shacl import rdf_validate
from pyshacl import validate as shacl_validate

logger = logging.getLogger(__name__)


class TelicentValidationError(Exception):
    pass


def validate_json(data: str, schema_file_path: str) -> bool | None:
    """
    Validates a JSON string against the schema in a given file.

    Args:
        data (str): The JSON to validate
        schema_file_path (str): The file path containing the JSON schema
    Returns:
        bool: The result of the validation
    Raises:
        TelicentValidationError: On failure to validate
    """
    with open(schema_file_path) as file:
        schema = json.load(file)
        try:
            validate(instance=data, schema=schema)
            logger.info('JSON is valid')
            return True
        except ValidationError as e:
            logger.error(f'JSON validation error: {e}')
            raise TelicentValidationError from e


def validate_rdf_turtle(data: Graph, shacl_parts: list, ontology_parts: list) -> bool | None:
    """
    Validates a Graph against SHACL and an ontology.

    Args:
        data (Graph): The Graph to validate
        shacl_parts (list): The SHACL files to validate against
        ontology_parts (list): The Ontology files to validate against
    Returns:
        bool: The result of the validation
    Raises:
        TelicentValidationError: On failure to validate
    """
    compound_shacl_graph = Graph()
    for shacl_part in shacl_parts:
        compound_shacl_graph += compound_shacl_graph.parse(location=shacl_part, format="turtle")
    compound_ontology_graph = Graph()
    for ontology_part in ontology_parts:
        compound_ontology_graph += compound_ontology_graph.parse(location=ontology_part, format="turtle")
    
    is_valid, result_graph, _ = shacl_validate(data, compound_shacl_graph, compound_ontology_graph, allow_warnings=True)

    logger.debug({result_graph.serialize()})

    if is_valid:
        logger.info("Data conforms to the ontology and SHACL shapes.")
        return True
    else:
        logger.error('SHACL validation error')
        raise TelicentValidationError(
            f"Data does not conform to the ontology and SHACL shapes: {result_graph.serialize()}"
        )
