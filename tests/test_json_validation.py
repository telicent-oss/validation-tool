from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import ANY, mock_open, patch

from jsonschema.exceptions import ValidationError

from telicent_validation_tool.validators import TelicentValidationError, validate_json

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


class JSONImplementationTestCase(TestCase):

    def setUp(self):
        from telicent_validation_tool import validators
        validators.json_schema_cache = {}

    @staticmethod
    def test_opens_specified_file():
        with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
            validate_json('{}', 'my_file')
        mock_file.assert_called_with("my_file")

    def test_opened_file_must_be_json(self):
        with patch("builtins.open", mock_open(read_data="{[}")):
            self.assertRaises(JSONDecodeError, validate_json, '{}', 'my_file')

    @staticmethod
    def test_validate_method_called():
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("telicent_validation_tool.validators.fast_validate_json") as mock_validate:
                validate_json('{}', 'my_file')
            mock_validate.assert_called_with(instance='{}', schema={}, cls=ANY)

    def test_validate_true_returns_true(self):
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("telicent_validation_tool.validators.fast_validate_json") as mock_validate:
                mock_validate.return_value = True
                self.assertTrue(validate_json('{}', 'my_file'))

    def test_validate_error_raises_error(self):
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch(
                target="telicent_validation_tool.validators.fast_validate_json",
                side_effect=ValidationError('Invalid')
            ):
                self.assertRaises(TelicentValidationError, validate_json, '{}', 'my_file')

    def test_schema_file_only_loaded_once(self):
        with patch("builtins.open", mock_open(read_data="{}")) as mocked_open:
            validate_json('{}', 'my_file')
            validate_json('{}', 'my_file')
            validate_json('{}', 'my_file')
            self.assertEqual(1, mocked_open.call_count)

    def test_can_reset_cache(self):
        with patch("builtins.open", mock_open(read_data="{}")) as mocked_open:
            validate_json('{}', 'my_file')
            validate_json('{}', 'my_file')
            self.assertEqual(1, mocked_open.call_count)
            validate_json('{}', 'my_file', force_reload=True)
            self.assertEqual(2, mocked_open.call_count)
