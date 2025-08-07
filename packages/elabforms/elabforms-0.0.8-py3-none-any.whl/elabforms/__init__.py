"""
A set of tools to create and manage standardized forms for eLabFTW

"""

from . import generate_templates
from .template_builder import TemplateBuilder
from .template_part import TemplatePart
from .template import Template

__all__ = [
    "generate_templates",
    "TemplateBuilder",
    "TemplatePart",
    "Template",
]
