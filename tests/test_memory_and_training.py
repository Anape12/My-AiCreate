import json
import tempfile
import unittest
from pathlib import Path

from memory.experience_memory import ExperienceMemory
from memory.sourced_knowledge_memory import SourcedKnowledgeMemory
from training.dataset_exporter import export_successful_experiences
from training.pipeline import prepare_fine_tuning
from training.model_registry import ModelRegistry


class MemoryAndTrainingTests(unittest.TestCase):
    def test_experience_memory_saves_and_searches_successful_record(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = ExperienceMemory(Path(directory) / "experiences.jsonl")
            memory.save({"query": "東京 天気", "plan": ["weather"], "answer": "雨", "success": True, "review_status": "approved", "score": 5})
            memory.save({"query": "大阪 天気", "plan": ["weather"], "answer": "晴れ", "success": False})

            found = memory.search("東京 天気")

            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["answer"], "雨")

    def test_experience_requires_review_before_training(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = ExperienceMemory(Path(directory) / "experiences.jsonl")
            experience_id = memory.save({"query": "質問", "answer": "十分に長い回答です", "success": True})
            reviewed = memory.review(experience_id, "approved", score=5)

            self.assertEqual(reviewed["review_status"], "approved")
            self.assertEqual(reviewed["score"], 5)

    def test_exporter_writes_only_successful_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "training.jsonl"
            count = export_successful_experiences([
                {"query": "質問", "answer": "回答", "success": True},
                {"query": "失敗", "answer": "", "success": False},
            ], output)

            record = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(count, 1)
            self.assertEqual(record["messages"][1]["content"], "回答")

    def test_pipeline_curates_records_and_writes_review_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            _, manifest = prepare_fine_tuning([
                {"query": "質問", "answer": "十分に長い回答です", "success": True, "review_status": "approved", "score": 5, "tool_results": "ok"},
                {"query": "質問", "answer": "短い", "success": True, "review_status": "pending", "tool_results": "ok"},
            ], directory, "mistral")

            self.assertEqual(manifest["accepted"], 1)
            self.assertEqual(manifest["rejected"], 1)
            self.assertEqual(manifest["status"], "ready_for_review")

    def test_only_ready_models_can_be_activated(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = ModelRegistry(Path(directory) / "models.json")
            registry.register("candidate", "mistral", "training_prepared")
            with self.assertRaises(ValueError):
                registry.activate("candidate")

            registry.register("candidate", "mistral", "ready", "my-ai:latest")
            registry.activate("candidate")
            self.assertEqual(registry.active_model(), "candidate")

    def test_sourced_knowledge_is_persisted_with_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = SourcedKnowledgeMemory(Path(directory) / "knowledge.jsonl")
            memory.add("東京のイベント情報", "example search", "東京 イベント", "https://example.com")

            result = memory.search("東京 イベント")

            self.assertEqual(result[0]["source"], "example search")
            self.assertEqual(result[0]["url"], "https://example.com")


if __name__ == "__main__":
    unittest.main()
