"""
Baseline / 实验表格指标 — 本仓库中的计算位置与搬运说明（汇总单文件）

表中常见 9 列与实现对应关系
============================

1) 语句覆盖率(%)
   - 实现: evaluation.coverage_json.parse_coverage_json
   - 输入: coverage.py 生成的 JSON（ totals 或 files 聚合）
   - 输出键: line_coverage（实为语句覆盖百分比）
   - 写入实验: evaluation.experiment_run_log._run_coverage_json + build_experiment_run_record
   - 依赖 pytest-cov、--cov-branch 时才有可靠分支数据

2) 分支覆盖率(%)
   - 同上 parse_coverage_json → branch_coverage

3) 变更函数覆盖率（比例 + 可选百分数）
   - 实现: evaluation.changed_function_coverage.build_changed_function_coverage_report
   - 输入: WorkflowState.change_analysis + changed_files（function/method）；同次 coverage 完整 JSON paths files.*.functions
   - 口径: 变更函数中 summary.covered_lines>0 的个数 / 变更函数数
   - 落盘: workflow_steps/<stamp>/changed_function_coverage.json；experiment_record 摘要 changed_function_coverage_ratio|_percent
   - 调度: experiment_run_log.append_experiment_run_log

4) 测试通过率(%)
   - 实现: evaluation.pytest_parsing.parse_pytest_output
   - 输入: pytest stdout+stderr 合并文本 → pass_rate

5) 测试用例数（注意两套）
   - test_count: 生成源码中 def test_* 计数（AST）— experiment_run_log._count_test_functions_source + build_experiment_run_record
   - total_tests: pytest 摘要 — parse_pytest_output

6) 生成时间(s)
   - 全流程：工作流结束时 experiment_run_log.merge_workflow_total_time_into_experiment_record 写入
     ``workflow_total_seconds``（秒）、``workflow_finished_at``；Execution 写 record 时附带 ``workflow_started_at``。
     跨度为从 graph/workflow._execute_workflow 起点到全部步骤（含 Evaluation/Feedback）结束。
   - 仅 LLM 生成阶段：见 mutiagent.log 中 TestGenAgent「总耗时 Nms」÷1000。

7) Precision（主流程口径：pytest 通过率）
8) Recall（主流程口径：变更 + 行被 coverage 执行覆盖的比例）
9) F1
   - 实现: evaluation.metrics.compute_all_metrics；变更行 Recall 对齐见 evaluation.change_line_coverage
   - 喂数: evaluation_agent 从 junit 得 passed/tests 为 Precision；report_dir/coverage.json × state.diff 得 Recall；F1=2PR/(P+R)。
   - 离线 / 仅有列表且无 pytest 输出时仍可回退为旧「选测×故障」Precision/Recall/F1。
   - Ts 收窄: nodes.execution_agent 写 execution.selected_tests（仅旧口径使用）

离线批处理补充
===============
- scripts/collect_experiment_metrics.py：本地 pytest --cov、变更行覆盖率 change_line_coverage_from_diff 等。

搬运最小依赖（可复制文件）
========================
- metrics.py — P/R/F1 等（纯函数，依赖最少）
- coverage_json.py — 覆盖率 JSON 解析
- pytest_parsing.py — 通过率
- changed_function_coverage.py — 变更函数覆盖（依赖 state 形状；可改为传入 list[dict]）
- experiment_run_log.py — 拼装 experiment_record（依赖 WorkflowState 与数据集路径）

本模块提供 METRICS_INDEX 与常用符号再导出，便于::

    from mutiagent.evaluation.baseline_metrics_guide import compute_all_metrics
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 程序化索引（表头关键字 → 元信息）
# ---------------------------------------------------------------------------

METRICS_INDEX: dict[str, dict[str, Any]] = {
    "statement_coverage_pct": {
        "label_zh": "语句覆盖率(%)",
        "implementations": ["mutiagent.evaluation.coverage_json:parse_coverage_json"],
        "record_fields": ["line_coverage", "covered_lines", "total_lines"],
        "notes": "line_coverage 为语句维度百分比（命名历史原因）。",
    },
    "branch_coverage_pct": {
        "label_zh": "分支覆盖率(%)",
        "implementations": ["mutiagent.evaluation.coverage_json:parse_coverage_json"],
        "record_fields": ["branch_coverage"],
        "notes": "需 coverage JSON 含分支统计；子进程使用 --cov-branch。",
    },
    "changed_function_coverage": {
        "label_zh": "变更函数覆盖率",
        "implementations": [
            "mutiagent.evaluation.changed_function_coverage:build_changed_function_coverage_report",
            "mutiagent.evaluation.experiment_run_log:append_experiment_run_log",
        ],
        "record_fields": ["changed_function_coverage_ratio", "changed_function_coverage_percent"],
        "artifact": "workflow_steps/<stamp>/changed_function_coverage.json",
    },
    "test_pass_rate_pct": {
        "label_zh": "测试通过率(%)",
        "implementations": ["mutiagent.evaluation.pytest_parsing:parse_pytest_output"],
        "record_fields": ["pass_rate", "passed", "failed", "errors", "skipped"],
    },
    "test_case_count": {
        "label_zh": "测试用例数",
        "implementations": [
            "mutiagent.evaluation.experiment_run_log:_count_test_functions_source",
            "mutiagent.evaluation.pytest_parsing:parse_pytest_output → total_tests",
        ],
        "record_fields": ["test_count（生成 AST）", "total_tests（pytest）"],
        "notes": "两字段含义不同；论文/表格需注明口径。",
    },
    "generation_time_s": {
        "label_zh": "生成时间(s)",
        "implementations": [
            "仅 TestGen：mutiagent.nodes.test_gen_agent 日志「总耗时 N ms」",
            "全流程墙钟：experiment_run_log.merge_workflow_total_time_into_experiment_record → experiment_record.workflow_total_seconds（秒）；起止见 workflow_started_at / workflow_finished_at",
        ],
        "record_fields": ["workflow_total_seconds", "workflow_started_at", "workflow_finished_at"],
        "notes": "workflow_total_seconds 为 CodeChange 起至 Feedback 结束整图（perf_counter）；与仅 LLM 生成阶段不同。",
    },
    "precision": {
        "label_zh": "Precision（通过率）",
        "implementations": [
            "mutiagent.evaluation.metrics:compute_all_metrics / pass_rate_precision",
            "mutiagent.nodes.evaluation_agent:evaluation_agent（junit passed/total）",
        ],
        "state_fields": ["state.diff + changed_files（Recall 用）", "junit_cases / junit_summary"],
        "evaluation_fields": ["evaluation.metrics.precision", "evaluation.metric_flags.precision_meaningful"],
    },
    "recall_bug_detection": {
        "label_zh": "Recall（变更行覆盖）",
        "implementations": [
            "mutiagent.evaluation.change_line_coverage:change_line_coverage_from_diff_and_cov_paths",
            "mutiagent.evaluation.metrics:test_selection_recall（仅旧回退）",
            "mutiagent.nodes.evaluation_agent:evaluation_agent",
        ],
        "notes": "全流程默认 Recall 为 diff 变更 + 行相对 coverage.json 的覆盖比例；collect 仅用列表且无 pytest/cov 时可能仍为旧选测 recall。",
    },
    "f1": {
        "label_zh": "F1(%)",
        "implementations": ["mutiagent.evaluation.metrics:f1_score / compute_all_metrics"],
    },
}


# ---------------------------------------------------------------------------
# 再导出：单文件入口 import（搬运时优先依赖这些符号）
# ---------------------------------------------------------------------------

from mutiagent.evaluation.changed_function_coverage import build_changed_function_coverage_report
from mutiagent.evaluation.coverage_json import parse_coverage_json
from mutiagent.evaluation.experiment_run_log import build_experiment_run_record
from mutiagent.evaluation.metrics import compute_all_metrics
from mutiagent.evaluation.pytest_parsing import parse_pytest_output

__all__ = [
    "METRICS_INDEX",
    "build_changed_function_coverage_report",
    "build_experiment_run_record",
    "compute_all_metrics",
    "parse_coverage_json",
    "parse_pytest_output",
]
