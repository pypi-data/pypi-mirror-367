import unittest
import os
import json
import sys

#   sys.path.insert(0, os.path.abspath(
#   os.path.join(os.path.dirname(__file__), '../elabforms')))

from elabforms.template_part import TemplatePart


class TestTemplatePart(unittest.TestCase):
    def setUp(self):
        """
        Prepares the necessary data for the tests.
        """
        self.valid_template_part_content = {
            "elabftw": {
                "extra_fields_groups": [
                    {"id": 1, "name": "Group 1"}
                ]
            },
            "extra_fields": {
                "field1": {
                    "type": "text",
                    "value": "",
                    "group_id": 1
                }
            }
        }
        self.invalid_template_part_content = {
            "elabftw": {
                "extra_fields_groups": [
                    {"id": 1, "name": "Group 1"},
                    {"id": 2, "name": "Group 2"}
                ]
            },
            "extra_fields": {}
        }
        self.template_part_file = "test_template_part.json"
        with open(self.template_part_file, "w") as f:
            json.dump(self.valid_template_part_content, f)

    def tearDown(self):
        """
        Cleans up the files created after the tests.
        """
        if os.path.exists(self.template_part_file):
            os.remove(self.template_part_file)

    def test_valid_template_part(self):
        """
        Tests the creation of a valid TemplatePart.
        """
        template_part = TemplatePart(self.template_part_file)
        self.assertEqual(template_part.template_content,
                         self.valid_template_part_content)

    def test_invalid_template_part_structure(self):
        """
        Tests the validation of an invalid structure.
        """
        with open(self.template_part_file, "w") as f:
            json.dump(self.invalid_template_part_content, f)
        with self.assertRaises(ValueError):
            TemplatePart(self.template_part_file)

    def test_set_content_id(self):
        """
        Tests updating the ID in a TemplatePart.
        """
        template_part = TemplatePart(self.template_part_file)
        updated_template_part = template_part.set_content_id(2)
        for group in (
                updated_template_part.template_content
        )['elabftw']['extra_fields_groups']:
            self.assertEqual(group['id'], 2)
        for field in (
                updated_template_part.template_content['extra_fields'].values()
        ):
            self.assertEqual(field['group_id'], 2)


if __name__ == "__main__":
    unittest.main()