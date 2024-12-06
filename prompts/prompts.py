RETRY_PROMPT = """
This is the original prompt:
<original_prompt>
{original_prompt}
</original_prompt>

And produced the following output:
<output_prompt>
{output}
</output_prompt>

With the following exception:
<exception>
{exception}
</exception>

Please make sure you output the correct structure using this output format and do not include additional notes.
{format_instructions}
"""

ARTICLE_CONTENT = """
<article_content>
{article_content}
</article_content>
"""

JSON_COMMENTARY_GUIDELINES_EXTRACTOR = """
The document you are analyzing is the {article_name} of the GDPR regulations.
Your task is to analyze and structure the provided article in a precise JSON format while maintaining complete fidelity to the original text.
You need to focus ONLY on extraction all the articles and clauses.

Your analysis must be structured in the following JSON format:
{format_instructions}

<example>
{{
  "expert_commentary": "Empty string if not present",
  "guidelines_case_law": "Empty string if not present"
}}
</example>

<important>
1. Never summarize, paraphrase, or modify the original content
2. Follow the exact JSON format provided
3. Even if a section is empty, include it with an empty string
4. Ensure the output is valid JSON format convertible with json.loads() in python and include all the parameters
5. No analytical content or commentary has been added, NEVER
6. Never split the JSON into two parts
</important>

BE SURE THAT YOU HAVE INCLUDED ALL THE EXPERT COMMENTARY AND GUIDELINES CASE LAW

Make sure you are not inventing information
Process the article content and return it in the specified JSON format. Focus exclusively on accurate structural representation without adding any analysis or interpretation.
If you do your job great and respect the rules you will get tons of money.
If the output is not complete or not convertible with json.loads() you will get fired.
"""

JSON_ARTICLES_EXTRACTOR = """
The document you are analyzing is the {article_name} of the GDPR regulations.
Your task is to analyze and structure the provided article in a precise JSON format while maintaining complete fidelity to the original text.
You need to focus ONLY on extraction all the articles and clauses.

Your analysis must be structured in the following JSON format:
{format_instructions}

<example>
{{
  "title": "Main article title",
  "article_num": 1,
  "articles": [
    {{
      "title": "Title of sub articles",
      "number": 1,
      "content": "Content of the article",
      "clause": [
        {{
          "title": "a) Clause title",
          "content": "Content of the clause"
        }}
      ]
    }}
  ]
}}
</example>

<important>
1. Never summarize, paraphrase, or modify the original content
2. Follow the exact JSON format provided
3. Even if a section is empty, include it with an empty string
4. Ensure the output is valid JSON format convertible with json.loads() in python and include all the parameters
5. No analytical content or commentary has been added, NEVER
6. Never split the JSON into two parts
</important>

BE SURE THAT YOU HAVE INCLUDED ALL THE ARTICLES AND CLAUSES

Make sure you are not inventing articles or clauses
Process the article content and return it in the specified JSON format. Focus exclusively on accurate structural representation without adding any analysis or interpretation.
If you do your job great and respect the rules you will get tons of money.
If the output is not complete or not convertible with json.loads() you will get fired.
"""

JSON_RECITALS_EXTRACTOR = """
The document you are analyzing is the {article_name} of the GDPR regulations.
Your task is to analyze and structure the provided article in a precise JSON format while maintaining complete fidelity to the original text.
You need to focus ONLY on extraction all the recitals.

Your analysis must be structured in the following JSON format:
{format_instructions}

<example>
{{
  "recitals": [
    {{
      "number": 97,
      "content": "Content of the recitals"
    }}
  ]
}}
</example>

<important>
1. Never summarize, paraphrase, or modify the original content
2. Follow the exact JSON format provided
3. Even if a section is empty, include it with an empty string
4. Ensure the output is valid JSON format convertible with json.loads() in python and include all the parameters
5. No analytical content or commentary has been added, NEVER
6. Never split the JSON into two parts
</important>

BE SURE THAT YOU HAVE INCLUDED ALL THE RECITALS

Make sure you are not inventing recitals
Process the article content and return it in the specified JSON format. Focus exclusively on accurate structural representation without adding any analysis or interpretation.
If you do your job great and respect the rules you will get tons of money.
If the output is not complete or not convertible with json.loads() you will get fired.
"""

CHUNK_CONTEXT_PROMPT = """
Here is the chunk we want to situate within the whole document
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
"""

REFORMULATED_QUESTION = """
Please analyze this conversation and help me improve my GDPR-related question based on the dialogue history:

<conversation>
{chat_history}
</conversation>

As a GDPR expert, please:
1. Reformulate my question to be more precise and relevant. Do not add details that are not present in the chat history
2. Identify the most applicable GDPR articles related to this topic, cannot put more then 3 articles
3. Order the articles by importance order
4. The number must be from 1 to 21

Please provide your response in this JSON format:
{{
    "reformulated_question": "Your improved version of my question",
    "relevant_articles": [article_number1, article_number2]
}}

<output_format>
{format_instructions}
</output_format>

Your reformulated question is very important to retrieve the correct information with vector search.
Note: Please ensure the response is valid JSON that can be parsed with json.loads().
NEVER INCLUDE ADDITIONAL NOTES, STICK TO THE RULES
"""

MAIN_CHAT = """
You are providing expert guidance on GDPR compliance, drawing from deep knowledge of all GDPR articles and their practical applications.

Reference Material:
<context>
{context}
</context>

Please provide a focused, concise response that:
- Directly answers the question in 2-3 paragraphs maximum
- References key GDPR requirements
- Provides clear, actionable guidance
- Maintains accuracy without speculation

Keep your response brief while ensuring all essential information is included.
"""
