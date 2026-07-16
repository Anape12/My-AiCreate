import re


def calculate(query: str):
    text = query.replace("、", "").replace("。", "")

    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not m:
        return None

    amount = float(m.group(1))

    if "年間" in text or "1年" in text or "365日" in text:
        return round(amount * 365, 2)

    if "月間" in text or "1か月" in text or "30日" in text:
        return round(amount * 30, 2)

    return None
