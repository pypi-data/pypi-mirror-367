from .template import Template


class TemplatePart(Template):
    """
    Class to manage a template part for ElabFTW.
    Inherits from the Template class.
    """

    def __init__(self, template_file):
        """
        Initializes the TemplatePart object.

        Parameters:
            template_file (str): Path to the JSON file.
        """
        super().__init__(template_file)

        # Call the structure validation for the template content
        self.check_structure(self.template_content)

    @staticmethod
    def check_structure(template_file_content):
        """
        Validates the structure of a template part.

        Parameters:
            template_file_content (dict): JSON content of the file.

        Raises:
            ValueError: If the structure is invalid.
        """
        # Call the base validation from the Template class
        Template.check_structure(template_file_content)

        # Ensure there is only one groupfield
        if len(template_file_content['elabftw']['extra_fields_groups']) > 1:
            raise ValueError("The 'extra_fields_groups' list must contain only"
                             "one groupfield for a template part.")

    def set_content_id(self, new_id):
        """
        Updates the IDs of the contents in a template part.

        Parameters:
            new_id (int): New ID to assign.

        Returns:
            TemplatePart: The updated template part with the new ID set.
        """
        template_parts_file_content = self.template_content

        # Update the ID for each group in 'extra_fields_groups'
        for group in template_parts_file_content['elabftw'][
                    'extra_fields_groups']:
            group['id'] = new_id

        # Update the group_id for each field in 'extra_fields'
        for field in template_parts_file_content['extra_fields'].values():
            field['group_id'] = new_id

        # Update the template content with the new ID
        self.template_content = template_parts_file_content
        return self
