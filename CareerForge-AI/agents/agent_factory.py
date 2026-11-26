
import json
import os
from groq import Groq

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


def run_agent(
    provider: str,
    instructions: str,
    prompt: str,
    json_mode: bool = True
) -> str:

    """Send one bounded request to Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    client = Groq(
        api_key=api_key,
        timeout=60.0,
        max_retries=0
    )

    system_message = instructions
    user_message = prompt

    request_args = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        
        "temperature": 0.2,
        "max_completion_tokens": 300 if not json_mode else 1500,
        "reasoning_effort": "low",
        "include_reasoning": False

    }

    if json_mode:

        request_args["messages"][0]["content"] += (
            " Return the response as valid JSON."
        )

        request_args["messages"][1]["content"] += (
            " Output must be valid JSON."
        )

        request_args["response_format"] = {
            "type": "json_object"
        }

    response = client.chat.completions.create(
        **request_args
    )

    content = (
        response.choices[0].message.content or ""
    )

    if not content.strip():
        raise RuntimeError(
            "The model returned an empty response."
        )

    return content.strip()
