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

<gdpr_summary>
1. **Article 1 - Subject-matter and objectives**: This article outlines the GDPR's purpose, which is to protect individuals' rights regarding their personal data and to regulate the processing of such data.
2. **Article 2 - Material scope**: Specifies the data processing activities that fall under the GDPR, including processing in the context of EU member states' activities, regardless of whether the processing occurs in the EU or not.
3. **Article 3 - Territorial scope**: Defines the geographical scope of the GDPR, applying to organizations based in the EU and those outside the EU that offer goods or services to, or monitor the behavior of, EU data subjects.
4. **Article 4 - Definitions**: Provides definitions for key terms used in the regulation, such as 'personal data', 'processing', 'controller', and 'processor'.
5. **Article 5 - Principles relating to processing of personal data**: Lists the core principles for processing personal data, including lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity, and confidentiality.
6. **Article 6 - Lawfulness of processing**: Specifies the lawful bases for processing personal data, such as consent, contract necessity, legal obligation, vital interests, public task, and legitimate interests.
7. **Article 7 - Conditions for consent**: Details the conditions for obtaining valid consent from data subjects, emphasizing that consent must be freely given, specific, informed, and unambiguous.
8. **Article 8 - Conditions applicable to child's consent in relation to information society services**: Sets the age of consent for data processing related to information society services at 16, with the possibility for member states to lower it to no less than 13 years.
9. **Article 9 - Processing of special categories of personal data**: Prohibits processing of sensitive data (e.g., racial or ethnic origin, political opinions, religious beliefs) unless specific conditions are met, such as explicit consent or necessity for certain legal purposes.
10. **Article 10 - Processing of personal data relating to criminal convictions and offences**: States that processing personal data related to criminal convictions and offences requires a legal basis under EU or member state law.
11. **Article 11 - Processing which does not require identification**: Covers processing of data that doesn't require the identification of a data subject, setting limitations and obligations for controllers in such cases.
12. **Article 12 - Transparent information, communication and modalities for the exercise of the rights of the data subject**: Obligates controllers to provide information about data processing in a concise, transparent, and easily accessible form.
13. **Article 13 - Information to be provided where personal data are collected from the data subject**: Details the information that must be provided to data subjects when their data is collected directly, including the purpose of processing and the data retention period.
14. **Article 14 - Information to be provided where personal data have not been obtained from the data subject**: Specifies the information to be provided when data is not obtained directly from the data subject, including the source of the data.
15. **Article 15 - Right of access by the data subject**: Grants data subjects the right to access their personal data and obtain copies of it, along with other details about how and why their data is processed.
16. **Article 16 - Right to rectification**: Gives data subjects the right to have inaccurate personal data corrected and incomplete data completed.
17. **Article 17 - Right to erasure ('right to be forgotten')**: Allows data subjects to have their personal data erased under certain conditions, such as when the data is no longer necessary for its original purpose.
18. **Article 18 - Right to restriction of processing**: Provides data subjects the right to restrict processing of their data under certain circumstances, such as when the accuracy of the data is contested.
19. **Article 19 - Notification obligation regarding rectification or erasure of personal data or restriction of processing**: Requires controllers to notify all recipients of the data about any rectification, erasure, or restriction of processing, unless this proves impossible or involves disproportionate effort.
20. **Article 20 - Right to data portability**: Grants data subjects the right to receive their personal data in a structured, commonly used, and machine-readable format, and to transfer that data to another controller.
21. **Article 21 - Right to object**: Gives data subjects the right to object to the processing of their personal data based on certain grounds, including processing for direct marketing, research, or based on a public or legitimate interest.
</gdpr_summary>

As a GDPR expert, please:
1. Reformulate my question to be more precise and relevant. Do not add details that are not present in the chat history
2. Identify the most applicable GDPR articles related to this topic, cannot put more then 3 main articles (must be from 1 to 21 since there are 21 total articles)
3. Include ONLY relevant articles numbers related to this topic
4. Order the articles by importance order

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
