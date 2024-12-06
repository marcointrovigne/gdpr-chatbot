import sys

from loguru import logger

from schemas.llm import MessageSchema, SenderType
from tools.agents import extract_article, main_chat
from tools.tools import get_context

logger.remove()
logger.add(sink=sys.stderr, level="WARNING")


def main():
    conversation_history: list[MessageSchema] = []
    try:
        while True:
            message = input("Write your message (or 'quit' to exit): ").strip()
            if message.lower() == "quit":
                print("Goodbye! Have a great day!")
                break

            if not message:
                print("Please enter a valid message.")
                continue

            # Add new message to conversation history
            conversation_history.append(MessageSchema(sender=SenderType.USER, message=message))

            # Preprocess the message
            reformulated = extract_article(chat_history=conversation_history, model="claude-3-5-sonnet-20241022")

            # Get context from embeddings
            context = get_context(reformulated=reformulated)

            # Final answer
            output = main_chat(chat_history=conversation_history, context=context, model="claude-3-5-sonnet-20241022")

            # Update conversation history
            conversation_history.append(MessageSchema(sender=SenderType.ASSISTANT, message=message))

            # Print the response
            print(output)

    except KeyboardInterrupt:
        print("\nSession terminated by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
