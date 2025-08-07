import sys
from .template_builder import TemplateBuilder
import argparse

def main(template_parts_list_file, output_template_file):
    """
    Main function to execute the template generation.
    """
    try:
        TemplateBuilder(template_parts_list_file, output_template_file)
        print(f"Template successfully generated and saved to {output_template_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cli():
    """
    Command-line interface using argparse.
    """
    argparser = argparse.ArgumentParser(
        description="Generate a JSON template from a CSV list of parts."
    )
    argparser.add_argument(
        "-l", "--template_parts_list", dest="template_parts_list_file", required=True, type=str,
        help="Path to the CSV file listing the parts of the template"
    )
    argparser.add_argument(
        "-o", "--output", dest="output_template_file", required=True, type=str,
        help="Path to the output JSON template file"
    )
    args = argparser.parse_args()
    main(args.template_parts_list_file, args.output_template_file)

if __name__ == "__main__":
    cli()