class EvaluationGate:
    """Conservative pre-filter; human approval remains the training authority."""

    def evaluate(self, answer: str, tool_results: str, successful: bool) -> tuple[bool, str]:
        if not successful or not answer.strip():
            return False, "No successful answer was produced."
        if "could not be completed" in tool_results:
            return False, "At least one tool failed."
        if answer.startswith("LLM provider could not"):
            return False, "The model was unavailable."
        return True, "Awaiting human review."
