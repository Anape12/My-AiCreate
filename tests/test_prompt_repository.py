import tempfile
import unittest
from pathlib import Path

from prompt_repository import PromptRepository


class PromptRepositoryTests(unittest.TestCase):
    def test_combines_character_and_mode_prompts(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt_dir = Path(directory) / "mia"
            prompt_dir.mkdir()
            (prompt_dir / "prompt.md").write_text("基本人格", encoding="utf-8")
            (prompt_dir / "chat.md").write_text("チャット規則", encoding="utf-8")
            repository = PromptRepository(directory)
            self.assertEqual("基本人格\n\nチャット規則", repository.load("mia", "CHAT"))

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                PromptRepository(directory).load("../secret", "CHAT")

    def test_keeps_loaded_prompt_in_memory_until_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt_dir = Path(directory) / "mia"
            prompt_dir.mkdir()
            base = prompt_dir / "prompt.md"
            base.write_text("最初の人格", encoding="utf-8")
            (prompt_dir / "chat.md").write_text("チャット規則", encoding="utf-8")
            repository = PromptRepository(directory)
            first = repository.load("mia", "CHAT")
            base.write_text("変更後の人格", encoding="utf-8")
            self.assertEqual(first, repository.load("mia", "CHAT"))


if __name__ == "__main__":
    unittest.main()
