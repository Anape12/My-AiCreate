def refine_answer(answer: str, rag_context: str) -> str:
    if not answer:
        return answer

    if rag_context and "分からない" in answer:
        return answer.replace("分からない", "参考情報の範囲では確認できませんでした")

    return answer
