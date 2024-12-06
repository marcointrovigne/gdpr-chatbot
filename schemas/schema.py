from typing import Literal

from pydantic import BaseModel, Field


class ClauseModel(BaseModel):
    """
    A model representing a legal clause within a sub-article.

    Attributes:
        title (str): The title or heading of the clause
        content (str): The main text content of the clause
    """
    title: str = Field(
        description="The title or heading of the clause"
    )
    content: str = Field(
        description="The main text content of the clause"
    )


class SubArticlesModel(BaseModel):
    """
    A model representing a sub-article within the main article.

    Attributes:
        title (str): The title of the sub-article
        number (int): The numerical identifier of the sub-article
        content (str): The main text content of the sub-article
        clause (List[ClauseModel]): A list of clauses contained within the sub-article
    """
    title: str = Field(
        description="The title of the sub-article"
    )
    number: int = Field(
        description="The numerical identifier of the sub-article"
    )
    content: str = Field(
        description="The main text content of the sub-article"
    )
    clause: list[ClauseModel] = Field(
        description="List of clauses contained within the sub-article"
    )


class RecitalsContent(BaseModel):
    """
    A model representing the content of a recital.

    Attributes:
        number (int): The numerical identifier of the recital
        content (str): The text content of the recital
    """
    number: int = Field(
        description="The numerical identifier of the recital"
    )
    content: str = Field(
        description="The text content of the recital"
    )


class ArticleModel(BaseModel):
    """
    A model representing a main article in the regulation.

    Attributes:
        title (str): The title of the article
        article_num (int): The numerical identifier of the article
        articles (List[SubArticlesModel]): A list of sub-articles contained within the main article
    """
    title: str = Field(
        description="The title of the article"
    )
    article_num: int = Field(
        description="The numerical identifier of the article"
    )
    articles: list[SubArticlesModel] = Field(
        description="List of sub-articles contained within the main article"
    )


class RecitalsModel(BaseModel):
    """
    A model representing the recitals section of the regulation.

    Attributes:
        recitals (List[RecitalsContent]): A list of recital contents
    """
    recitals: list[RecitalsContent] = Field(
        description="List of recital contents in the regulation"
    )


class CommentaryGuidelinesModel(BaseModel):
    """
    A model representing expert commentary and guidelines for the regulation.

    Attributes:
        expert_commentary (str): Expert analysis and interpretation of the regulation
        guidelines_case_law (str): Related guidelines and case law references
    """
    expert_commentary: str = Field(
        description="Expert analysis and interpretation of the regulation"
    )
    guidelines_case_law: str = Field(
        description="Related guidelines and case law references"
    )


class RegulationModel(ArticleModel, RecitalsModel, CommentaryGuidelinesModel):
    """
    A comprehensive model that combines articles, recitals, and commentary for a complete regulation.

    This model inherits from:
        - ArticleModel: For managing article content
        - RecitalsModel: For managing recitals
        - CommentaryGuidelinesModel: For managing expert commentary and guidelines
    """
    pass


class QdrantDocument(BaseModel):
    """
        A model representing a document for vector storage in Qdrant.

        Attributes:
            embed_text (str): Text prepared for embedding
            article_num (int): The numerical identifier of the article
            article_summary (str): A summary of the article
            content (str): The full content of the document
            category (str): The category of the document
        """
    embed_text: str = Field(
        description="Text prepared for embedding"
    )
    article_num: int = Field(
        description="The numerical identifier of the article"
    )
    article_summary: str = Field(
        description="A summary of the article content"
    )
    content: str = Field(
        description="The full content of the document"
    )
    category: Literal["article", "recital"] = Field(
        description="The category of the article"
    )
