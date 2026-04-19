"""对生成的 Python 源码做 compile 校验，避免落盘未闭合字符串等语法错误。"""


def exec_syntax_error(src: str, *, filename: str = "<mutiagent>") -> str | None:
    """若 `compile(..., 'exec')` 失败则返回简短错误说明，否则返回 None。"""
    try:
        compile(src, filename, "exec")
        return None
    except SyntaxError as e:
        ln = getattr(e, "lineno", None) or "?"
        return f"SyntaxError line {ln}: {e.msg}"
