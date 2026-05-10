import json
import sqlite3
from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from mutiagent.api.assistant import router as assistant_router
from mutiagent.graph.state import GenerateTestsRequest, GenerateTestsResponse
from mutiagent.graph.workflow import iter_workflow_events, run_workflow
from mutiagent.utils.logging_config import configure_app_logging
from mutiagent.utils.run_db import resolve_db_path


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_app_logging()
    yield


app = FastAPI(
    title="mutiagent-mvp",
    version="0.1.0",
    description="面向代码变更的多智能体回归测试用例生成（LangGraph + FastAPI）。",
    lifespan=lifespan,
)

app.include_router(assistant_router)


_INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>mutiagent API</title>
  <style>
    :root { --bg:#f6f8fa; --card:#fff; --border:#d0d7de; --text:#1f2328; --muted:#656d76; --accent:#0969da; }
    body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "PingFang SC", sans-serif;
      background: var(--bg); color: var(--text); margin: 0; padding: 1.5rem; line-height: 1.6; max-width: 52rem; margin-inline: auto; }
    h1 { font-size: 1.5rem; margin: 0 0 0.25rem; }
    .sub { color: var(--muted); font-size: 0.95rem; margin-bottom: 1.5rem; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
    h2 { font-size: 1.05rem; margin: 0 0 0.75rem; color: var(--text); }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); vertical-align: top; }
    th { color: var(--muted); font-weight: 600; width: 7rem; }
    code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.82rem; }
    code { background: #eff1f3; padding: 0.1rem 0.35rem; border-radius: 4px; }
    pre { background: #24292f; color: #e6edf3; padding: 0.85rem 1rem; border-radius: 6px; overflow: auto; white-space: pre-wrap; word-break: break-word; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .links { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 0.5rem; }
    .pill { display: inline-block; padding: 0.35rem 0.65rem; background: #ddf4ff; border-radius: 6px; font-size: 0.88rem; }
    ul { margin: 0.4rem 0; padding-left: 1.2rem; color: var(--muted); font-size: 0.92rem; }
  </style>
</head>
<body>
  <h1>mutiagent</h1>
  <p class="sub">MVP：输入本地仓库路径与 <code>git diff</code>，经多智能体流水线生成 pytest 用例并可选执行评估。</p>

  <div class="card">
    <h2>快速入口</h2>
    <div class="links">
      <a class="pill" href="/ui/">Web 控制台（/ui）</a>
      <a class="pill" href="/docs">Swagger UI（/docs）</a>
      <a class="pill" href="/redoc">ReDoc（/redoc）</a>
      <a class="pill" href="/openapi.json">OpenAPI JSON</a>
      <a class="pill" href="/health">健康检查</a>
    </div>
  </div>

  <div class="card">
    <h2>HTTP 接口说明</h2>
    <table>
      <thead><tr><th>方法</th><th>路径</th><th>说明</th></tr></thead>
      <tbody>
        <tr><td><code>GET</code></td><td><code>/</code></td><td>本说明页</td></tr>
        <tr><td><code>GET</code></td><td><code>/ui/</code></td><td>Web 工作台（顶栏 / 侧栏多视图，调用全流程）</td></tr>
        <tr><td><code>GET</code></td><td><code>/health</code></td><td>存活探测，返回 <code>{"ok": true}</code></td></tr>
        <tr><td><code>POST</code></td><td><code>/api/assistant/chat</code></td><td>AI 助理多轮对话（携带当前分析上下文 JSON）</td></tr>
        <tr><td><code>POST</code></td><td><code>/generate-tests</code></td><td>
          请求体 JSON：<code>repo_path</code>（本地项目根目录）、<code>diff</code>（unified diff 全文）、
          <code>run_eval</code>（可选，默认 <code>true</code>：在目标仓库执行生成的 pytest 并落盘报告）。
        </td></tr>
        <tr><td><code>POST</code></td><td><code>/generate-tests-stream</code></td><td>
          同上请求体，响应为 <code>application/x-ndjson</code>：多行 <code>{"type":"progress",...}</code>，最后一行 <code>{"type":"complete","result":...}</code> 或 <code>{"type":"error","message":...}</code>（供前端进度条）。
        </td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>调用示例</h2>
    <p class="sub" style="margin-bottom:0.5rem">将 <code>repo_path</code> 换成你的项目绝对路径，<code>diff</code> 为单行转义后的 diff 或使用文件配合脚本。</p>
    <pre>curl -s http://127.0.0.1:8000/generate-tests \\
  -H "Content-Type: application/json" \\
  -d '{"repo_path":"/path/to/project","diff":"diff --git a/foo.py b/foo.py\\n...","run_eval":true}'</pre>
  </div>

  <div class="card">
    <h2>说明</h2>
    <ul>
      <li>LLM 与 Key 由环境变量 / 项目根目录 <code>.env</code> 配置（见 README）。</li>
      <li><code>run_eval=true</code> 时会在目标仓库下生成 <code>.mutiagent/reports/&lt;时间戳&gt;/</code>（含 <code>report.html</code>、junit 等）。</li>
      <li>关闭写盘可设环境变量 <code>MUTIAGENT_DISABLE_TEST_REPORT=1</code>。</li>
      <li>默认在 <code>run_eval</code> 时自动为被测仓库创建 <code>.mutiagent/mutiagent_pytest_venv</code> 并安装 <code>requirements.txt</code> 等；无 requirements 时根据变更的 .py 中 import 白名单推断常见 PyPI 依赖（<code>mutiagent_inferred_pip.txt</code>，可用 <code>MUTIAGENT_INFER_PIP=0</code> 关闭）。请求体中 <code>auto_venv: false</code> 或 <code>MUTIAGENT_DISABLE_AUTO_VENV=1</code> 可改回用 PATH 上 <code>python</code>。无 bugsinpy 时若 mutiagent 宿主 Python 偏旧，可设 <code>MUTIAGENT_VENV_PYTHON</code> 为 3.12+ 再删旧 venv 重跑。已自建 venv 时可设 <code>MUTIAGENT_PYTEST_PYTHON</code>（会跳过自动 venv 与自动 pip）。</li>
      <li>工作流在「项目探测」阶段会预建/复用上述 venv，再进入生成与执行。</li>
      <li>Ansible 等含 <code>lib/ansible</code> 的仓库：pytest 默认只把 <code>lib</code> 与仓库根加入 <code>PYTHONPATH</code>，不继承外层，减轻与 conda 里 <code>pip install ansible</code> 的冲突；需要继承时设 <code>MUTIAGENT_PYTEST_APPEND_PYTHONPATH=1</code>。</li>
      <li>pytest 文本：每次运行会写入仓库 <code>.mutiagent/reports/&lt;时间戳&gt;/pytest_stdout.txt</code> 与 <code>pytest_stderr.txt</code>；摘要同时写入项目根 <code>log/mutiagent.log</code>（<code>ExecutionAgent</code> 段落）。API 每次启动默认清空该日志，保留历史请设 <code>MUTIAGENT_LOG_APPEND=1</code>。</li>
      <li>流水线与 <code>mutiagent.workflow</code> 日志默认写入项目根目录 <code>log/mutiagent.log</code>。</li>
    </ul>
  </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return _INDEX_HTML


@app.get("/health")
def health() -> dict:
    return {"ok": True}


def _app_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _open_db() -> sqlite3.Connection | None:
    db_path = resolve_db_path(_app_repo_root())
    if not db_path.exists():
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/db/projects")
def list_db_projects() -> dict:
    conn = _open_db()
    if conn is None:
        return {"items": []}
    try:
        rows = conn.execute(
            """
            SELECT
                wr.repo_path AS repo_path,
                COUNT(DISTINCT wr.run_id) AS run_count,
                MAX(wr.started_at) AS last_started_at,
                SUM(CASE WHEN wr.status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
                SUM(CASE WHEN wr.status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
                COUNT(gtf.id) AS generated_file_count
            FROM workflow_runs wr
            LEFT JOIN generated_test_files gtf ON gtf.run_id = wr.run_id
            GROUP BY wr.repo_path
            ORDER BY last_started_at DESC
            """
        ).fetchall()
        return {
            "items": [
                {
                    "repo_path": row["repo_path"],
                    "run_count": int(row["run_count"] or 0),
                    "last_started_at": row["last_started_at"],
                    "completed_count": int(row["completed_count"] or 0),
                    "failed_count": int(row["failed_count"] or 0),
                    "generated_file_count": int(row["generated_file_count"] or 0),
                }
                for row in rows
            ]
        }
    finally:
        conn.close()


@app.get("/db/project-runs")
def list_project_runs(
    repo_path: str = Query(..., description="项目仓库绝对路径"),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    conn = _open_db()
    if conn is None:
        return {"repo_path": repo_path, "runs": []}
    try:
        run_rows = conn.execute(
            """
            SELECT
                wr.run_id,
                wr.started_at,
                wr.finished_at,
                wr.status,
                wr.error_message,
                ex.exit_code
            FROM workflow_runs wr
            LEFT JOIN (
                SELECT e1.run_id, e1.exit_code
                FROM executions e1
                INNER JOIN (
                    SELECT run_id, MAX(id) AS max_id
                    FROM executions
                    GROUP BY run_id
                ) e2 ON e1.id = e2.max_id
            ) ex ON ex.run_id = wr.run_id
            WHERE wr.repo_path = ?
            ORDER BY wr.started_at DESC
            LIMIT ?
            """,
            (repo_path, limit),
        ).fetchall()
        if not run_rows:
            return {"repo_path": repo_path, "runs": []}

        run_ids = [str(row["run_id"]) for row in run_rows]
        placeholders = ",".join("?" for _ in run_ids)
        case_rows = conn.execute(
            f"""
            SELECT run_id, status, COUNT(*) AS cnt
            FROM generated_test_cases
            WHERE run_id IN ({placeholders})
            GROUP BY run_id, status
            """,
            run_ids,
        ).fetchall()
        case_detail_rows = conn.execute(
            f"""
            SELECT run_id, suite, classname, case_name, case_time, status, detail
            FROM generated_test_cases
            WHERE run_id IN ({placeholders})
            ORDER BY id DESC
            """,
            run_ids,
        ).fetchall()
        file_rows = conn.execute(
            f"""
            SELECT run_id, file_path, content, assumptions_json, status, exit_code, created_at
            FROM generated_test_files
            WHERE run_id IN ({placeholders})
            ORDER BY id DESC
            """,
            run_ids,
        ).fetchall()
        eval_rows = conn.execute(
            f"""
            SELECT ws.run_id, ws.payload_json
            FROM workflow_steps ws
            INNER JOIN (
                SELECT run_id, MAX(step_index) AS max_step
                FROM workflow_steps
                WHERE node = 'EvaluationAgent' AND run_id IN ({placeholders})
                GROUP BY run_id
            ) wmax ON ws.run_id = wmax.run_id AND ws.step_index = wmax.max_step
            """,
            run_ids,
        ).fetchall()

        case_summary: dict[str, dict[str, int]] = {rid: {} for rid in run_ids}
        for row in case_rows:
            rid = str(row["run_id"])
            case_summary.setdefault(rid, {})[str(row["status"])] = int(row["cnt"] or 0)
        case_details: dict[str, list[dict]] = {rid: [] for rid in run_ids}
        for row in case_detail_rows:
            rid = str(row["run_id"])
            case_details.setdefault(rid, []).append(
                {
                    "suite": row["suite"],
                    "classname": row["classname"],
                    "case_name": row["case_name"],
                    "case_time": row["case_time"],
                    "status": row["status"],
                    "detail": row["detail"],
                }
            )

        files_by_run: dict[str, list[dict]] = {rid: [] for rid in run_ids}
        for row in file_rows:
            assumptions_raw = row["assumptions_json"] or "[]"
            try:
                assumptions = json.loads(assumptions_raw)
            except json.JSONDecodeError:
                assumptions = []
            files_by_run.setdefault(str(row["run_id"]), []).append(
                {
                    "file_path": row["file_path"],
                    "content": row["content"],
                    "assumptions": assumptions if isinstance(assumptions, list) else [],
                    "status": row["status"],
                    "exit_code": row["exit_code"],
                    "created_at": row["created_at"],
                }
            )
        metrics_by_run: dict[str, dict] = {rid: {} for rid in run_ids}
        metric_flags_by_run: dict[str, dict] = {rid: {} for rid in run_ids}
        for row in eval_rows:
            rid = str(row["run_id"])
            payload_raw = row["payload_json"] or "{}"
            try:
                payload = json.loads(payload_raw)
            except json.JSONDecodeError:
                payload = {}
            if isinstance(payload, dict):
                evaluation_obj = payload.get("evaluation") if isinstance(payload.get("evaluation"), dict) else None
                metrics_src = (
                    evaluation_obj.get("metrics") if isinstance(evaluation_obj, dict) else payload.get("metrics")
                )
                flags_src = (
                    evaluation_obj.get("metric_flags")
                    if isinstance(evaluation_obj, dict)
                    else payload.get("metric_flags")
                )
                if isinstance(metrics_src, dict):
                    metrics_by_run[rid] = metrics_src
                if isinstance(flags_src, dict):
                    metric_flags_by_run[rid] = flags_src

        runs = []
        for row in run_rows:
            rid = str(row["run_id"])
            runs.append(
                {
                    "run_id": rid,
                    "started_at": row["started_at"],
                    "finished_at": row["finished_at"],
                    "status": row["status"],
                    "error_message": row["error_message"],
                    "exit_code": row["exit_code"],
                    "case_summary": case_summary.get(rid, {}),
                    "case_details": case_details.get(rid, []),
                    "generated_tests": files_by_run.get(rid, []),
                    "evaluation_metrics": metrics_by_run.get(rid, {}),
                    "metric_flags": metric_flags_by_run.get(rid, {}),
                }
            )
        return {"repo_path": repo_path, "runs": runs}
    finally:
        conn.close()


@app.post("/generate-tests", response_model=GenerateTestsResponse)
def generate_tests(req: GenerateTestsRequest) -> GenerateTestsResponse:
    result = run_workflow(
        repo_path=req.repo_path,
        diff=req.diff,
        run_eval=req.run_eval,
        auto_venv=req.auto_venv,
        auto_install_python=req.auto_install_python,
        retrieval_enabled=req.retrieval_enabled,
        bug_pattern_enabled=req.bug_pattern_enabled,
        impact_analysis_enabled=req.impact_analysis_enabled,
        test_repair_enabled=req.test_repair_enabled,
        feedback_enabled=req.feedback_enabled,
    )
    return GenerateTestsResponse(**result)


@app.post("/generate-tests-stream")
def generate_tests_stream(req: GenerateTestsRequest) -> StreamingResponse:
    """NDJSON 流：progress 行 + 最终 complete / error。"""

    def body() -> Iterator[str]:
        for ev in iter_workflow_events(
            repo_path=req.repo_path,
            diff=req.diff,
            run_eval=req.run_eval,
            auto_venv=req.auto_venv,
            auto_install_python=req.auto_install_python,
            retrieval_enabled=req.retrieval_enabled,
            bug_pattern_enabled=req.bug_pattern_enabled,
            impact_analysis_enabled=req.impact_analysis_enabled,
            test_repair_enabled=req.test_repair_enabled,
            feedback_enabled=req.feedback_enabled,
        ):
            yield json.dumps(jsonable_encoder(ev), ensure_ascii=False) + "\n"

    return StreamingResponse(body(), media_type="application/x-ndjson; charset=utf-8")


_frontend_dir = Path(__file__).resolve().parents[3] / "frontend"
if _frontend_dir.is_dir():
    app.mount(
        "/ui",
        StaticFiles(directory=str(_frontend_dir), html=True),
        name="ui",
    )
