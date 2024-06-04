from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from rdflib import Graph

from telicent_validation_tool import TelicentValidationError, validate_rdf_turtle

__license__ = """
Copyright (c) Telicent Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class RDFImplementationTestCase(TestCase):

    @staticmethod
    def test_builds_compound_shacl_graph():
        with patch.object(Graph, 'parse') as mock_method:
            validate_rdf_turtle(Graph(), ['test'], [])
            mock_method.assert_called_with(location='test', format='turtle')

    @staticmethod
    def test_builds_compound_compound_ontology_graph():
        with patch.object(Graph, 'parse') as mock_method:
            validate_rdf_turtle(Graph(), [], ['test'])
            mock_method.assert_called_with(location='test', format='turtle')

    def test_validate_called(self):
        g = Graph()
        error_graph = MagicMock()
        with patch(
            'telicent_validation_tool.validators.rdf_validate', return_value=(True, error_graph, None)
        ) as mock_method:
            validate_rdf_turtle(g, [], [])
            mock_method.assert_called_with(g, ANY, ANY)
            self.assertEqual(2, len(error_graph.serialize.mock_calls))

    def test_valid_graph(self):
        error_graph = MagicMock()
        with patch(
            'telicent_validation_tool.validators.rdf_validate', return_value=(True, error_graph, None)
        ):
            self.assertTrue(validate_rdf_turtle(Graph(), [], []))
            self.assertEqual(2, len(error_graph.serialize.mock_calls))

    def test_invalid_graph(self):
        error_graph = MagicMock()
        with patch(
            'telicent_validation_tool.validators.rdf_validate', return_value=(False, error_graph, None)
        ):
            self.assertRaises(TelicentValidationError, validate_rdf_turtle, Graph(), [], [])
            self.assertEqual(4, len(error_graph.serialize.mock_calls))
