import json


class ReactAgent:

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    def build_prompt(self, query, context):
        return f"""
あなたはAIエージェントです。

必ずJSONで出力してください:

{{
  "thought": "次に何をするか",
  "action": "train | weather | none"
}}

# ルール
- JSON以外は出力しない
- actionは必ず指定された値から選ぶ

# 質問
{query}

# これまでの情報
{context}
"""

    def parse(self, response):
        try:
            response = response.replace("```json", "").replace("```", "")
            data = json.loads(response)
            return data.get("action", "none")
        except:
            return "none"

    def run(self, query, max_steps=3):
        context = ""

        for _ in range(max_steps):

            prompt = self.build_prompt(query, context)
            response = self.llm.invoke(prompt)

            action = self.parse(response)

            if action in self.tools:
                # 👇 query渡すの重要
                result = self.tools[action](query)
                context += f"\n[{action}結果]: {result}"
            else:
                break

        return context
