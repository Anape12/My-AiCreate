import re
import threading
from pathlib import Path


class PromptRepository:
    """Loads version-controlled character prompts from the prompts directory."""

    KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parent / "prompts").resolve()
        self._cache = {}
        self._lock = threading.Lock()

    def preload_all(self):
        """Load every configured character prompt once during application startup."""
        if not self.root.is_dir():
            raise FileNotFoundError(f"プロンプトディレクトリが見つかりません: {self.root}")
        for directory in self.root.iterdir():
            if directory.is_dir() and self.KEY_PATTERN.fullmatch(directory.name):
                self.load(directory.name, "CHAT")
                self.load(directory.name, "THREAD")

    def load(self, prompt_key, conversation_type):
        key = (prompt_key or "").strip().lower()
        if not self.KEY_PATTERN.fullmatch(key):
            raise ValueError("プロンプトキーの形式が不正です。")
        mode = "thread" if conversation_type.upper() == "THREAD" else "chat"
        cache_key = (key, mode)
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            files = (self.root / key / "prompt.md", self.root / key / f"{mode}.md")
            missing = [str(path) for path in files if not path.is_file()]
            if missing:
                raise FileNotFoundError(f"プロンプトが見つかりません: {', '.join(missing)}")
            content = "\n\n".join(path.read_text(encoding="utf-8").strip() for path in files)
            self._cache[cache_key] = content
            return content
