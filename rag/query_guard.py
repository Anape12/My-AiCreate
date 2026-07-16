def normalize_query(query: str) -> str:
    text = query.strip()
    if not text:
        return text

    if "本能寺の変" in text:
        return "本能寺の変は何年に起きたかを、歴史的事実として答えてください。"

    if any(keyword in text for keyword in ["業務", "システム", "要件", "設計", "運用", "承認", "在庫", "受注", "請求", "顧客"]):
        return f"{text}\n業務システムとしての観点で、実務的かつ具体的に回答してください。"

    return text
