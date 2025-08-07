import unittest
import os
import csv
import json
import sys
#   sys.path.insert(0, os.path.abspath(
#   os.path.join(os.path.dirname(__file__), '../elabforms')))
from elabforms.template_builder import TemplateBuilder
from elabforms.template_part import TemplatePart
from elabforms.template import Template


class TestTemplateBuilder(unittest.TestCase):
    def setUp(self):
        """
        Prepares the necessary files for the tests.
        """
        self.template_parts_list_file = "test_template_parts_list.csv"
        self.template_file_path = "output_template.json"

        # Create test JSON files for template parts
        self.template_part_1 = "template_part_1.json"
        self.template_part_2 = "template_part_2.json"

        template_part_1_content = {
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

        template_part_2_content = {
            "elabftw": {
                "extra_fields_groups": [
                    {"id": 2, "name": "Group 2"}
                ]
            },
            "extra_fields": {
                "field2": {
                    "type": "number",
                    "value": "",
                    "group_id": 2
                }
            }
        }

        with open(self.template_part_1, "w") as f:
            json.dump(template_part_1_content, f)

        with open(self.template_part_2, "w") as f:
            json.dump(template_part_2_content, f)

        # Create a CSV file listing the template parts
        with open(self.template_parts_list_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([self.template_part_1])
            writer.writerow([self.template_part_2])

    def tearDown(self):
        """
        Cleans up the files created after the tests.
        """
        for file in [self.template_parts_list_file, self.template_part_1,
                     self.template_part_2, self.template_file_path]:
            if os.path.exists(file):
                os.remove(file)

    def test_read_template_parts_list(self):
        """
        Tests reading the list of template parts from a CSV file.
        """
        template_builder = TemplateBuilder(self.template_parts_list_file)
        self.assertEqual(template_builder.template_parts_list,
                         [self.template_part_1, self.template_part_2])

    def test_build_template(self):
        """
        Tests generating a complete template from the parts.
        """
        TemplateBuilder.build_template(self.template_parts_list_file,
                                       self.template_file_path)

        # Check that the final template file was created
        self.assertTrue(os.path.exists(self.template_file_path))

        # Verify the content of the generated file
        with open(self.template_file_path, "r") as f:
            full_template_content = json.load(f)

        self.assertEqual(len(
            full_template_content["elabftw"]["extra_fields_groups"]), 2)
        self.assertIn("field1", full_template_content["extra_fields"])
        self.assertIn("field2", full_template_content["extra_fields"])


if __name__ == "__main__":
    unittest.main()