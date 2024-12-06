import uuid

from loguru import logger

from database.qdrant_db import Qdrant
from schemas.schema import RegulationModel, QdrantDocument
from tools.agents import contextual_embedding_agent


def find_article_summary(article_num: int) -> str:
    """
    Retrieve the summary of a GDPR article based on its number.

    This function maintains a comprehensive mapping of GDPR articles to their
    summaries, providing quick access to article overviews without needing
    to parse the full regulatory text.

    Args:
        article_num (int): The article number to look up (1-21)

    Returns:
        str: Formatted string containing article number, title, and summary.
             Returns empty string if article not found.

    Example:
        >>> find_article_summary(5)
        "Article 5-Principles relating to processing of personal data: Lists the core principles..."
    """
    # Static mapping of GDPR articles to their summaries
    articles_data = [
        {
            "article": 1,
            "title": "Subject-matter and objectives",
            "summary": "This article outlines the GDPR's purpose, which is to protect individuals' rights regarding their personal data and to regulate the processing of such data"
        },
        {
            "article": 2,
            "title": "Material scope",
            "summary": "Specifies the data processing activities that fall under the GDPR, including processing in the context of EU member states' activities, regardless of whether the processing occurs in the EU or not"
        },
        {
            "article": 3,
            "title": "Territorial scope",
            "summary": "Defines the geographical scope of the GDPR, applying to organizations based in the EU and those outside the EU that offer goods or services to, or monitor the behavior of, EU data subjects"
        },
        {
            "article": 4,
            "title": "Definitions",
            "summary": "Provides definitions for key terms used in the regulation, such as 'personal data', 'processing', 'controller', and 'processor'"
        },
        {
            "article": 5,
            "title": "Principles relating to processing of personal data",
            "summary": "Lists the core principles for processing personal data, including lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, and confidentiality"
        },
        {
            "article": 6,
            "title": "Lawfulness of processing",
            "summary": "Specifies the lawful bases for processing personal data, such as consent, contract necessity, legal obligation, vital interests, public task, and legitimate interests"
        },
        {
            "article": 7,
            "title": "Conditions for consent",
            "summary": "Details the conditions for obtaining valid consent from data subjects, emphasizing that consent must be freely given, specific, informed, and unambiguous"
        },
        {
            "article": 8,
            "title": "Conditions applicable to child's consent in relation to information society services",
            "summary": "Sets the age of consent for data processing related to information society services at 16, with the possibility for member states to lower it to no less than 13 years"
        },
        {
            "article": 9,
            "title": "Processing of special categories of personal data",
            "summary": "Prohibits processing of sensitive data (e.g., racial or ethnic origin, political opinions, religious beliefs) unless specific conditions are met, such as explicit consent or necessity for certain legal purposes"
        },
        {
            "article": 10,
            "title": "Processing of personal data relating to criminal convictions and offences",
            "summary": "States that processing personal data related to criminal convictions and offences requires a legal basis under EU or member state law"
        },
        {
            "article": 11,
            "title": "Processing which does not require identification",
            "summary": "Covers processing of data that doesn't require the identification of a data subject, setting limitations and obligations for controllers in such cases"
        },
        {
            "article": 12,
            "title": "Transparent information, communication and modalities for the exercise of the rights of the data subject",
            "summary": "Obligates controllers to provide information about data processing in a concise, transparent, and easily accessible form"
        },
        {
            "article": 13,
            "title": "Information to be provided where personal data are collected from the data subject",
            "summary": "Details the information that must be provided to data subjects when their data is collected directly, including the purpose of processing and the data retention period"
        },
        {
            "article": 14,
            "title": "Information to be provided where personal data have not been obtained from the data subject",
            "summary": "Specifies the information to be provided when data is not obtained directly from the data subject, including the source of the data"
        },
        {
            "article": 15,
            "title": "Right of access by the data subject",
            "summary": "Grants data subjects the right to access their personal data and obtain copies of it, along with other details about how and why their data is processed"
        },
        {
            "article": 16,
            "title": "Right to rectification",
            "summary": "Gives data subjects the right to have inaccurate personal data corrected and incomplete data completed"
        },
        {
            "article": 17,
            "title": "Right to erasure ('right to be forgotten')",
            "summary": "Allows data subjects to have their personal data erased under certain conditions, such as when the data is no longer necessary for its original purpose"
        },
        {
            "article": 18,
            "title": "Right to restriction of processing",
            "summary": "Provides data subjects the right to restrict processing of their data under certain circumstances, such as when the accuracy of the data is contested"
        },
        {
            "article": 19,
            "title": "Notification obligation regarding rectification or erasure of personal data or restriction of processing",
            "summary": "Requires controllers to notify all recipients of the data about any rectification, erasure, or restriction of processing, unless this proves impossible or involves disproportionate effort"
        },
        {
            "article": 20,
            "title": "Right to data portability",
            "summary": "Grants data subjects the right to receive their personal data in a structured, commonly used, and machine-readable format, and to transfer that data to another controller"
        },
        {
            "article": 21,
            "title": "Right to object",
            "summary": "Gives data subjects the right to object to the processing of their personal data based on certain grounds, including processing for direct marketing, research, or based on a public or legitimate interest"
        }
    ]
    for article in articles_data:
        if article['article'] == article_num:
            return f"Article {str(article_num)}-{article['title']}: {article['summary']}"
    return ""


def create_article_content(article: RegulationModel) -> str:
    """
    Create a consolidated content string from a RegulationModel instance.

    This function combines various components of a GDPR article (title,
    recitals, sub-articles, clauses, expert comment) into a single formatted string
    for processing and storage.

    Args:
        article (RegulationModel): The article model containing all components

    Returns:
        str: Formatted string containing all article content

    Example:
        >>> content = create_article_content(article)
        >>> print(content)
        "Article 5-Principles...\n\nArt. 1 - Lawfulness...\n\nRecital. 39: Data protection..."
    """
    # Get article title summary and expert comment
    title = find_article_summary(article_num=article.article_num)
    recitals = ""
    articles = ""
    comments = f"Expert Commentary: {article.expert_commentary}" if article.expert_commentary else ""

    # Process recitals
    for recital in article.recitals:
        recitals += f"Recital. {str(recital.number)}: {recital.content}\n"

    # Process sub-articles and clauses
    for art in article.articles:
        articles += f"\n\nArt. {str(art.number)} - {art.title}\n{art.content}"
        if art.clause:
            for clause in art.clause:
                articles += f"\n{clause.title}: {clause.content}"

    return title + "\n\n" + articles + "\n\n" + recitals + "\n\n" + comments


class Embedding:
    """
    Handles the creation and management of vector embeddings for GDPR articles
    and recitals using Qdrant vector database.

    This class processes regulatory content and creates searchable embeddings
    for both full articles and their individual components (recitals, clauses).
    It maintains contextual relationships between different parts of the regulation.

    Attributes:
        qdrant (Qdrant): Instance of Qdrant database handler

    Example:
        >>> embedding = Embedding(force_delete=True)
        >>> embedding.create_article_documents(articles)
    """

    def __init__(self, force_delete: bool = False):
        """
        Initialize the Embedding handler.

        Args:
            force_delete (bool): Whether to force delete existing collection
        """
        self.qdrant = Qdrant()
        self.qdrant.create_collection(force_delete=force_delete)

    def create_recitals_documents(self, articles: list[RegulationModel]) -> None:
        """
        Create embeddings for recitals from GDPR articles.

        Processes each recital within the articles, creating individual
        vector embeddings that maintain the relationship with their
        parent articles.

        Args:
            articles (List[RegulationModel]): List of GDPR articles
        """
        logger.info("Creating embeddings for recitals")

        for article in articles:
            logger.info(f"Processing recitals for Article {article.article_num}")

            for recital in article.recitals:
                rec_embed = f"Recital. {str(recital.number)}: {recital.content}"

                # Creating Document as written in the project requisites
                qdrant_document = QdrantDocument(
                    embed_text=rec_embed,
                    article_num=article.article_num,
                    article_summary=find_article_summary(article.article_num),
                    content=rec_embed,
                    category="recital",
                )

                # Created Qdrant point
                point = self.qdrant.create_point(bm25_text=qdrant_document.embed_text,
                                                 embed_text=qdrant_document.embed_text,
                                                 payload=qdrant_document.model_dump(),
                                                 id=str(uuid.uuid4()))

                # Upload point to Qdrant DB
                self.qdrant.upload_point(point=point)
                logger.info(f"Created embedding for Recital {recital.number}")

        logger.info("Completed recitals embedding creation")

    def create_article_documents(self, articles: list[RegulationModel]):
        """
        Create embeddings for GDPR articles and their components.

        Processes each article and its sub-components (sub-articles, clauses),
        creating contextual embeddings that capture the relationships between
        different parts of the regulation.

        Args:
            articles (List[RegulationModel]): List of GDPR articles
        """

        logger.info("Creating embeddings for articles")

        for article in articles:
            logger.info(f"Processing Article {article.article_num}")

            # Create the full article content for contextual embedding
            article_content = create_article_content(article=article)

            for art in article.articles:

                # Create base article embedding
                art_embed = f"Art. {str(art.number)} - {art.title}\n{art.content}"

                # Add clause content if present
                if art.clause:
                    for clause in art.clause:
                        art_embed += f"\n{clause.title}: {clause.content}"

                # Generate contextual embedding
                contextual_embedding = contextual_embedding_agent(chunk_content=art_embed,
                                                                  article_content=article_content)

                qdrant_document = QdrantDocument(
                    embed_text=f"{art_embed}\n\n{contextual_embedding}",
                    article_num=article.article_num,
                    article_summary=find_article_summary(article.article_num),
                    content=art_embed,
                    category="article"
                )

                # Created Qdrant point
                # Created Qdrant point
                point = self.qdrant.create_point(bm25_text=qdrant_document.embed_text,
                                                 embed_text=qdrant_document.embed_text,
                                                 payload=qdrant_document.model_dump(),
                                                 id=str(uuid.uuid4()))

                # Upload point to db
                self.qdrant.upload_point(point=point)
