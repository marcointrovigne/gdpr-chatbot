import asyncio
import json
import os
from pathlib import Path

from loguru import logger

from schemas.schema import RegulationModel
from tools.embedding import Embedding


async def create_embeddings(force_delete: bool = True):
    """
    Create vector embeddings for GDPR regulatory content asynchronously.

    This function processes structured GDPR content from JSON files and creates
    vector embeddings for both articles and recitals. The embeddings are stored
    in a vector database for efficient similarity search.

    The function performs the following steps:
    1. Loads structured JSON files from the dataset directory
    2. Converts JSON data to RegulationModel instances
    3. Creates embeddings for recitals
    4. Creates embeddings for articles and their components

    Args:
        force_delete (bool, optional): Whether to force delete existing embeddings.
            Defaults to True.

    Example:
        >>> await create_embeddings(force_delete=True)
        This will create new embeddings for all regulatory content concurrently.
    """
    # Initialize empty list for storing regulation models
    articles = []

    # Construct path to structured output directory
    dataset_path = os.path.join(Path(__file__).parent.parent, "dataset", "structured_output")

    # Process each JSON file in the directory
    for filename in os.listdir(dataset_path):
        if filename.endswith(".json"):
            with open(os.path.join(dataset_path, filename), "r") as f:
                file_data = json.load(f)

        articles.append(RegulationModel(**file_data))

    # Initialize embedding handler
    em = Embedding(force_delete=force_delete)
    # Process embeddings concurrently using thread pool
    try:
        # Process embeddings concurrently
        # Using asyncio.to_thread directly as it manages its own thread pool
        tasks = [
            asyncio.create_task(asyncio.to_thread(em.create_article_documents, articles)),
            asyncio.create_task(asyncio.to_thread(em.create_recitals_documents, articles))
        ]

        # Wait for both tasks to complete
        await asyncio.gather(*tasks)
        logger.info("Async embedding creation completed successfully")

    except Exception as e:
        logger.error(f"Failed to create embeddings: {str(e)}")
        raise

    logger.info("Async embedding creation completed successfully")


async def main(force_delete: bool = True):
    """Main async function to run the embedding creation."""
    try:
        await create_embeddings(force_delete=force_delete)
    except Exception as e:
        logger.error(f"Embedding creation failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main(force_delete=True))
