import os
import re
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
groq_api_key = os.getenv("GROQ_API_KEY")


def set_llm_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that generates dark jokes. Don't continue the conversation, just generate a joke."),
        ("user", "generate a joke on the topic: {topic}")
    ])

    llm = ChatGroq(
        model="Gemma2-9b-It",
        groq_api_key=groq_api_key
    )

    return prompt | llm | StrOutputParser()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Mention me with a topic like 'JOKEONLYBOT technology' to get a dark joke."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Help! Mention me with a topic like 'JOKEONLYBOT death' to get some dark humor."
    )


async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    await update.message.reply_text(f"Generating a joke... about {topic}")
    chain = set_llm_chain()
    joke = await asyncio.to_thread(chain.invoke, {"topic": topic})  # Non-blocking
    await update.message.reply_text(joke.strip())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    message_upper = message.upper()

    if message_upper.startswith("JOKEONLYBOT"):
        parts = message.split(maxsplit=1)
        if len(parts) > 1:
            topic = parts[1]
            await generate_joke(update, context, topic)
        else:
            await update.message.reply_text("Please include a topic after 'JOKEONLYBOT'.")
    else:
        await update.message.reply_text("Mention me like 'JOKEONLYBOT death' to get a joke.")



def main():
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        raise ValueError("TELEGRAM_API_KEY not set in environment variables.")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


