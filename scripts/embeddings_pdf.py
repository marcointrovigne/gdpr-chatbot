import asyncio
import os
from pathlib import Path

from loguru import logger

from schemas.schema import RegulationModel
from tools.embedding import Embedding
from tools.pdf_extractor import PDFExtractor


async def create_embeddings(save_files: bool = False,
                            force_delete: bool = True) -> list[RegulationModel]:
    """
    Asynchronously create vector embeddings for GDPR regulatory content from PDF documents.

    This function processes PDF documents containing GDPR articels, extracts structured data,
    and creates vector embeddings for both articles and recitals. The embeddings are stored
    in a vector database for efficient similarity search.

    The function performs the following steps:
    1. Extracts structured data from PDF documents
    2. Creates embeddings for recitals
    3. Creates embeddings for articles and their components
    4. Optionally saves the structured data to files

    Args:
        save_files (bool, optional): Whether to save the extracted structured data to files.
            Defaults to False.
        force_delete (bool, optional): Whether to force delete existing embeddings.
            Defaults to True.

    Returns:
        List[RegulationModel]: List of processed regulation models containing the structured data.

    Raises:
        Exception: If there are errors during PDF extraction or embedding creation.

    Example:
        >>> structured_articles = await create_embeddings_async(save_files=True)
        This will process PDFs and create embeddings asynchronously.
    """
    # Get the dataset path relative to the current file
    dataset_path = os.path.join(Path(__file__).parent.parent, "dataset")
    logger.info(f"Processing PDFs from dataset path: {dataset_path}")

    # Initialize PDF extractor
    pdf_extractor = PDFExtractor(dataset_path=dataset_path)

    # Extract structured data from PDFs
    logger.info("Extracting structured data from PDFs...")
    structured_articles = await pdf_extractor.create_structured_data(save_files=save_files)
    logger.info(f"Successfully extracted structured data")

    # Initialize embedding handler
    em = Embedding(force_delete=force_delete)

    # Process embeddings concurrently using thread pool
    try:
        # Create tasks for concurrent processing
        logger.info("Creating embedding tasks...")
        tasks = [
            asyncio.create_task(asyncio.to_thread(em.create_recitals_documents, structured_articles)),
            asyncio.create_task(asyncio.to_thread(em.create_article_documents, structured_articles))
        ]

        # Wait for both tasks to complete
        await asyncio.gather(*tasks)
        logger.info("Successfully created embeddings for articles and recitals")

    except Exception as e:
        logger.info(f"Failed to create embeddings: {str(e)}")
        raise

    return structured_articles


async def main(save_files: bool = False,
               force_delete: bool = True):
    """Main async function to run the embedding creation."""
    try:
        await create_embeddings(save_files=save_files, force_delete=force_delete)
    except Exception as e:
        logger.error(f"Embedding creation failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main(save_files=False,
                     force_delete=True))
