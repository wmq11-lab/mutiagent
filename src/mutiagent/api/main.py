import json
from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from mutiagent.api.assistant import router as assistant_router
from mutiagent.graph.state import GenerateTestsRequest, GenerateTestsResponse
from mutiagent.graph.workflow import iter_workflow_events, run_workflow
from mutiagent.utils.logging_config import configure_app_logging


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
      <li>pytest 默认用当前环境的 <code>python</code>；请求体 <code>auto_venv: true</code>（或环境变量 <code>MUTIAGENT_AUTO_VENV=1</code>）可在 <code>repo_path</code> 下自动创建 <code>.mutiagent/mutiagent_pytest_venv</code> 并安装依赖。</li>
      <li>也可手动为每个被测仓库建 venv，设 <code>MUTIAGENT_PYTEST_PYTHON</code> 指向该解释器。</li>
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


@app.post("/generate-tests", response_model=GenerateTestsResponse)
def generate_tests(req: GenerateTestsRequest) -> GenerateTestsResponse:
    result = run_workflow(
        repo_path=req.repo_path,
        diff=req.diff,
        run_eval=req.run_eval,
        auto_venv=req.auto_venv,
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
