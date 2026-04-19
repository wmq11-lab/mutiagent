from mutiagent.utils.syntax_guard import exec_syntax_error


def test_exec_syntax_error_none_on_valid() -> None:
    assert exec_syntax_error("x = 1\n") is None


def test_exec_syntax_error_on_unterminated_string() -> None:
    err = exec_syntax_error("patch('foo.bar\n", filename="t.py")
    assert err is not None
    assert "SyntaxError" in err
