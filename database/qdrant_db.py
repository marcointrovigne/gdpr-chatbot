import os
from typing import Literal

from fastembed import SparseTextEmbedding
from loguru import logger
from openai import OpenAI
from qdrant_client import QdrantClient, models
from qdrant_client.conversions.common_types import ScoredPoint, SparseVector


class Qdrant:
    """
    A class for managing regulatory content in Qdrant vector database with hybrid search capabilities.

    This class handles vector embeddings and search operations for GDPR articles and related
    content, using both dense (OpenAI) and sparse (BM25) embeddings for optimal retrieval.

    Attributes:
        client (QdrantClient): Qdrant client instance
        model (OpenAI): OpenAI client for embeddings
        bm25 (SparseTextEmbedding): BM25 embedding model
        collection_name (str): Name of the Qdrant collection
        model_name (str): OpenAI embedding model identifier
        size (int): Dimension size of embeddings
    """

    def __init__(self):
        """Initialize Qdrant connection and embedding models."""
        self.client = QdrantClient(url=os.getenv("QDRANT_URL"),
                                   api_key=os.getenv("QDRANT_API_KEY"))
        self.model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bm25 = SparseTextEmbedding(model_name="Qdrant/bm25")
        self.collection_name = "privasee-gdpr"
        self.model_name = "text-embedding-3-large"
        self.size = 3072

    def create_collection(self,
                          force_delete: bool = False) -> None:
        """
        Create or recreate the Qdrant collection for regulatory content.

        Sets up a collection with both dense and sparse vector configurations
        for hybrid search capabilities.

        Args:
            force_delete (bool): If True, deletes existing collection before creation

        Raises:
            Exception: If collection exists and force_delete is False
        """

        logger.info(f"Creating Qdrant collection {self.collection_name}")

        try:
            if self.client.collection_exists(collection_name=self.collection_name):
                if force_delete:
                    logger.warning(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(collection_name=self.collection_name)
                    logger.info(f"Collection {self.collection_name} deleted")
                else:
                    raise Exception(f"Collection {self.collection_name} already exists")

            # Configure vector spaces for hybrid search
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "text-embedding-3-large-dot": models.VectorParams(size=self.size, distance=models.Distance.DOT),
                    "text-embedding-3-large-cosine": models.VectorParams(size=self.size,
                                                                         distance=models.Distance.COSINE),
                },
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams(),
                }
            )

            logger.info(f"Collection created successfully: {self.collection_name}")
        except Exception as e:
            logger.error(f"Collection creation failed: {str(e)}")
            raise

    def create_point(self,
                     bm25_text: str,
                     embed_text: str,
                     payload: dict,
                     id: str) -> models.PointStruct:
        """
        Create a point with hybrid embeddings for regulatory content.

        Generates both dense and sparse embeddings for the provided text
        and combines them into a single point structure.

        Args:
            bm25_text (str): Text for BM25 sparse embedding
            embed_text (str): Text for dense embedding
            payload (dict): Additional metadata for the point
            id (str): Unique identifier for the point

        Returns:
            models.PointStruct: Point structure with embeddings
        """
        logger.info("Creating point")

        # BM25 Embedding
        em_bm = self.embed_bm25(text=bm25_text)

        # OpenAI Embedding
        text_embed = self.create_openai_embedding(text=embed_text)

        point = models.PointStruct(
            id=id,
            payload=payload,
            vector={
                "bm25": models.SparseVector(
                    indices=em_bm.indices,
                    values=em_bm.values,
                ),
                "text-embedding-3-large-cosine": text_embed,
                "text-embedding-3-large-dot": text_embed
            }
        )
        logger.info(f"Point {id} created successfully")
        return point

    def create_openai_embedding(self,
                                text: str) -> list[float]:
        """
       Create dense embeddings using OpenAI's embedding model.

       Generates vector embeddings for regulatory text using OpenAI's
       text embedding model, optimized for semantic search operations.

       Args:
           text (str): Regulatory text to embed

       Returns:
           List[float]: Dense vector embedding
       """
        logger.info("Creating OpenAI embedding")
        em = self.model.embeddings.create(input=text,
                                          model=self.model_name).data[0].embedding
        logger.info(f"Embedding of text: ({text}) created")
        return em

    def embed_bm25(self,
                   text: str) -> SparseVector:
        """
        Create sparse BM25 embeddings for text.

        Generates sparse vector representations using BM25 algorithm,
        which is particularly effective for keyword-based search in
        regulatory content.

        Args:
            text (str): Regulatory text to embed

        Returns:
            SparseVector: Sparse vector representation with indices and values
        """
        logger.info("Creating BM25 embedding")
        em = list(self.bm25.embed(documents=text))
        sparse_vector = SparseVector(indices=em[0].indices.tolist(), values=em[0].values.tolist())
        logger.info(f"BM25 embedding of text: ({text}) created")
        return sparse_vector

    def upload_point(self,
                     point: models.PointStruct) -> None:
        """
        Upload a single point to the Qdrant collection.

        Uploads a point containing regulatory content embeddings and
        metadata to the vector database.

        Args:
            point (models.PointStruct): Point containing embeddings and payload
        """
        self.client.upload_points(
            collection_name=self.collection_name,
            points=[
                point
            ],
        )
        logger.info(f"Point {point.id} correctly uploaded")

    def hybrid_search(self,
                      query: str,
                      article: int,
                      category: str,
                      distance: Literal["dot", "cosine"] = "dot",
                      top_k: int = 4) -> list[ScoredPoint]:
        """
        Perform hybrid search combining dense and sparse embeddings.

        Uses both BM25 and neural embeddings to search for regulatory content,
        combining results using Reciprocal Rank Fusion (RRF).

        Args:
            query (str): Search query text
            article (int): Article identifier to filter results
            category (str): Category identifier to filter results
            distance (Literal["dot", "cosine"]): Distance metric for dense embeddings
            top_k (int): Number of results to return

        Returns:
            List[ScoredPoint]: Ranked list of search results

        Raises:
            NotImplementedError: If invalid distance metric is specified
        """
        logger.info("Performing hybrid search")

        # Select embedding model based on distance metric
        if distance == "dot":
            embedding_model = "text-embedding-3-large-dot"
        elif distance == "cosine":
            embedding_model = "text-embedding-3-large-cosine"
        else:
            raise NotImplementedError

        # Generate embeddings for query
        bm25_embed = self.embed_bm25(text=query)
        openai_embed = self.create_openai_embedding(text=query)

        # Perform hybrid search
        scored_points = self.client.query_points(
            collection_name=self.collection_name,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="article_num",
                        match=models.MatchValue(value=article),
                    ),
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(
                            value=category,
                        ),
                    )
                ]
            ),
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(indices=bm25_embed.indices, values=bm25_embed.values),
                    using="bm25",
                    limit=8,
                ),
                models.Prefetch(
                    query=openai_embed,
                    using=embedding_model,
                    limit=8,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=top_k
        )
        return scored_points
