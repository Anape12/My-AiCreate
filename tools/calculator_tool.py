from rag.calculator import calculate

from .tool import Tool


class CalculatorTool(Tool):
    name = "calculator"
    description = "Calculates amounts and simple cost conversions from the question."

    def execute(self, input: str) -> str:
        result = calculate(input)
        if result is None:
            return "No supported calculation was found in the request."
        return str(result)
