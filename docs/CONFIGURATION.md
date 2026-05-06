# mutiagent 配置参考

面向**协作者在本地跑通项目**的说明；安装与调用示例见仓库根目录 [README.md](../README.md)。

---

## 目录

1. [配置从哪来](#配置从哪来)
2. [布尔开关约定](#布尔开关约定)
3. [最小可运行清单](#最小可运行清单)
4. [LLM](#llm)
5. [被测仓库：venv 与依赖](#被测仓库venv-与依赖)
6. [pytest 执行与报告](#pytest-执行与报告)
7. [日志与 SQLite](#日志与-sqlite)
8. [实验落盘与扩展指标](#实验落盘与扩展指标)
9. [流水线节点开关](#流水线节点开关)
10. [Impact 分析调参](#impact-分析调参)
11. [CodeChangeAgent 缓存与精炼](#codechangeagent-缓存与精炼)
12. [与 HTTP 请求体的关系](#与-http-请求体的关系)
13. [环境变量索引（按名称）](#环境变量索引按名称)

---

## 配置从哪来

1. **Shell**：`export`/`set` 的变量优先生效。
2. **`.env` 文件**：在首次导入 `mutiagent.llm.openai_client` 时，会依次尝试读取：
   - 当前工作目录下的 `.env`
   - 仓库根目录下的 `.env`（`openai_client.py` 向上三级）
3. **规则**：`.env` 里只会**写入尚未出现在 `os.environ` 中的键**（已有环境变量不会被覆盖）。

部分选项也可在 API 请求体里覆盖（见下文）。

---

## 布尔开关约定

各变量实现略有差异，常见模式如下（以具体章节为准）：

| 模式 | 「关」常见取值 | 「开」常见取值 |
|------|----------------|----------------|
| `… not in {"0","false","no","off"}` | `0`、`false`、`no`、`off` | 默认或其它任意非关值 |
| `… in {"1","true","yes","on"}` | 其它或未设 | `1`、`true`、`yes`、`on` |

---

## 最小可运行清单

1. **Python 3.10+**，在仓库根：`pip install -e ".[eval]"`（评测/覆盖率能力）或 `pip install -e .`
2. 配置 **LLM**：`MUTIAGENT_LLM_PROVIDER` + 对应 **`OPENAI_API_KEY` / `DEEPSEEK_API_KEY` / `ZHIPU_API_KEY`** + `MUTIAGENT_LLM_MODEL`（推荐）
3. 启动：`uvicorn mutiagent.api.main:app --reload --port 8000` 或 `bash scripts/dev.sh`
4. 首次对被测仓库跑通时，默认会在其下创建 `.mutiagent/mutiagent_pytest_venv` 并安装依赖，**耗时可能较长**。

**Python 3.11 数据集**：创建/复用 venv 时会为 `anyio` 做约束（见 `MUTIAGENT_VENV_ANYIO_SPEC`）。若仍冲突，可收紧该变量后删除数据集下 `.mutiagent/mutiagent_pytest_venv` 再跑。

---

## LLM

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_LLM_PROVIDER` | `openai` | `openai` / `deepseek` / `zhipu`（未知值回退 `openai`） |
| `MUTIAGENT_LLM_MODEL` | 依 provider | 也可用旧变量 `MUTIAGENT_OPENAI_MODEL` 作回退 |
| `MUTIAGENT_LLM_BASE_URL` | 依 provider | 覆盖各厂商默认 Base URL |
| `OPENAI_API_KEY` | — | OpenAI 或兼容网关 |
| `DEEPSEEK_API_KEY` | — | DeepSeek（亦允许回退 `OPENAI_API_KEY`） |
| `ZHIPU_API_KEY` | — | 智谱（亦允许回退 `OPENAI_API_KEY`） |
| `MUTIAGENT_OPENAI_MODEL` | — | 兼容旧配置；在 `MUTIAGENT_LLM_MODEL` 未设时作为模型名 |
| `MUTIAGENT_DISABLE_LLM` | 关 | `1`/`true`/`yes`/`on`：禁用 LLM（规则降级、离线调试） |

Provider 默认模型与 Base URL 定义见 [`openai_client.py`](../src/mutiagent/llm/openai_client.py) 中 `_PROVIDER_CONFIGS`。

---

## 被测仓库：venv 与依赖

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_DISABLE_AUTO_VENV` | 关 | 与 `MUTIAGENT_NO_AUTO_VENV` **等价**：`1`/`true`/`yes`/`on` 关闭自动 venv |
| `MUTIAGENT_AUTO_VENV` | 关 | `1`/…：脚本等场景**强制**开启自动 venv（逻辑见 `venv_flags`） |
| `MUTIAGENT_PYTEST_PYTHON` | 空 | **绝对路径**的解释器：跳过自动 venv；**不会**替你 `pip install` 数据集依赖 |
| `MUTIAGENT_VENV_PYTHON` | 空 | 创建 `.mutiagent/mutiagent_pytest_venv` 时使用的解释器（如新项目需 3.12+） |
| `MUTIAGENT_VENV_INSTALL_TIMEOUT` | `900` | 数据集内 `pip install` 超时（秒） |
| `MUTIAGENT_VENV_ANYIO_SPEC` | `anyio>=4.0,<4.12` | **仅 Python < 3.12** 时 pin anyio，减轻与 pytest 栈的兼容性冲突 |
| `MUTIAGENT_VENV_AUTO_INSTALL_PYTHON` | 关 | `1`/…：缺的 declared Python 时尝试 conda 安装（见 `dataset_venv`） |
| `MUTIAGENT_INFER_PIP` | 开 | `0`/`false`/`no`/`off`：不写 `mutiagent_inferred_pip.txt`、不根据 import 推断 PyPI 包 |

venv 开关合并规则：[`venv_flags.py`](../src/mutiagent/utils/venv_flags.py)。

---

## pytest 执行与报告

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_PYTEST_COVERAGE` | 开 | `0`/`false`/`no`/`off`：不加 pytest-cov（评测侧覆盖率变弱） |
| `MUTIAGENT_DISABLE_TEST_REPORT` | 关 | `1`/`true`/`yes`/`on`：不写 `.mutiagent/reports/...` |
| `MUTIAGENT_PYTEST_APPEND_PYTHONPATH` | 关 | `1`/…：pytest 继承当前进程的 `PYTHONPATH`（特殊仓库如 Ansible 布局时按需） |
| `MUTIAGENT_EXEC_COLLECT_ALL_TESTS` | 开 | `0`/`false`/`no`/`off`：跳过全仓 `pytest --collect-only`（大仓提速；部分指标依赖收集结果） |
| `MUTIAGENT_COLLECT_TIMEOUT_S` | `300` | `--collect-only` 子进程超时（秒） |
| `MUTIAGENT_PYTEST_LOG_MAX_CHARS` | `60000` | 写入 `log/mutiagent.log` 的单段 pytest 输出上限 |
| `MUTIAGENT_EVAL_METRIC_SCOPE_TESTS` | 开 | `0`/`false`/`no`/`off`：评测侧**不**按 junit 关键词收窄「通过的」用例集合 |

---

## 日志与 SQLite

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_LOG_APPEND` | 关 | `1`/`true`/`yes`/`on`：API 首次配置日志时**不清空** `log/mutiagent.log` |
| `MUTIAGENT_DEBUG` | 关 | `1`/…：`CodeChangeAgent`、`ImpactAnalysisAgent` 等调试日志 |
| `MUTIAGENT_DB_ENABLED` | 开 | 未设或真值：启用 SQLite；`0`/`false`/`no`/`off`：关闭 |
| `MUTIAGENT_DB_PATH` | `log/mutiagent.sqlite3`（相对仓库根） | 自定义数据库路径 |

表结构说明见 [README.md](../README.md) 中 SQLite 小节。

---

## 实验落盘与扩展指标

### 全局日志与后处理

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_EXPERIMENT_RUN_LOG` | 开 | `0`/`false`/`no`/`off`：不向 `log/experiment_runs.json` 追加（单步目录里仍可有 `experiment_record.json`） |
| `MUTIAGENT_EXPERIMENT_COV` | 开 | `0`/`false`/`no`/`off`：跳过额外 coverage JSON 子进程 |

### 进程环境（影响 `extended_experiment_metrics`）

| 变量 | 说明 |
|------|------|
| `FAILING_TESTS` | 逗号分隔基准失败 nodeid；与 `selected_tests` 求交用于 bug detection。未设且 junit 有失败用例时可用 junit 回填 |
| `CHANGED_FUNCS` | `path/to.py:func` 或仅符号名，用于「新增/变更函数」类指标的分母与推断 |
| `CHANGED_FILES` | 逗号分隔相对路径，覆盖状态里的变更文件集合（影响跨模块等指标） |
| `MUTIAGENT_MEASURE_FULL_SUITE_TIME` | `1`/`true`/`yes`/`on`：无缓存时对**数据集仓库**跑完整 pytest，写入 `log/full_pytest_suite_time_cache.json`（**很慢**） |
| `MUTIAGENT_FULL_SUITE_PYTEST_ARGS` | 全量测耗时附加参数，`shlex.split` 分词 |
| `MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE` | `1`/…：无全量墙钟缓存时，用选中集耗时与收集规模**粗估**执行时间缩减比例 |

实现与注释见 [`extended_experiment_metrics.py`](../src/mutiagent/evaluation/extended_experiment_metrics.py)。

---

## 流水线节点开关

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_ENABLE_RETRIEVAL` | 开 | `0`/`false`/`off`/`no`：关闭 RetrievalAgent（请求体 `retrieval_enabled` 可覆盖） |
| `MUTIAGENT_ENABLE_BUG_PATTERN` | 开 | `0`/`false`/`off`/`no`：关闭 BugPatternAgent（请求体 `bug_pattern_enabled` 可覆盖） |
| `MUTIAGENT_TESTGEN_FAST` | 关 | `1`/…：快速模式（更短超时与上下文，见 `test_gen_agent`） |
| `MUTIAGENT_TESTGEN_TIMEOUT_S` | 快速 45s / 正常最小 120s | 显式数值时 `max(10, float)`；非法或未设回退 120 |
| `MUTIAGENT_TESTGEN_STATIC_GUARD` | 开 | `0`/`false`/`no`/`off`：关闭生成后静态嗅探日志 |
| `MUTIAGENT_TEST_REPAIR_SEMANTIC` | 开 | `0`/`false`/`no`/`off`：关闭 TestRepair 语义规则 |
| `MUTIAGENT_PRIORITIZATION_DROP_LOW` | 开 | 未设为默认真；`0`/`false`/`no`/`off` 关闭「丢弃低档」行为 |

---

## Impact 分析调参

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_IMPACT_TOP_N` | `15` | 影响候选数量上限 |
| `MUTIAGENT_IMPACT_LLM_REFINE` | 关 | `1`/…：LLM 精炼影响结果 |
| `MUTIAGENT_IMPACT_MAX_PROPAGATION_HOPS` | `3` | 传播跳数上限 |

---

## CodeChangeAgent 缓存与精炼

| 变量 | 默认 | 说明 |
|------|------|------|
| `MUTIAGENT_CODE_CHANGE_CACHE` | 开 | `0`/`false`/`no`/`off`：关闭按仓库的分析磁盘缓存 |
| `MUTIAGENT_CACHE_DIR` | 空 | 非空时缓存根为该目录下 `repo_<hash>`，而非 `repo/.mutiagent` |
| `MUTIAGENT_CODE_CHANGE_CACHE_MAX` | `2000` | 缓存条目上限（实际 `max(100, int(...))`） |
| `MUTIAGENT_LLM_REFINE_LINES_THRESHOLD` | `30` | 触发行级 LLM 精炼的阈值之一 |
| `MUTIAGENT_LLM_REFINE_WEAK_TAG_THRESHOLD` | `2` | 弱标签精炼阈值 |

`MUTIAGENT_DISABLE_LLM=1` 时缓存键会带上 `llm:disabled`，与正常 LLM 结果隔离。

---

## 与 HTTP 请求体的关系

- `auto_venv`、`auto_install_python`、`run_eval`、`retrieval_enabled`、`bug_pattern_enabled` 等字段定义见 [`GenerateTestsRequest`](../src/mutiagent/graph/state.py)。
- 自动 venv 的最终判定 = **请求体** + **环境变量**（`venv_flags`），环境与 README / API 首页说明一致。
- 内置 API 文档：`/docs`（FastAPI Swagger）。

---

## 环境变量索引（按名称）

| 名称 | 章节 |
|------|------|
| `CHANGED_FILES` | [实验落盘与扩展指标](#实验落盘与扩展指标) |
| `CHANGED_FUNCS` | 同上 |
| `DEEPSEEK_API_KEY` | [LLM](#llm) |
| `FAILING_TESTS` | [实验落盘与扩展指标](#实验落盘与扩展指标) |
| `MUTIAGENT_AUTO_VENV` | [被测仓库：venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_CACHE_DIR` | [CodeChangeAgent](#codechangeagent-缓存与精炼) |
| `MUTIAGENT_CODE_CHANGE_CACHE` | 同上 |
| `MUTIAGENT_CODE_CHANGE_CACHE_MAX` | 同上 |
| `MUTIAGENT_COLLECT_TIMEOUT_S` | [pytest](#pytest-执行与报告) |
| `MUTIAGENT_DB_ENABLED` | [日志与 SQLite](#日志与-sqlite) |
| `MUTIAGENT_DB_PATH` | 同上 |
| `MUTIAGENT_DEBUG` | 同上 |
| `MUTIAGENT_DISABLE_AUTO_VENV` | [venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_DISABLE_LLM` | [LLM](#llm) |
| `MUTIAGENT_DISABLE_TEST_REPORT` | [pytest](#pytest-执行与报告) |
| `MUTIAGENT_ENABLE_BUG_PATTERN` | [流水线](#流水线节点开关) |
| `MUTIAGENT_ENABLE_RETRIEVAL` | 同上 |
| `MUTIAGENT_EVAL_METRIC_SCOPE_TESTS` | [pytest](#pytest-执行与报告) |
| `MUTIAGENT_EXEC_COLLECT_ALL_TESTS` | 同上 |
| `MUTIAGENT_EXEC_TIME_REDUCTION_ESTIMATE` | [扩展指标](#实验落盘与扩展指标) |
| `MUTIAGENT_EXPERIMENT_COV` | 同上 |
| `MUTIAGENT_EXPERIMENT_RUN_LOG` | 同上 |
| `MUTIAGENT_FULL_SUITE_PYTEST_ARGS` | 同上 |
| `MUTIAGENT_IMPACT_LLM_REFINE` | [Impact](#impact-分析调参) |
| `MUTIAGENT_IMPACT_MAX_PROPAGATION_HOPS` | 同上 |
| `MUTIAGENT_IMPACT_TOP_N` | 同上 |
| `MUTIAGENT_INFER_PIP` | [venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_LLM_BASE_URL` | [LLM](#llm) |
| `MUTIAGENT_LLM_MODEL` | 同上 |
| `MUTIAGENT_LLM_PROVIDER` | 同上 |
| `MUTIAGENT_LLM_REFINE_LINES_THRESHOLD` | [CodeChangeAgent](#codechangeagent-缓存与精炼) |
| `MUTIAGENT_LLM_REFINE_WEAK_TAG_THRESHOLD` | 同上 |
| `MUTIAGENT_LOG_APPEND` | [日志与 SQLite](#日志与-sqlite) |
| `MUTIAGENT_MEASURE_FULL_SUITE_TIME` | [扩展指标](#实验落盘与扩展指标) |
| `MUTIAGENT_NO_AUTO_VENV` | [venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_OPENAI_MODEL` | [LLM](#llm) |
| `MUTIAGENT_PRIORITIZATION_DROP_LOW` | [流水线](#流水线节点开关) |
| `MUTIAGENT_PYTEST_APPEND_PYTHONPATH` | [pytest](#pytest-执行与报告) |
| `MUTIAGENT_PYTEST_COVERAGE` | 同上 |
| `MUTIAGENT_PYTEST_LOG_MAX_CHARS` | 同上 |
| `MUTIAGENT_PYTEST_PYTHON` | [venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_TESTGEN_FAST` | [流水线](#流水线节点开关) |
| `MUTIAGENT_TESTGEN_STATIC_GUARD` | 同上 |
| `MUTIAGENT_TESTGEN_TIMEOUT_S` | 同上 |
| `MUTIAGENT_TEST_REPAIR_SEMANTIC` | 同上 |
| `MUTIAGENT_VENV_ANYIO_SPEC` | [venv](#被测仓库venv-与依赖) |
| `MUTIAGENT_VENV_AUTO_INSTALL_PYTHON` | 同上 |
| `MUTIAGENT_VENV_INSTALL_TIMEOUT` | 同上 |
| `MUTIAGENT_VENV_PYTHON` | 同上 |
| `OPENAI_API_KEY` | [LLM](#llm) |
| `ZHIPU_API_KEY` | [LLM](#llm) |

以代码为准的自检命令（仓库根目录）：

```bash
rg "MUTIAGENT_[A-Z0-9_]+" src/mutiagent --glob '*.py'
```
