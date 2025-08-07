import csv
import json
import os
import sys


def read_template_parts_list(template_parts_list_file):
    """
    Reads a file containing a list of template parts to be concatenated.

    Parameters:
        template_parts_list_file (str): Path to the .csv or .txt file
        containing the list.

    Returns:
        list of str: A list of file paths as strings.

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
    """

    template_parts_list = []
    if template_parts_list_file.endswith('.csv'):
        template_parts_list = read_template_parts_list_csv(
            template_parts_list_file)
    else:
        raise ValueError(
            f"Unsupported file extension: {template_parts_list_file}")
    for template_part in template_parts_list:
        if not os.path.exists(template_part):
            raise FileNotFoundError(f"File not found: {template_part}")
        if not template_part.endswith('.json'):
            raise ValueError(f"File must be in json format: {template_part}")
    return template_parts_list


def read_template_parts_list_csv(template_parts_list_file):
    """
    Reads file paths from a CSV file. Assumes the first column contains
    the paths.

    Parameters:
        template_parts_list_file (str): Path to the CSV file.

    Returns:
        list of str: A list of strings from the first column of each row.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(template_parts_list_file, 'r') as f:
        reader = csv.reader(f)
        return [row[0] for row in reader if row]


def read_template_part(template_parts_file):
    """
    Reads a JSON template parts file and extracts the 'groupfield' and
    its details.

    Parameters:
        template_parts_file (str): Path to a JSON file representing a
        template parts.

    Returns:
      content (dict): The parsed JSON content.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON structure is invalid.
    """
    try:
        with open(template_parts_file, 'r') as f:
            template_parts_content = json.load(f)
            check_template_parts_structure(template_parts_content)

            return template_parts_content
    except KeyError as e:
        raise ValueError(f"Invalid template parts file: Missing key {e}")


def check_template_parts_structure(template_parts_file_content):
    """
    Validates the structure of a template parts content against Elab
    format rules.

    Parameters:
        template_parts_file_content (dict): The JSON-parsed content of
        the template parts.

    Returns:
        bool: True if the structure is valid.

    Raises:
        ValueError: If the structure does not meet the required format.
        Warning: If some fields do not have corresponding 'groupfield'
        mappings.
    """
    # Check if the required keys are present
    required_keys = ['elabftw', 'extra_fields']
    for key in required_keys:
        if key not in template_parts_file_content:
            raise ValueError(f"Invalid template parts file: Missing key {key}")

    # Check if 'elabftw' contains 'extra_fields_groups'
    if 'extra_fields_groups' not in template_parts_file_content['elabftw']:
        raise ValueError("Invalid template parts file: Missing "
                         "'extra_fields_groups' in 'elabftw'")
    if not isinstance(template_parts_file_content['elabftw']
                      ['extra_fields_groups'], list):
        raise ValueError("Invalid template parts file: 'extra_fields_groups' "
                         "should be a list")
    if not template_parts_file_content['elabftw']['extra_fields_groups']:
        raise ValueError("Invalid template parts file: 'extra_fields_groups' "
                         "list is empty")
    if not all(isinstance(group, dict) for group in
               template_parts_file_content['elabftw']['extra_fields_groups']):
        raise ValueError("Invalid template parts file: 'extra_fields_groups' "
                         "should contain"
                         "dictionaries")


def set_content_id(new_id, template_parts_file_content):
    """
    Updates the ID of the content in a template parts.

    Parameters:
        new_id (int): The new ID to assign.
        template_parts_file_content (dict): The original template parts
        content.

    Returns:
        dict: The updated template parts content.
    """
    # Update the ID in the 'extra_fields_groups'
    for group in template_parts_file_content['elabftw']['extra_fields_groups']:
        group['id'] = new_id

    # Update the ID in the 'extra_fields'
    for field in template_parts_file_content['extra_fields'].values():
        field['group_id'] = new_id

    return template_parts_file_content


def concatenate_templates(existing_template_parts_content,
                          new_template_part_content):
    """
    Concatenates the contents of two template parts.

    Parameters:
        existing_template_parts_content (dict): Content of the existing
        template.
        new_template_parts_content (dict): Content of the new template
        to append.

    Returns:
        dict: The merged template content.
    """
    # Merge the 'extra_fields_groups'
    existing_template_parts_content['elabftw']['extra_fields_groups'].extend(
        new_template_part_content['elabftw']['extra_fields_groups']
    )
    # Merge the 'extra_fields'
    existing_template_parts_content['extra_fields'].update(
        new_template_part_content['extra_fields']
    )
    return existing_template_parts_content


def save_template(full_template_content, template_file_path):
    """
    Saves the template content to a JSON file.

    Parameters:
        full_template_content (dict): The content to save.
        template_file_path (str): Path to the output JSON file.

    Returns:
        None
    """
    # Save the content to the file

    with open(template_file_path, 'w') as f:
        json.dump(full_template_content, f, indent=4)


def generate_template(template_parts_list_file, template_file_path):
    """
    Generates a full template by merging all template parts listed in a
    file.

    Parameters:
        template_parts_list_file (str): Path to a .csv or .txt file
        listing JSON parts files.
        template_file_path (str): Path to the output JSON file to save
        the template.

    Returns:
        None
    """
    # Read the list of template parts
    template_parts_list = read_template_parts_list(template_parts_list_file)

    # Initialize the full template content
    full_template_content = None

    # Iterate through each template part file
    for new_id, template_part_file in enumerate(template_parts_list):
        # Read the content of the current template part
        new_template_part_content = read_template_part(
            template_part_file)

        new_template_part_content = set_content_id(
            new_id + 1,
            new_template_part_content)
        if full_template_content is None:
            full_template_content = new_template_part_content
        else:
            full_template_content = concatenate_templates(
                full_template_content, new_template_part_content)

        # Update the ID of the content

    # Save the final merged template to a file
    save_template(full_template_content, template_file_path)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python generate_templates.py "
              "<template_parts_list_file.csv>"
              "<output_template.json>")
    else:
        generate_template(sys.argv[1], sys.argv[2])
