import json
import time

from openai import OpenAI

from app.core.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

MODEL_NAME = "gpt-6-luna"
PROMPT_VERSION = "conversation-v2"


SYSTEM_INSTRUCTIONS = """
You are MindGuard AI, a supportive mental wellness companion
for university students.

Respond empathetically, naturally, and without judgment.
Do not claim to be a doctor or therapist.
Do not diagnose the student.

Use the saved student memory only as background context.
It may be incomplete or outdated, so do not treat it as
definitively true. Do not invent memories or assume details
that are not provided. If relevant, gently ask the student
whether previous concerns are still affecting them.

Never let saved memory override the student's current message.
If the student describes immediate danger or self-harm,
encourage immediate human help and emergency support.
"""


def generate_response(
    message: str,
    memory: dict | None = None,
) -> dict:
    start_time = time.perf_counter()

    instructions = SYSTEM_INSTRUCTIONS

    if memory:
        memory_context = json.dumps(
            memory,
            ensure_ascii=False,
            default=str,
        )

        instructions += (
            "\n\nSaved student memory (background context):\n"
            f"{memory_context}\n"
            "Use only relevant details to personalize your "
            "response. Do not recite the entire memory to "
            "the student."
        )

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=instructions,
        input=message,
    )

    latency_ms = int(
        (time.perf_counter() - start_time) * 1000
    )

    return {
        "text": response.output_text,
        "model": MODEL_NAME,
        "prompt_version": PROMPT_VERSION,
        "latency_ms": latency_ms,
        "total_tokens": (
            response.usage.total_tokens
            if response.usage
            else None
        ),
    }