import unittest
import os
import json
import sys


from elabforms.template import Template  # noqa: E402


class TestTemplate(unittest.TestCase):
    def setUp(self):
        """
        Prepares the necessary data for the tests.
        """
        self.valid_template_content = {
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
        self.invalid_template_content = {
            "elabftw": {
                "extra_fields_groups": []
            }
        }
        self.template_file = "test_template.json"
        with open(self.template_file, "w") as f:
            json.dump(self.valid_template_content, f)

    def tearDown(self):
        """
        Cleans up the files created after the tests.
        """
        if os.path.exists(self.template_file):
            os.remove(self.template_file)

    def test_read_template_valid(self):
        """
        Tests reading a valid JSON file.
        """
        template = Template(self.template_file)
        self.assertEqual(template.template_content,
                         self.valid_template_content)

    def test_read_template_invalid(self):
        """
        Tests reading an invalid JSON file.
        """
        with open(self.template_file, "w") as f:
            json.dump(self.invalid_template_content, f)
        with self.assertRaises(ValueError):
            Template(self.template_file)

    def test_is_empty(self):
        """
        Tests if the is_empty method works correctly.
        """
        empty_template = Template()
        self.assertTrue(empty_template.is_empty())

        non_empty_template = Template(self.template_file)
        self.assertFalse(non_empty_template.is_empty())

    def test_save_template(self):
        """
        Tests saving a template to a file.
        """
        template = Template(self.template_file)
        output_file = "output_template.json"
        template.save_template(output_file)

        with open(output_file, "r") as f:
            saved_content = json.load(f)

        self.assertEqual(saved_content, self.valid_template_content)

        if os.path.exists(output_file):
            os.remove(output_file)

    def test_add_template_part(self):
        """
        Tests adding a new part to a template.
        """
        template = Template(self.template_file)
        new_template_part = Template()
        new_template_part.template_content = {
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
        template.add_template_part(new_template_part)
        self.assertEqual(len(
            template.template_content["elabftw"]["extra_fields_groups"]), 2)
        self.assertIn("field2",
                      template.template_content["extra_fields"])


if __name__ == "__main__":
    unittest.main()