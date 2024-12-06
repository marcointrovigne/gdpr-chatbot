from database.qdrant_db import Qdrant
from schemas.llm import MessageSchema, ReformulatedQuestion


def convert_chat_history(chat_history: list[MessageSchema]) -> list[dict[str, str]]:
    result = []

    for message in chat_history:
        result.append({
            "role": message.sender,
            "content": message.message,
        })
    return result


def str_format_chat_history(chat_history: list[MessageSchema]) -> str:
    result = ""
    for message in chat_history:
        result += f"{message.sender}: {message.message}\n"
    return result


def get_context(reformulated: ReformulatedQuestion) -> str:
    q = Qdrant()

    out = ""
    articles_1 = q.hybrid_search(query=reformulated.reformulated,
                                 article=reformulated.article[0],
                                 category="article",
                                 top_k=3)
    recitals_1 = q.hybrid_search(query=reformulated.reformulated,
                                 article=reformulated.article[0],
                                 category="recital",
                                 top_k=1)
    if articles_1.points:
        out += f"---{articles_1.points[0].payload.get('article_summary')}---\n"
        for article in articles_1.points:
            out += f"{article.payload.get('content')}\n\n"
        for recital in recitals_1.points:
            out += f"{recital.payload.get('content')}\n\n"

    if len(reformulated.article) > 1:
        for i in range(1, len(reformulated.article)):
            secondary_articles = q.hybrid_search(query=reformulated.reformulated,
                                                 article=reformulated.article[i],
                                                 category="article",
                                                 top_k=1)

            if secondary_articles.points:
                out += f"---{secondary_articles.points[0].payload.get('article_summary')}---\n"
                for article in secondary_articles.points:
                    out += f"{article.payload.get('content')}\n\n"
    return out
