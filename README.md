# GDPR Articles RAG System

Retrieval-Augmented Generation (RAG) system designed to process and answer queries about GDPR Articles 1-21. This system combines advanced document processing, vectorization, and natural language understanding to provide accurate, context-aware responses to GDPR-related questions.

## System Architecture

The system implements a multi-stage approach to process and retrieve GDPR information:

1. **Document Processing Pipeline**
   - PDF extraction and article separation
   - Structured data creation using LLM analysis
   - Document vectorization using hybrid search (BM25 + OpenAI embeddings)

2. **Query Processing System**
   - Question reformulation and article selection
   - Contextual retrieval using hybrid search
   - Response generation with context-aware LLM

## Project Structure

```
.
├── README.md
├── database
│   └── qdrant_db.py              # Qdrant database interface
├── dataset
│   ├── GDPR_Art_1-21.pdf        # Source PDF
│   ├── raw_articles/            # Extracted markdown files
│   └── structured_output/       # Processed JSON files
├── main.py                      # Main chat interface
├── prompts
│   └── prompts.py              # LLM prompt templates
├── schemas
│   ├── llm.py                  # LLM-related schemas
│   └── schema.py               # Data model schemas
├── scripts
│   ├── embeddings_dataset.py   # Dataset-based embedding generation
│   └── embeddings_pdf.py       # PDF-based embedding generation
└── tools
    ├── agents.py               # LLM interaction handlers
    ├── embedding.py            # Embedding creation utilities
    ├── pdf_extractor.py        # PDF processing tools
    └── tools.py                # Utility functions
```

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- Poetry for dependency management
- Qdrant vector database
- OpenAI API access
- Anthropic API access

### Environment Configuration
Create a `.env` file in the root directory with the following credentials:
```
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Installation Steps
1. Install Poetry if not already installed:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install project dependencies:
   ```bash
   poetry install
   ```

## Creating Embeddings

You have two options for creating embeddings:

### Option 1: Generate from PDF (Full Process)
```bash
python scripts/embeddings_pdf.py
```
This will:
- Extract content from the PDF
- Split into individual articles
- Create structured JSON output
- Generate embeddings for all content

### Option 2: Generate from Existing Dataset
```bash
python scripts/embeddings_dataset.py
```
This uses pre-split articles and structured JSON files to create embeddings.

## Usage

Start the interactive chat interface:
```bash
python main.py
```

You can then ask questions about GDPR articles directly in the terminal.

## Technical Implementation Details

### System Architecture

The system consists of four main components: data modeling, document processing, search functionality, and a chat interface. Each component is designed to handle specific aspects of GDPR content processing and retrieval.

### Data Models

I implemented two primary data models to handle different aspects of the system:

The RegulationModel serves as the core data structure for GDPR content. It maintains the hierarchical organization of articles, including sub-articles, recitals, and expert commentary. This model ensures that complex relationships between GDPR components are preserved and accessible.

The QdrantDocument model acts as an interface layer for search operations. It contains fields essential for vector search: embedded text, article identifiers, summaries, and content categorization. This model optimizes the storage and retrieval of GDPR content in the vector database.

### Document Processing Pipeline

Converting the GDPR PDF into structured data required a sophisticated multi-phase approach. The process begins with document analysis to identify structural patterns and markers for accurate segmentation. Using these markers, I developed an extraction algorithm that divides the document into 21 distinct articles, each preserved as a markdown file.

The key innovation in this phase is a three-stage LLM processing pipeline that converts unstructured text into precisely formatted data. This approach was necessary due to the diverse types of information contained within GDPR articles. Here's how it works:

1. The first LLM call focuses on article structure, identifying and organizing main content, sub-articles, and their associated clauses.
2. The second LLM call processes recitals, which provide crucial interpretative context.
3. The third LLM call extracts expert commentary and implementation guidelines.

To optimize this process, I implemented prompt caching to reduce token usage and API costs. This is particularly important given the multiple LLM calls required for each article.

### Search System Implementation

The search system's architecture reflects findings from research into legal document retrieval. I discovered that sub-articles contain the most specific and actionable information, while recitals provide essential context. Based on this, I made a strategic decision to exclude expert guidelines and commentary from the search index, focusing solely on primary regulatory content.

I developed a hybrid search approach combining two indexing methods:

For recitals, I implemented dual indexing:
- BM25 sparse vector representation for precise keyword matching
- Dense embeddings using OpenAI's `text-embedding-3-large` for semantic understanding

For sub-articles, which require more sophisticated processing due to their importance, I implemented contextual retrieval. This involves processing each sub-article within its parent article's context. The enriched text then undergoes the same dual indexing process, creating a search space that captures both local and broader article context.

### Chat System Implementation

The chat interface operates through a sophisticated two-phase process designed to maximize accuracy and relevance.

Phase One: Query Processing
- Process the complete conversation history through an LLM
- Generate a reformulated question optimized for vector search
- Identify 1-3 most relevant GDPR articles

Phase Two: Retrieval and Response
- Implement hybrid search to Qdrant using the reformulated question as query
- For primary article: retrieve two most similar sub-articles and one related recital
- For secondary articles: retrieve single most relevant sub-article
- Process retrieved context and conversation history through final LLM prompt

This implementation ensures responses maintain legal precision while remaining relevant to user queries. The system balances comprehensive coverage of topics with focused, actionable information.

### Optimization Techniques

Throughout the system, I've implemented several optimization strategies:

Performance Optimization:
- Prompt caching for efficient token usage
- Selective embedding focusing on critical content
- Dual-vector space for enhanced search accuracy

Quality Optimization:
- Contextual enrichment of sub-articles
- Hierarchical relevance ordering
- Conversation-aware response generation

The combination of these techniques ensures the system provides accurate, contextually appropriate responses while maintaining efficient resource usage.
