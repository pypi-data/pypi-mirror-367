import json


class Template:
    """
    Class to manage a template for ElabFTW.
    """

    def __init__(self, template_file=None):
        """
        Initializes the Template object.

        Attributes:
             template_content (dict): Content of the template,
        loaded from the JSON file.

        Parameters:
            template_file (str): Path to the JSON file.
        """
        if template_file is None:
            self.template_content = {}
        else:
            self.template_file = template_file
            self.template_content = self.read_template(template_file)

    @staticmethod
    def read_template(template_file):
        """
        Reads a JSON template file and validates its structure.

        Parameters:
            template_file (str): Path to the JSON file.

        Returns:
            dict: Content of the JSON file.

        Raises:
            ValueError: If the structure is invalid.
        """
        try:
            with open(template_file, 'r') as f:
                template_content = json.load(f)
                Template.check_structure(template_content)
                return template_content
        except KeyError as e:
            raise ValueError(f"Invalid template file: missing key {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {template_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")

    @staticmethod
    def check_structure(template_file_content):
        """
        Validates the structure of a template.

        Parameters:
            template_file_content (dict): JSON content of the file.

        Raises:
            ValueError: If the structure is invalid.
        """
        required_keys = ['elabftw', 'extra_fields']
        for key in required_keys:
            if key not in template_file_content:
                raise ValueError(f"Invalid template file: missing key {key}")

        if 'extra_fields_groups' not in template_file_content['elabftw']:
            raise ValueError("Invalid template file: missing "
                             "'extra_fields_groups' key")
        if not isinstance(
                template_file_content['elabftw']['extra_fields_groups'], list):
            raise ValueError("'extra_fields_groups' must be a list")
        if not template_file_content['elabftw']['extra_fields_groups']:
            raise ValueError("The 'extra_fields_groups' list is empty")
        if not all(isinstance(group, dict) for group in
                   template_file_content['elabftw']['extra_fields_groups']):
            raise ValueError("'extra_fields_groups' must contain dictionaries")
        if not all('id' in group for group in
                   template_file_content['elabftw']['extra_fields_groups']):
            raise ValueError("'extra_fields_groups' dictionaries must have an "
                             "'id' key")

    def add_template_part(self, new_template_part):
        """
        Add a new template part to the current template
        Parameters:
            new_template_part (Template): A Template object
            containing the new content to add.

        Returns:
            dict: Merged content.
        """
        self.template_content['elabftw']['extra_fields_groups'].extend(
            new_template_part.template_content['elabftw'][
                'extra_fields_groups']
        )
        self.template_content['extra_fields'].update(
            new_template_part.template_content['extra_fields']
        )
        return self

    def save_template(self, template_file_path):
        """
        Saves the current template content to a JSON file.

        Parameters:
            template_file_path (str): Path to the output JSON file.

        Returns:
            None
        """
        with open(template_file_path, 'w') as f:
            json.dump(self.template_content, f, indent=4)

    def is_empty(self):
        """
        Checks if the template content is empty.

        Returns:
            bool: True if the template content is empty, False otherwise.
        """
        return not bool(self.template_content)
