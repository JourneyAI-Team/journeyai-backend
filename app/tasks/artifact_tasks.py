def post_artifact_creation():
    print("HELLOOOOOO")
    # # Generate embeddings from artifact
    # embedding_input = construct_embedding_input_for_artifact(
    #     title=new_artifact.title, body=new_artifact.body, source="user"
    # )

    # artifact_embeddings = await get_embeddings(embedding_input, source="user")

    # # Save embeddings to Qdrant
    # await insert_vector(
    #     collection_name="Artifacts",
    #     id=new_artifact.id,
    #     payload={
    #         "session_id": new_artifact.session_id,
    #         "user_id": new_artifact.user_id,
    #         "organization_id": new_artifact.organization_id,
    #         "account_id": new_artifact.account_id,
    #     },
    #     vector=artifact_embeddings,
    # )
    return "hello world"
