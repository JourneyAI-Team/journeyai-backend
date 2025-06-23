from loguru import logger
from fastapi import HTTPException, UploadFile, status

from app.clients.openai_client import get_openai_async_client

openai = get_openai_async_client()


async def insert_uploaded_session_file(file: UploadFile, vector_store_id: str):
    with logger.contextualize(vector_store_id=vector_store_id, file=file.filename):
        try:
            uploaded_file = await openai.files.create(
                file=(file.filename, file.file), purpose="assistants"
            )

            logger.success(f"File uploaded successfully. {file.filename=}")

            await openai.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=uploaded_file.id,
            )

            logger.success(f"File added to vector store successfully. {file.filename=}")

            return uploaded_file
        except Exception as e:
            logger.exception(f"Error uploading file. {file.filename=}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e,
            ) from e


async def batch_insert_uploaded_session_files(
    files: list[UploadFile], vector_store_id: str
):
    with logger.contextualize(vector_store_id=vector_store_id, files=files):

        uploaded_files = 0
        for file in files:

            try:
                # Upload file to OpenAI

                uploaded_file = await openai.files.create(
                    file=(file.filename, file.file), purpose="assistants"
                )

                logger.debug(
                    f"Uploaded file '{file.filename}' with ID: {uploaded_file.id}"
                )

                # Add file to vector store
                await openai.vector_stores.files.create(
                    vector_store_id=vector_store_id, file_id=uploaded_file.id
                )

                uploaded_files += 1
                logger.debug(f"Added file '{file.filename}' to vector store")

            except Exception as e:
                logger.exception(f"Error processing file '{file.filename}': {str(e)}")
                # Continue with other files even if one fails
                continue
