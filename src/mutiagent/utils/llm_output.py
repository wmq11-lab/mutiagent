"""Normalize LLM-produced source text (e.g. strip markdown fences)."""


def strip_markdown_code_fence(text: str) -> str:
    """
    If the model wrapped the answer in ``` / ```python fences, return inner code only.
    Otherwise return text stripped of outer whitespace.
    """
    s = text.strip()
    if not s.startswith("```"):
        return s
    parts = s.split("\n", 1)
    if len(parts) < 2:
        return s
    body = parts[1]
    if "```" in body:
        body = body[: body.rfind("```")].rstrip()
    return body.strip()
