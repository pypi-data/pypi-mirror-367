import os
import csv
from .template_part import TemplatePart
from .template import Template


class TemplateBuilder:
    """
    Class to generate a complete template from multiple parts.
    """

    def __init__(self, template_parts_list_file, template_file_path=None):
        """
        Class to generate a complete template from multiple parts.

        Attributes:
             template_parts_list_file (str): Path to the CSV file
                listing template parts.

             template_parts_list (list): List of JSON file paths for
             template parts.
              template_file_path (str, optional): Path to the
             output JSON file.
        """
        self.template_parts_list_file = template_parts_list_file
        self.template_parts_list = self.read_template_parts_list(
            template_parts_list_file)

        if template_file_path:
            self.template_file_path = template_file_path
            self.build_template(template_parts_list_file, template_file_path)

    @staticmethod
    def read_template_parts_list(template_parts_list_file):
        """
        Reads a list of template part files from a CSV file.

        Parameters:
            template_parts_list_file (str): Path to the CSV file.

        Returns:
            list: List of JSON file paths.

        Raises:
            ValueError: If the file extension is not supported.
            FileNotFoundError: If a file is not found.
        """
        if not template_parts_list_file.endswith('.csv'):
            raise ValueError(
                f"Unsupported file extension: {template_parts_list_file}")

        with open(template_parts_list_file, 'r') as f:
            reader = csv.reader(f)
            template_parts_list = [row[0] for row in reader if row]

        for template_part in template_parts_list:
            if not os.path.exists(template_part):
                raise FileNotFoundError(f"File not found: {template_part}")
            if not template_part.endswith('.json'):
                raise ValueError(
                    f"The file must be in JSON format: {template_part}")

        return template_parts_list

    @staticmethod
    def build_template(template_parts_list_file, template_file_path):
        """
     Generates a complete template by merging all the listed parts.

     Parameters:
            template_parts_list_file (str): Path to the CSV file
     listing the parts.
            template_file_path (str): Path to the output JSON file.

     Returns:
         None
     """
        template_builder = TemplateBuilder(template_parts_list_file)

        full_template = Template()

        for new_id, template_part_file in enumerate(
                template_builder.template_parts_list):
            template_part = TemplatePart(template_part_file)

            template_part.set_content_id(new_id + 1)

            if full_template.is_empty():
                full_template = template_part
            else:
                full_template.add_template_part(
                                                template_part)

        full_template.save_template(template_file_path)
