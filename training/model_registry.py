"""Records the model lifecycle without coupling the API to one base model."""

import json
from pathlib import Path


class ModelRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict:
        if not self.path.exists():
            return {"active_model": None, "models": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def register(self, name: str, base_model: str, stage: str, artifact: str = "") -> None:
        data = self._read()
        data["models"][name] = {"base_model": base_model, "stage": stage, "artifact": artifact}
        self._write(data)

    def activate(self, name: str) -> None:
        data = self._read()
        if name not in data["models"]:
            raise ValueError(f"Unknown model: {name}")
        if data["models"][name]["stage"] != "ready":
            raise ValueError("Only a model marked 'ready' can be activated.")
        data["active_model"] = name
        self._write(data)

    def active_model(self) -> str | None:
        return self._read().get("active_model")

    def active_runtime_model(self) -> str | None:
        data = self._read()
        name = data.get("active_model")
        if not name:
            return None
        return data["models"][name].get("artifact") or name
