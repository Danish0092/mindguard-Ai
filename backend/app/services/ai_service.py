import time

from openai import OpenAI

from app.core.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

MODEL_NAME = "gpt-6-luna"
PROMPT_VERSION = "conversation-v1"


def generate_response(message: str) -> dict:
    start_time = time.perf_counter()

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=(
            "You are MindGuard AI, a supportive mental wellness "
            "companion for university students. "
            "Respond empathetically and naturally. "
            "Do not claim to be a doctor or therapist. "
            "Do not diagnose the student. "
            "If the student describes immediate danger or "
            "self-harm, encourage them to seek immediate "
            "human help and emergency support."
        ),
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