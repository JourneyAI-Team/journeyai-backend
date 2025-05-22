def construct_embedding_input_for_artifact(title: str, body: str, source: str):
    embedding_input = f"""
    Title: {title}
    Body: {body}
    """
    if source == "user":
        embedding_input = (
            """
        Uploaded by User
        """
            + embedding_input
        )
    return embedding_input


def construct_embedding_input_for_messages():
    pass
