def get_quick_answer(query: str):
    text = query.lower()

    if "if文" in text:
        return "if文は、条件によって処理を分けるための書き方です。たとえば「雨なら傘を持つ」のような判断をコードにできます。"

    if "こんにちは" in text or "hi" in text:
        return "こんにちは。今日はどうした？気になることを気軽に話してね。"

    return None
