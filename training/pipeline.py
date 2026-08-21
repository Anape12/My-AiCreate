"""Prepares a reviewed fine-tuning job; it never starts a costly job implicitly."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .curator import curate_successful_experiences
from .dataset_exporter import export_successful_experiences


@dataclass
class FineTuneJob:
    base_model: str
    dataset_path: str
    output_dir: str
    backend: str = "trl"
    method: str = "lora"

    def command(self) -> list[str]:
        return [
            "python", "-m", "training.run_finetune",
            "--base-model", self.base_model,
            "--dataset", self.dataset_path,
            "--output-dir", self.output_dir,
            "--method", self.method,
        ]


def prepare_fine_tuning(experiences: list[dict], output_dir: str | Path, base_model: str) -> tuple[FineTuneJob, dict]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    curation = curate_successful_experiences(experiences)
    dataset_path = output / "training.jsonl"
    count = export_successful_experiences(curation.accepted, dataset_path)
    job = FineTuneJob(base_model=base_model, dataset_path=str(dataset_path), output_dir=str(output / "adapter"))
    manifest = {
        "accepted": count,
        "rejected": len(curation.rejected),
        "job": asdict(job),
        "command": job.command(),
        "status": "ready_for_review",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return job, manifest
