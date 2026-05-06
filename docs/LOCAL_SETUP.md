# 本地配置与运行（协作者）

按顺序执行即可在本机启动 API；**所有命令默认在已克隆的仓库根目录下**（下文记为 `mutiagent/`）。环境变量大全见 [CONFIGURATION.md](CONFIGURATION.md)。

---

## 1. 前置条件

- **Python 3.10+**（`python3 --version`）
- **Git**
- 可用的 **LLM API Key**（OpenAI / DeepSeek / 智谱等，与下面 `.env` 中 `MUTIAGENT_LLM_PROVIDER` 一致）

---

## 2. 获取代码并进入目录

```bash
git clone <你的仓库 URL> mutiagent
cd mutiagent
```

若已克隆，只需 `cd` 到该目录。

---

## 3. 创建隔离环境（二选一）

**方式 A：`venv`（推荐，与机器无关）**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
```

**方式 B：conda（与 README 中「mutiagent」环境一致时使用）**

```bash
conda activate mutiagent
```

---

## 4. 安装本项目

```bash
pip install -e ".[eval]"
```

若不需要本地跑 mutiagent 自带测试与 coverage，可改为：

```bash
pip install -e .
```

---

## 5. 配置 LLM（`.env`）

```bash
cp .env.example .env
```

用编辑器打开 `.env`，至少填写：

- `MUTIAGENT_LLM_PROVIDER`（`openai` / `deepseek` / `zhipu`）
- 对应 Key：`OPENAI_API_KEY` / `DEEPSEEK_API_KEY` / `ZHIPU_API_KEY`
- `MUTIAGENT_LLM_MODEL`（与厂商文档一致）

说明：导入 `mutiagent` 时会读 **当前工作目录** 或 **仓库根** 下的 `.env`，且**不会覆盖**已在 Shell 里 `export` 的变量。

---

## 6. 启动服务

**方式 A：直接 uvicorn**

```bash
cd /path/to/mutiagent
uvicorn mutiagent.api.main:app --reload --port 8000
```

**方式 B：开发脚本**（清空并轮转 `log/mutiagent.log` 的启动方式见脚本内容）

```bash
bash scripts/dev.sh
```

启动成功后本机接口基址一般为：`http://127.0.0.1:8000`。

---

## 7. 快速自检

浏览器打开交互文档：

```text
http://127.0.0.1:8000/docs
```

或用 **curl** 跑一次最小请求（把 `repo_path` 换成你本机存在的 Python 项目路径，`diff` 换成真实 diff 文本）：

```bash
curl -s http://127.0.0.1:8000/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/python/project",
    "diff": "diff --git a/foo.py b/foo.py\n--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new\n"
  }'
```

首次对被测仓库执行 pytest 时，默认可能在其下创建 `.mutiagent/mutiagent_pytest_venv` 并安装依赖，**等待较久属正常**。

---

## 8. 常见问题

| 现象 | 建议 |
|------|------|
| 提示缺 Key 或 401 | 检查 `.env` 与 `MUTIAGENT_LLM_PROVIDER` 是否一致；或是否在终端误用了空的 `export`。 |
| 端口被占用 | 换端口：`uvicorn mutiagent.api.main:app --reload --port 8001`。 |
| 只想用本机已有 venv 跑 pytest | 设置 `MUTIAGENT_PYTEST_PYTHON` 为该 venv 的 `python` **绝对路径**；详见 [CONFIGURATION.md](CONFIGURATION.md)。 |
| Python 3.11 下 pytest 一启动就报错（anyio/typing 等） | 看 [CONFIGURATION.md](CONFIGURATION.md) 中 `MUTIAGENT_VENV_ANYIO_SPEC`，必要时删被测仓库下 `.mutiagent/mutiagent_pytest_venv` 后重跑。 |
| 需要保留 `log/mutiagent.log` 历史 | 启动前设 `MUTIAGENT_LOG_APPEND=1`；`scripts/dev.sh` 已默认追加模式相关设置，具体以脚本为准。 |

---

## 9. 进一步

- 仅测 `CodeChangeAgent`：[README.md](../README.md) 中「直接测试 CodeChangeAgent」一节。
- 可调参数全集：[CONFIGURATION.md](CONFIGURATION.md)。
