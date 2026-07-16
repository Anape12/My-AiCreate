def get_quick_answer(query: str):
    text = query.lower()

    if "if文" in text:
        return "if文は条件によって処理を分岐するための構文です。"

    if "こんにちは" in text or "hi" in text:
        return "こんにちは！何を知りたいですか？"

    return None
