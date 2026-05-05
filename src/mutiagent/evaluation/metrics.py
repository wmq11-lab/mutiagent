from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _to_set(items: Iterable[Any] | None) -> set[str]:
    if items is None:
        return set()
    return {str(x) for x in items}


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def test_selection_precision(selected_tests: Iterable[Any] | None, failing_tests: Iterable[Any] | None) -> float:
    ts = _to_set(selected_tests)
    tf = _to_set(failing_tests)
    return _safe_div(len(ts & tf), len(ts))


def test_selection_recall(selected_tests: Iterable[Any] | None, failing_tests: Iterable[Any] | None) -> float:
    ts = _to_set(selected_tests)
    tf = _to_set(failing_tests)
    return _safe_div(len(ts & tf), len(tf))


def f1_score(precision: float, recall: float) -> float:
    return _safe_div(2 * precision * recall, precision + recall)


def test_reduction_rate(selected_tests: Iterable[Any] | None, all_tests: Iterable[Any] | None) -> float:
    ts = _to_set(selected_tests)
    tall = _to_set(all_tests)
    return 1.0 - _safe_div(len(ts), len(tall))


def time_reduction(execution_time: float | int, full_time: float | int) -> float:
    return 1.0 - _safe_div(float(execution_time), float(full_time))


def redundancy_rate(precision: float) -> float:
    return 1.0 - precision


def pass_rate_precision(passed: int, total: int) -> float:
    """通过率 Precision：passed / total（0~1）。"""
    return _safe_div(float(max(0, passed)), float(max(0, total)))


def compute_all_metrics(
    *,
    selected_tests: Iterable[Any] | None,
    all_tests: Iterable[Any] | None,
    failing_tests: Iterable[Any] | None,
    execution_time: float | int,
    full_time: float | int,
    precision_pass_rate: float | None = None,
    recall_change_line: float | None = None,
) -> dict[str, float]:
    """
    默认：选测 Precision/Recall/F1（|Ts∩Tf| 类）；可选覆盖为：

    - precision_pass_rate：pytest 通过率 passed/total（0~1）
    - recall_change_line：变更 + 行中被执行覆盖的比例（0~1）

    二者均给出时 F1 = 2PR/(P+R)；仅给出一项时不写入 f1（调用方宜用 metric_flags 控制展示）。
    未给出覆盖参数时维持旧「选测 × 故障集」语义（如 collect_experiment_metrics 纯列表模式）。
    """
    reduction = test_reduction_rate(selected_tests, all_tests)
    tr = time_reduction(execution_time, full_time)

    if precision_pass_rate is not None or recall_change_line is not None:
        p = float(precision_pass_rate) if precision_pass_rate is not None else 0.0
        r = float(recall_change_line) if recall_change_line is not None else 0.0
        redundancy = redundancy_rate(p) if precision_pass_rate is not None else 1.0
        out: dict[str, float] = {
            "reduction": round(reduction, 6),
            "time_reduction": round(tr, 6),
            "redundancy": round(redundancy, 6),
        }
        if precision_pass_rate is not None:
            out["precision"] = round(p, 6)
        if recall_change_line is not None:
            out["recall"] = round(r, 6)
        if precision_pass_rate is not None and recall_change_line is not None:
            out["f1"] = round(f1_score(p, r), 6)
        return out

    precision = test_selection_precision(selected_tests, failing_tests)
    recall = test_selection_recall(selected_tests, failing_tests)
    f1 = f1_score(precision, recall)
    redundancy = redundancy_rate(precision)
    return {
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "reduction": round(reduction, 6),
        "time_reduction": round(tr, 6),
        "redundancy": round(redundancy, 6),
    }


if __name__ == "__main__":
    # Simple usage example
    example = compute_all_metrics(
        selected_tests=["tests/test_a.py::test_x", "tests/test_b.py::test_y"],
        all_tests=["tests/test_a.py::test_x", "tests/test_b.py::test_y", "tests/test_c.py::test_z"],
        failing_tests=["tests/test_b.py::test_y"],
        execution_time=12.0,
        full_time=30.0,
    )
    print(example)
