# import os

# from dotenv import load_dotenv
# from google import genai


# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

# client = genai.Client(api_key=api_key)


# def ask_gemini(question, context):

#     prompt = f"""
#     You are an AI educational assistant.

#     Use the provided study material to answer the student's question.

#     STUDY MATERIAL:
#     {context}

#     STUDENT QUESTION:
#     {question}

#     Give a clear and easy-to-understand explanation.
#     """

#     response = client.models.generate_content(
#         model="gemini-3.6-flash",
#         contents=prompt
#     )

#     return response.text

import os

from dotenv import load_dotenv
from google import genai
from openai import OpenAI


load_dotenv()


# ---------------- GEMINI ----------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(
    api_key=gemini_api_key
)


# ---------------- DEEPSEEK ----------------

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

deepseek_client = OpenAI(
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com"
)


# ---------------- GEMINI ----------------

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

    response = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ---------------- DEEPSEEK FALLBACK ----------------

def ask_deepseek(question, context):

    prompt = f"""
    You are an AI educational assistant.

    Use the provided study material to answer the student's question.

    STUDY MATERIAL:
    {context}

    STUDENT QUESTION:
    {question}

    Give a clear and easy-to-understand explanation.
    """

    response = deepseek_client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ---------------- MAIN FUNCTION ----------------

def ask_ai(question, context):

    try:
        print("Trying Gemini...")

        return ask_gemini(question, context)

    except Exception as e:

        error_message = str(e)

        # Only fallback for Gemini availability/high-demand errors
        if "503" in error_message or "UNAVAILABLE" in error_message:
            print("Gemini unavailable. Switching to DeepSeek...")

            return ask_deepseek(question, context)

        # Other errors should still be visible
        raise