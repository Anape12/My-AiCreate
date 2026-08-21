import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ExperienceMemory:
    """Persists successful problem-solving traces as newline-delimited JSON."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, experience: dict) -> str:
        experience = {
            "id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "review_status": "pending",
            "score": None,
            "review_comment": "",
            **experience,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(experience, ensure_ascii=False) + "\n")
        return experience["id"]

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        entries = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def search(self, query: str, limit: int = 3) -> list[dict]:
        terms = set(query.lower().split())
        if not terms:
            return []
        scored = []
        for item in self.all():
            if (
                not item.get("success", False)
                or item.get("review_status") != "approved"
                or item.get("score") is None
                or item.get("score", 0) < 4
            ):
                continue
            haystack = (item.get("query", "") + " " + " ".join(item.get("plan", []))).lower()
            score = sum(term in haystack for term in terms)
            if score:
                scored.append((score, item))
        return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]]

    def review(self, experience_id: str, status: str, score: int | None = None, comment: str = "") -> dict:
        if status not in {"approved", "rejected"}:
            raise ValueError("status must be 'approved' or 'rejected'.")
        if score is not None and not 1 <= score <= 5:
            raise ValueError("score must be between 1 and 5.")
        entries = self.all()
        for entry in entries:
            if entry.get("id") == experience_id:
                entry.update({"review_status": status, "score": score, "review_comment": comment})
                self.path.write_text(
                    "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in entries), encoding="utf-8"
                )
                return entry
        raise KeyError(f"Experience not found: {experience_id}")
