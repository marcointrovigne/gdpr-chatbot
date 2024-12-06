import asyncio
import json
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from loguru import logger

from schemas.schema import RegulationModel
from tools.agents import agent_article

load_dotenv()


class PDFExtractor:
    """
    A class for extracting and structuring regulatory content from GDPR PDF documents.

    This class specifically handles the extraction of regulatory articles, commentaries,
    and recitals from GDPR document. It provides functionality to parse PDF content
    into structured data following standard regulatory formats.

    Attributes:
        dataset_path (str): Base directory path for input/output files
        pdf_file (str): GDPR pdf file name (inside dataset folder)
        scopes (List[str]): Valid processing scopes (article, commentary, recitals)

    Example:
        >>> extractor = PDFExtractor("path/to/dataset")
        >>> structured_data = extractor.create_structured_data()
    """

    def __init__(self,
                 dataset_path: str) -> None:
        """
        Initialize the PDFExtractor with the specified dataset path.

        Args:
            dataset_path (str): Path to the directory containing GDPR PDF
                              and where output will be stored

        Raises:
            FileNotFoundError: If the specified PDF file is not found at the expected location
        """
        self.dataset_path = dataset_path
        self.pdf_file = os.path.join(self.dataset_path, "GDPR_Art_1-21.pdf")
        self.scopes = ["article", "commentary", "recitals"]
        logger.info(f"Initialized PDFExtractor with dataset path: {self.dataset_path}")
        if not os.path.exists(self.pdf_file):
            logger.error(f"PDF file not found: {self.pdf_file}")
            raise FileNotFoundError(f"PDF file not found at {self.pdf_file}")

    def _save_markdown_files(self, articles: dict[str, str]) -> None:
        """
        Save extracted articles as individual markdown files.

        This method creates a directory structure for raw article content,
        preserving the original text in markdown format.

        Args:
            articles (Dict[str, str]): Dictionary mapping article identifiers to their content
        """
        articles_path = os.path.join(self.dataset_path, "raw_articles")

        # Create output directory if it doesn't exist
        if not os.path.exists(articles_path):
            os.makedirs(articles_path)

        logger.info(f"Saving articles to directory: {articles_path}")

        for key, content in articles.items():
            file_path = os.path.join(articles_path, f"{key}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                logger.info(f"Successfully saved article: {key}")

    def _split_articles(self,
                        save_md_files: bool = True) -> dict[str, str]:
        """
        Split GDPR PDF content into the 21 articles.

        This method processes the PDF document page by page, identifying article
        boundaries and maintaining the hierarchical structure of the regulation.
        It handles the specific format where articles begin with "EN\nArticle".

        Args:
            save_md_files (bool): Whether to save extracted articles as markdown files

        Returns:
            Dict[str, str]: Dictionary mapping article identifiers to their content

        Raises:
            Exception: Any error during PDF processing is logged and re-raised
        """
        try:
            # Load PDF document
            logger.info(f"Loading PDF file: {self.pdf_file}")
            loader = PyPDFLoader(self.pdf_file)
            pages = [page for page in loader.lazy_load()]
            logger.info(f"Successfully loaded {len(pages)} pages")

            # Process pages and extract articles
            articles: dict[str, str] = {}
            article = 0
            for i, page in enumerate(pages):
                logger.info(f"Processing page {i + 1}/{len(pages)}")

                # Check for new article marker
                if page.page_content.startswith("EN\nArticle"):
                    article += 1
                    logger.info(f"Found Article {article} on page {i + 1}")
                    articles[f"article_{article}"] = page.page_content
                else:
                    # Append content to current article
                    articles[f"article_{article}"] += f"\n{page.page_content}"

            # Save markdown files if requested
            if save_md_files:
                self._save_markdown_files(articles=articles)
            logger.info(f"Successfully extracted {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise

    def _save_json_file(self, key: str, structured_article: RegulationModel) -> None:
        """
        Save structured article data to JSON file.

        Creates a structured output directory and saves the processed GDPR article
        content in JSON format, maintaining the schema defined by RegulationModel.

        Args:
            key (str): Identifier for the article
            structured_article (RegulationModel): Processed article data
        """
        output_path = os.path.join(self.dataset_path, "structured_output")

        # Create output directory if needed
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        file_path = os.path.join(output_path, f"{key}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(structured_article.model_dump(), f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully saved structured data: {key}")

    async def create_structured_data(self,
                                     save_files: bool = True) -> list[RegulationModel]:
        """
        Create structured regulatory data from PDF content asynchronously.

        Processes multiple GDPR articles concurrently, extracting article content,
        recitals, and expert commentary. Uses asyncio to parallelize agent calls
        for improved performance.

        Args:
            save_files: Flag to save structured output as JSON files.
                       Defaults to True.

        Returns:
            List of RegulationModel instances containing structured GDPR data.
        """
        logger.info("Starting GDPR data structuring process")

        # Extract articles from PDF
        articles = self._split_articles(save_md_files=save_files)
        structured_articles: list[RegulationModel] = []

        async def process_article(key: str, content: str) -> RegulationModel:
            # Create wrapper coroutines for the synchronous agent_article function
            async def run_agent(scope: str):
                return agent_article(article_name=key, article_content=content, scope=scope)

            # Create tasks from the wrapper coroutines
            article_task = asyncio.create_task(run_agent("article"))
            recitals_task = asyncio.create_task(run_agent("recitals"))
            commentary_task = asyncio.create_task(run_agent("commentary"))

            # Wait for all tasks to complete in parallel
            json_article, json_recitals, json_commentary = await asyncio.gather(
                article_task,
                recitals_task,
                commentary_task
            )

            return RegulationModel(
                title=json_article.title,
                article_num=json_article.article_num,
                articles=json_article.articles,
                recitals=json_recitals.recitals,
                expert_commentary=json_commentary.expert_commentary,
                guidelines_case_law=json_commentary.guidelines_case_law
            )

        # Process each article
        for key, content in articles.items():
            logger.info(f"Processing structured data for {key}")

            # Process article data concurrently
            structured_article = await process_article(key, content)
            structured_articles.append(structured_article)
            logger.info(f"Successfully structured {key}")

            if save_files:
                self._save_json_file(key, structured_article)
        return structured_articles
