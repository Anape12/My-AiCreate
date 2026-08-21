import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _terms(text: str) -> set[str]:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    terms = set(re.findall(r"[\w]+", normalized))
    compact = re.sub(r"\s+", "", normalized)
    terms.update(compact[index:index + 2] for index in range(max(0, len(compact) - 1)))
    return {term for term in terms if term}


class SourcedKnowledgeMemory:
    """Persistent, source-attributed web knowledge cache for offline retrieval."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def add(self, content: str, source: str, query: str, url: str = "") -> None:
        if not content.strip():
            return
        records = self.all()
        if any(record.get("content") == content and record.get("source") == source for record in records):
            return
        records.append({
            "id": str(uuid4()),
            "content": content.strip(),
            "source": source,
            "url": url,
            "query": query,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        })
        self.path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8"
        )

    def search(self, query: str, limit: int = 3) -> list[dict]:
        query_terms = _terms(query)
        scored = []
        for record in self.all():
            record_terms = _terms(record.get("content", "") + " " + record.get("query", ""))
            union = query_terms | record_terms
            score = len(query_terms & record_terms) / len(union) if union else 0.0
            if score:
                scored.append((score, record))
        return [record for _, record in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]
