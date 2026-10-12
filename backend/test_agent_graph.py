
from app.services.agent_graph import mindguard_graph


def run_test(message: str) -> None:
    result = mindguard_graph.invoke({
        "student_id": "test-student",
        "conversation_id": "test-conversation",
        "message": message,
        "screening": {},
        "flagged": False,
        "response": "",
        "response_metadata": {},
        "route": "",
    })

    print("Message:", message)
    print("Flagged:", result["flagged"])
    print("Route:", result["route"])
    print("Response:", result["response"])
    print("Response Metadata:", result["response_metadata"])
    print("-" * 50)


run_test("I feel stressed about my university exams.")
run_test("I want to kill myself.")
