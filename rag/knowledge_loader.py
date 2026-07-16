from pathlib import Path


class KnowledgeLoader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self):
        if not self.file_path.exists():
            return []
        return [line.strip() for line in self.file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
