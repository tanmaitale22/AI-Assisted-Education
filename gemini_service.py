import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def ask_gemini(question, context):

    prompt = f"""
You are an AI educational assistant.

Use the provided study material to answer the student's question.

STUDY MATERIAL:
{context}

STUDENT QUESTION:
{question}

Give a clear and easy-to-understand explanation.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text