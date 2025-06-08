import os
from typing import Any

from jinja2 import Template


def render_prompt_template(
    file_path: str, context: dict[str, Any] | None = None
) -> str:
    """
    Read a markdown file from the prompts folder and render it using Jinja2.

    Parameters
    ----------
    file_path : str
        Path to the markdown file relative to the prompts folder.
        Example: "internal/context.md" resolves to "./prompts/internal/context.md"
    context : dict[str, Any], optional
        Dictionary containing variables to be used in Jinja2 template rendering.
        If None, an empty dictionary is used.

    Returns
    -------
    str
        The rendered template as a string.

    Raises
    ------
    FileNotFoundError
        If the specified markdown file does not exist.
    """

    if context is None:
        context = {}

    # Construct the full path relative to current working directory
    full_path = os.path.join(os.getcwd(), "prompts", file_path)

    # Read the markdown file
    with open(full_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    # Create Jinja2 template and render with context
    template = Template(template_content)
    rendered_content = template.render(**context)

    return rendered_content
