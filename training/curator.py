"""Quality gates that turn raw experiences into training examples."""

from dataclasses import dataclass


@dataclass
class CurationResult:
    accepted: list[dict]
    rejected: list[dict]


def curate_successful_experiences(experiences: list[dict], min_answer_length: int = 8) -> CurationResult:
    accepted, rejected = [], []
    for experience in experiences:
        answer = str(experience.get("answer", "")).strip()
        tool_results = str(experience.get("tool_results", ""))
        valid = (
            experience.get("success") is True
            and experience.get("review_status") == "approved"
            and experience.get("score") is not None
            and experience.get("score") >= 4
            and bool(str(experience.get("query", "")).strip())
            and len(answer) >= min_answer_length
            and "could not be completed" not in tool_results
        )
        (accepted if valid else rejected).append(experience)
    return CurationResult(accepted=accepted, rejected=rejected)
