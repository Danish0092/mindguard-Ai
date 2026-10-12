
from typing import Any, TypedDict


class MindGuardState(TypedDict):
    student_id: str
    conversation_id: str
    message: str

    # Crisis screening
    screening: dict[str, Any]
    flagged: bool

    # Assistant response
    response: str
    response_metadata: dict[str, Any]

    # Execution metadata
    route: str
    memory: dict[str, Any]




from langgraph.graph import END, START, StateGraph

from app.services.ai_service import generate_response
from app.services.crisis_detection import assess_crisis


def crisis_screening_node(state: MindGuardState) -> dict:
    screening = assess_crisis(state["message"])
    flagged = screening["flagged"]

    return {
        "screening": screening,
        "flagged": flagged,
        "route": "crisis" if flagged else "conversation",
    }


def crisis_response_node(state: MindGuardState) -> dict:
    response = (
        "I'm concerned about your safety, and I'm glad "
        "you shared this with me. If you may act on these "
        "thoughts or are in immediate danger, contact your "
        "local emergency services or go to the nearest "
        "emergency department now. If possible, move near "
        "someone you trust and tell them directly what is "
        "happening. I cannot contact emergency services "
        "for you, and I cannot confirm that a counselor "
        "has seen this message. Are you in immediate danger "
        "right now?"
    )

    return {"response": response}



def conversation_node(state: MindGuardState) -> dict:
    ai_result = generate_response(
        state["message"],
        memory=state.get("memory") or {},
    )

    return {
        "response": ai_result["text"],
        "response_metadata": ai_result,
    }


def route_after_screening(state: MindGuardState) -> str:
    return "crisis_response" if state["flagged"] else "conversation"


graph = StateGraph(MindGuardState)

graph.add_node("crisis_screening", crisis_screening_node)
graph.add_node("crisis_response", crisis_response_node)
graph.add_node("conversation", conversation_node)

graph.add_edge(START, "crisis_screening")

graph.add_conditional_edges(
    "crisis_screening",
    route_after_screening,
    {
        "crisis_response": "crisis_response",
        "conversation": "conversation",
    },
)

graph.add_edge("crisis_response", END)
graph.add_edge("conversation", END)

mindguard_graph = graph.compile()
