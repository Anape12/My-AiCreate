import os

import requests

from .tool import Tool


class TrainTool(Tool):
    name = "train"
    description = "Gets public transit status from the configured transit-status endpoint."
    requires_online = True

    def execute(self, input: str) -> str:
        endpoint = os.getenv("TRAIN_STATUS_URL")
        if not endpoint:
            return "Train status is unavailable because TRAIN_STATUS_URL is not configured."
        response = requests.get(endpoint, params={"q": input}, timeout=10)
        response.raise_for_status()
        return response.text[:4000]
