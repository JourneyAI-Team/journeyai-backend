import json
import os
from typing import Any

from jinja2 import Template
from loguru import logger

from app.clients.openai_client import get_openai_async_client
from app.models.assistant import Assistant

openai = get_openai_async_client()


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
        If the master.md file, metadata.json file, or assistant directory does not exist.
    """

    internal_name = name

    with logger.contextualize(assistant_internal_name=internal_name):
        logger.info(f"Starting preloaded assistant insertion for '{name}'")

        assistant_dir_path = os.path.join(os.getcwd(), "prompts", "assistants", name)
        master_file_path = os.path.join(assistant_dir_path, "master.md")
        metadata_file_path = os.path.join(assistant_dir_path, "metadata.json")

        logger.debug(f"Assistant directory path: {assistant_dir_path}")
        logger.debug(f"Master file path: {master_file_path}")
        logger.debug(f"Metadata file path: {metadata_file_path}")

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

        # Read metadata.json for the assistant metadata
        try:
            with open(metadata_file_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
            logger.debug("Successfully read metadata.json file")
        except FileNotFoundError:
            logger.error(f"Metadata file not found: {metadata_file_path}")
            raise
        except Exception as e:
            logger.exception(f"Error reading metadata.json file: {str(e)}")
            raise

        # Extract values from metadata with defaults
        assistant_name = metadata.get("name", name.replace("_", " ").title())
        description = metadata.get("description", f"Pre-loaded assistant: {name}")
        category = metadata.get("category", "General")
        tool_config = metadata.get("tool_config", {"tools": []})
        model = metadata.get("model", "gpt-4o")
        version = metadata.get("version", "0.0.1")

        # Create Assistant object
        assistant = Assistant(
            name=assistant_name,
            internal_name=internal_name,
            description=description,
            category=category,
            tool_config=tool_config,
            developer_prompt=developer_prompt,
            model=model,
            testing=True,  # Mark as testing since it's pre-loaded
            version=version,
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

            # Upload files to OpenAI and create vector store
            if md_files:
                try:
                    # Create vector store first
                    vector_store = await openai.vector_stores.create(
                        name=f"assistant:{assistant.id}"
                    )
                    logger.debug(f"Created vector store with ID: {vector_store.id}")

                    # Upload each file to OpenAI
                    uploaded_files = 0
                    for filename in md_files:
                        file_path = os.path.join(assistant_dir_path, filename)

                        try:
                            # Upload file to OpenAI
                            with open(file_path, "rb") as file_content:
                                file_result = await openai.files.create(
                                    file=file_content, purpose="assistants"
                                )

                            logger.debug(
                                f"Uploaded file '{filename}' with ID: {file_result.id}"
                            )

                            # Add file to vector store
                            await openai.vector_stores.files.create(
                                vector_store_id=vector_store.id, file_id=file_result.id
                            )

                            uploaded_files += 1
                            logger.debug(f"Added file '{filename}' to vector store")

                        except Exception as e:
                            logger.exception(
                                f"Error processing file '{filename}': {str(e)}"
                            )
                            # Continue with other files even if one fails
                            continue

                    # Update assistant's tool_config with vector store ID
                    if "vector_store_ids" not in assistant.tool_config:
                        assistant.tool_config["vector_store_ids"] = []
                    assistant.tool_config["vector_store_ids"].append(vector_store.id)

                    # Save the updated assistant
                    await assistant.save()

                    logger.success(
                        f"Successfully created assistant '{name}' with {uploaded_files} files uploaded to vector store {vector_store.id}"
                    )

                except Exception as e:
                    logger.exception(
                        f"Error creating vector store or uploading files: {str(e)}"
                    )
                    raise
            else:
                logger.info(f"No markdown files found to upload for assistant '{name}'")
            return assistant
