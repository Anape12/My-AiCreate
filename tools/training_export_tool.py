from .tool import Tool
from training.pipeline import prepare_fine_tuning


class TrainingExportTool(Tool):
    name = "export_training_data"
    description = "Exports successful experience records as JSONL for later fine-tuning."

    def __init__(self, experience_memory, output_path, base_model: str):
        self.experience_memory = experience_memory
        self.output_path = output_path
        self.base_model = base_model

    def execute(self, input: str) -> str:
        _, manifest = prepare_fine_tuning(
            self.experience_memory.all(), self.output_path.parent, self.base_model
        )
        return (
            f"Prepared {manifest['accepted']} reviewed examples; rejected {manifest['rejected']}. "
            f"Review {self.output_path.parent / 'manifest.json'} before running fine-tuning."
        )
