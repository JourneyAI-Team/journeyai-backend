import json
import os
from typing import Any

from jinja2 import Template
from loguru import logger

from app.clients.arq_client import get_arq
from app.models.artifact import Artifact
from app.models.assistant import Assistant
from app.schemas.types import OriginType


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


def is_assistant_pre_loaded(name: str) -> bool:
    """
    Check if an assistant has pre-loaded prompts in the prompts/assistants folder.

    Parameters
    ----------
    name : str
        The name of the assistant to check for pre-loaded content.

    Returns
    -------
    bool
        True if the assistant directory exists in prompts/assistants/, False otherwise.
    """
    assistant_dir_path = os.path.join(os.getcwd(), "prompts", "assistants", name)
    return os.path.isdir(assistant_dir_path)


async def insert_preloaded_assistant(
    name: str,
) -> Assistant:
    """
    Create an Assistant object from pre-loaded prompts and create Artifact objects
    for assistant documents.

    Parameters
    ----------
    name : str
        The name of the assistant directory in prompts/assistants/

    Returns
    -------
    Assistant
        The created Assistant object

    Raises
    ------
    FileNotFoundError
        If the master.md file or assistant directory does not exist.
    """

    internal_name = name

    with logger.contextualize(assistant_internal_name=internal_name):
        logger.info(f"Starting preloaded assistant insertion for '{name}'")

        arq = await get_arq()

        assistant_dir_path = os.path.join(os.getcwd(), "prompts", "assistants", name)
        master_file_path = os.path.join(assistant_dir_path, "master.md")
        tool_config_path = os.path.join(assistant_dir_path, "tool_config.json")

        logger.debug(f"Assistant directory path: {assistant_dir_path}")
        logger.debug(f"Master file path: {master_file_path}")
        logger.debug(f"Tool config file path: {tool_config_path}")

        # Check if the assistant is already in the database
        existing_assistant = await Assistant.find_one({"internal_name": internal_name})
        if existing_assistant:
            logger.info(f"Assistant '{name}' already exists in database")
            return existing_assistant

        # Read master.md for the developer_prompt
        try:
            with open(master_file_path, "r", encoding="utf-8") as file:
                developer_prompt = file.read()
            logger.debug(
                f"Successfully read master.md file ({len(developer_prompt)} characters)"
            )
        except FileNotFoundError:
            logger.error(f"Master file not found: {master_file_path}")
            raise
        except Exception as e:
            logger.exception(f"Error reading master.md file: {str(e)}")
            raise

        # Read tool_config.json for the tool configuration
        try:
            with open(tool_config_path, "r", encoding="utf-8") as file:
                tool_config = json.load(file)
            logger.debug("Successfully read tool_config.json file")
        except FileNotFoundError:
            logger.error(f"Tool config file not found: {tool_config_path}")
            raise
        except Exception as e:
            logger.exception(f"Error reading tool_config.json file: {str(e)}")
            raise

        # Create Assistant object with placeholders for other fields
        assistant = Assistant(
            name=name.replace("_", " ").title(),
            internal_name=internal_name,
            description=f"Pre-loaded assistant: {name}",
            tool_config=tool_config,
            developer_prompt=developer_prompt,
            model="gpt-4o",  # Default model
            testing=True,  # Mark as testing since it's pre-loaded
            version="0.0.1",
        )

        # Save the assistant to get an ID
        await assistant.insert()
        logger.info(f"Assistant '{name}' created with ID: {assistant.id}")

        with logger.contextualize(assistant_id=assistant.id):
            # Get all .md files in the assistant directory except master.md
            try:
                md_files = []
                for filename in os.listdir(assistant_dir_path):
                    if filename.endswith(".md") and filename != "master.md":
                        md_files.append(filename)

                logger.debug(
                    f"Found {len(md_files)} markdown files to process: {md_files}"
                )
            except Exception as e:
                logger.exception(
                    f"Error listing files in assistant directory: {str(e)}"
                )
                raise

            # Create Artifact objects for each .md file
            artifacts_created = 0
            for filename in md_files:
                file_path = os.path.join(assistant_dir_path, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_content = file.read()

                    # Create artifact with type "assistant_document"
                    artifact = Artifact(
                        type="assistant_document",
                        origin_type=OriginType.USER,
                        title=filename,
                        body=file_content,
                        assistant_id=assistant.id,
                    )

                    await artifact.insert()
                    await arq.enqueue_job(
                        "post_artifact_creation", artifact.id, _queue_name="artifacts"
                    )

                    artifacts_created += 1
                    logger.debug(
                        f"Created artifact for file '{filename}' with ID: {artifact.id}"
                    )

                except Exception as e:
                    logger.exception(f"Error processing file '{filename}': {str(e)}")
                    # Continue with other files even if one fails
                    continue

            logger.success(
                f"Successfully created assistant '{name}' with {artifacts_created} artifacts"
            )
            return assistant
