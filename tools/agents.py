import json
from typing import Literal, Type, Union

import anthropic
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from loguru import logger
from pydantic import BaseModel

from prompts.prompts import (RETRY_PROMPT, JSON_COMMENTARY_GUIDELINES_EXTRACTOR,
                             JSON_ARTICLES_EXTRACTOR, JSON_RECITALS_EXTRACTOR, ARTICLE_CONTENT, CHUNK_CONTEXT_PROMPT,
                             REFORMULATED_QUESTION, MAIN_CHAT)
from schemas.llm import MessageSchema, ReformulatedQuestion
from schemas.schema import ArticleModel, CommentaryGuidelinesModel, RecitalsModel
from tools.tools import str_format_chat_history, convert_chat_history

load_dotenv()

# Type alias for regulatory model outputs
RegulatoryModel = Union[ArticleModel, CommentaryGuidelinesModel, RecitalsModel]


def agent_article(article_name: str,
                  article_content: str,
                  scope: Literal["article", "commentary", "recitals"]) -> RegulatoryModel:
    """
    Process GDPR articles using specialized LLM calling.

    This function analyzes GDPR articles using a Large Language Model to extract
    structured information based on the specified scope (article content, commentary,
    or recitals).

    Args:
        article_name (str): Identifier of the article (e.g., "article_5")
        article_content (str): Raw content of the article to be analyzed
        scope (Literal["article", "commentary", "recitals"]): Analysis scope to apply
            - "article": Extracts article structure and content
            - "commentary": Extracts expert commentary and guidelines
            - "recitals": Extracts related recitals

    Returns:
        Union[ArticleModel, CommentaryGuidelinesModel, RecitalsModel]:
            Structured output based on the specified scope
    """
    logger.info(f"Starting GDPR-LLM for {article_name} with scope: {scope}")

    # Select appropriate template and model based on scope
    if scope == "article":
        template = JSON_ARTICLES_EXTRACTOR
        pydantic_mod = ArticleModel
    elif scope == "commentary":
        template = JSON_COMMENTARY_GUIDELINES_EXTRACTOR
        pydantic_mod = CommentaryGuidelinesModel
    elif scope == "recitals":
        template = JSON_RECITALS_EXTRACTOR
        pydantic_mod = RecitalsModel
    else:
        raise NotImplementedError(f"Scope {scope} not implemented")

    # Initialize Anthropic client
    client = anthropic.Anthropic()

    # Using Pydantic output parser for sake of simplicity to get format instructions
    parser = PydanticOutputParser(pydantic_object=pydantic_mod)

    # Prompt as string is necessary for the retry option
    article_prompt = ARTICLE_CONTENT.format(article_content=article_content)
    text_prompt = template.format(article_name=article_name, format_instructions=parser.get_format_instructions())
    prompt_as_string = article_prompt + text_prompt

    logger.info(f"Invoking LLM for {article_name} with scope: {scope}")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        system="You are a specialized GDPR Article Analysis Expert.",
        messages=[
            {"role": "user",
             "content": [
                 {
                     "type": "text",
                     "text": article_prompt,
                     "cache_control": {"type": "ephemeral"}
                 },
                 {
                     "type": "text",
                     "text": text_prompt,
                 },
             ]
             }
        ],
        # Implementing cache
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )

    raw_response = response.content[0].text
    logger.info("Received raw LLM response")

    # Parse response into appropriate model
    try:
        logger.info("Parsing LLM output")
        response = pydantic_mod(**json.loads(raw_response))
    except Exception as e:
        logger.warning(f"Initial parsing failed for {article_name}-{scope}, attempting retry")
        response = retry_agent(exception=e,
                               original_prompt=prompt_as_string,
                               output=raw_response,
                               pydantic_mod=pydantic_mod)
    logger.info(f"Correctly build structured output for {article_name} for {scope}")
    return response


def contextual_embedding_agent(chunk_content: str,
                               article_content: str) -> str:
    """
    Generate contextual embeddings for GDPR article chunks.

    This function creates context-aware embeddings by analyzing article chunks
    within the broader context of their parent articles.

    Args:
        chunk_content (str): Content of the specific article chunk
        article_content (str): Full content of the parent article

    Returns:
        str: Contextual embedding text for the chunk
    """
    logger.info("Generating contextual embedding")

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[
            {"role": "user",
             "content": [
                 {
                     "type": "text",
                     "text": ARTICLE_CONTENT.format(article_content=article_content),
                     "cache_control": {"type": "ephemeral"}
                 },
                 {
                     "type": "text",
                     "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk_content),
                 },
             ]
             }
        ],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    logger.info("Successfully generated contextual embedding")
    return response.content[0].text


def retry_agent(exception: Exception,
                original_prompt: str,
                output: str,
                pydantic_mod: Type[BaseModel]) -> RegulatoryModel:
    """
    Retry failed GDPR analysis attempts with error correction.

    This function handles cases where the initial analysis fails, attempting
    to correct the output format based on the error information.

    Args:
        exception (Exception): The original parsing error
        original_prompt (str): The prompt that caused the error
        output (str): The problematic output to be corrected
        pydantic_mod (Type[BaseModel]): The expected output model type

    Returns:
        Union[ArticleModel, CommentaryGuidelinesModel, RecitalsModel]:
            Corrected structured output

    Raises:
        Exception: If retry attempt fails
    """
    logger.info("Initiating retry for failed analysis")
    client = anthropic.Anthropic()

    # Creating parser for instructions output
    parser = PydanticOutputParser(pydantic_object=pydantic_mod)
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            system="You are a specialized GDPR Article Analysis Expert.",
            messages=[
                {"role": "user",
                 "content": RETRY_PROMPT.format(exception=str(exception),
                                                original_prompt=original_prompt,
                                                output=output,
                                                format_instructions=parser.get_format_instructions())}
            ],
        )
        raw_response = response.content[0].text

        response = pydantic_mod(**json.loads(raw_response))
        logger.info("Successfully corrected output on retry")
        return response

    except Exception as e:
        logger.error(f"Retry attempt failed: {str(e)}", exc_info=True)
        raise


def extract_article(chat_history: list[MessageSchema],
                    model: str = "claude-3-5-sonnet-20241022"):
    """
    Analyzes chat history to identify and extract relevant GDPR article references using Claude 3.5 Sonnet.

    This function processes the chat history through a specialized GDPR Article Analysis system,
    reformulating the discussion into a structured format that identifies specific GDPR articles
    and their relevance to the conversation.

    Parameters:
        chat_history (list[MessageSchema]): A list of message objects representing the
            conversation history. Each message follows the MessageSchema format.
        model (str): The model type to use for extracting relevant GDPR articles

    Returns:
        ReformulatedQuestion: A structured object containing the reformulated question
            and relevant GDPR article references.
    """
    client = anthropic.Anthropic()
    parser = PydanticOutputParser(pydantic_object=ReformulatedQuestion)

    text_prompt = REFORMULATED_QUESTION.format(chat_history=str_format_chat_history(chat_history),
                                               format_instructions=parser.get_format_instructions())
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are a specialized GDPR Article Analysis Expert.",
        messages=[{"role": "user",
                   "content": text_prompt}],
    )
    raw_response = response.content[0].text
    try:
        response = ReformulatedQuestion(**json.loads(raw_response))
    except Exception as e:
        response = retry_agent(exception=e,
                               original_prompt=text_prompt,
                               output=raw_response,
                               pydantic_mod=ReformulatedQuestion)
    return response


def main_chat(chat_history: list[MessageSchema],
              context: str,
              model: str = "claude-3-5-sonnet-20241022"):
    """
    Processes a GDPR-related conversation.

    This function manages an interactive conversation about GDPR topics, leveraging
    a pre-configured expert system with comprehensive knowledge of GDPR articles
    and regulations. It maintains conversation context and provides detailed,
    expert-level responses.

    Parameters:
        chat_history (list[MessageSchema]): A list of previous messages in the conversation,
            following the MessageSchema format.
        context (str): Additional contextual information relevant to the current
            conversation retrieved from VectorDB.
        model (str): The model type to use for extracting relevant GDPR articles

    Returns:
        str: The expert system's response to the current conversation state,
            incorporating both the chat history and provided context.
    """
    client = anthropic.Anthropic()
    messages = convert_chat_history(chat_history=chat_history)
    messages.append({"role": "user",
                     "content": MAIN_CHAT.format(context=context)})
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are an expert in GDPR with 15+ years of experience. You know all the articles by memory and you can answer all the people questions on GDPR.",
        messages=messages
    )
    return response.content[0].text
