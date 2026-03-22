from __future__ import annotations

from mutiagent.graph.state import ChangeRecord, WorkflowState
from mutiagent.nodes import code_change_agent
from mutiagent.nodes.code_change_agent import extract_changed_entities, extract_impact_seeds, ingest_change


def test_ingest_change_builds_structured_change_analysis(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path
    app_file = repo_root / "app.py"
    app_file.write_text(
        "def process(value):\n"
        "    if value is None:\n"
        "        raise ValueError('value is required')\n"
        "    return value.strip()\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,4 @@\n"
        " def process(value):\n"
        "+    if value is None:\n"
        "+        raise ValueError('value is required')\n"
        "     return value.strip()\n"
    )

    state = WorkflowState(repo_path=str(repo_root), diff=diff)
    out = ingest_change(state)

    assert out.changed_files == ["app.py"]
    assert len(out.change_analysis) == 1
    assert out.change_analysis[0].file == "app.py"
    assert len(out.change_analysis[0].changes) == 1

    change = out.change_analysis[0].changes[0]
    assert change.entity == "process"
    assert change.type == "function"
    assert change.change_type == "MODIFY"
    assert "input_validation_added" in change.semantic_tags
    assert "null_check_added" in change.semantic_tags
    assert "invalid_input" in change.test_focus
    assert "null_safety" in change.test_focus
    assert change.intent == "BUG_FIX"
    assert any(seed.kind == "variable" and seed.name == "value" for seed in change.impact_seeds)
    assert out.change_graph is not None
    assert out.debug.get("change_graph", {}).get("node_count", 0) >= 1
    node_kinds = {n.kind for n in out.change_graph.nodes}
    assert "file" in node_kinds and "symbol" in node_kinds


def test_ingest_change_cache_second_run_hits(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MUTIAGENT_CACHE_DIR", str(tmp_path / "shared_cache"))
    monkeypatch.setenv("MUTIAGENT_CODE_CHANGE_CACHE", "1")
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    app_file = repo_root / "app.py"
    app_file.write_text("def f():\n    return 1\n", encoding="utf-8")
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,3 @@\n"
        " def f():\n"
        "+    x = 1\n"
        "     return 1\n"
    )
    state = WorkflowState(repo_path=str(repo_root), diff=diff)
    out1 = ingest_change(state)
    assert out1.debug["code_change"]["cache_misses"] >= 1
    assert out1.debug["code_change"]["cache_writes"] >= 1
    assert out1.debug["code_change"]["cache_hits"] == 0

    out2 = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))
    assert out2.debug["code_change"]["cache_hits"] >= 1
    assert out2.debug["code_change"]["cache_misses"] == 0
    assert out2.change_analysis == out1.change_analysis


def test_ingest_change_drops_ignored_paths(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path
    main_file = repo_root / "src" / "main.py"
    main_file.parent.mkdir(parents=True)
    main_file.write_text("def main():\n    return None\n", encoding="utf-8")
    diff = (
        "--- a/dist/x.js\n"
        "+++ b/dist/x.js\n"
        "@@ -1 +1 @@\n"
        "-1\n"
        "+2\n"
        "--- a/src/main.py\n"
        "+++ b/src/main.py\n"
        "@@ -1,2 +1,3 @@\n"
        " def main():\n"
        "+    x = 1\n"
        "     return None\n"
    )
    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))
    assert out.changed_files == ["src/main.py"]
    assert len(out.change_analysis) == 1
    assert out.change_analysis[0].file == "src/main.py"


def test_extract_changed_entities_detects_added_class_and_method(tmp_path) -> None:
    repo_root = tmp_path
    app_file = repo_root / "service.py"
    app_file.write_text(
        "class Service:\n"
        "    def execute(self, payload):\n"
        "        return payload\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/service.py\n"
        "+++ b/service.py\n"
        "@@ -0,0 +1,3 @@\n"
        "+class Service:\n"
        "+    def execute(self, payload):\n"
        "+        return payload\n"
    )

    entities = extract_changed_entities(diff, repo_path=str(repo_root))
    service_changes = entities["service.py"]

    assert [item["entity"] for item in service_changes] == ["Service", "execute"]
    assert all(item["change_type"] == "ADD" for item in service_changes)
    assert [item["type"] for item in service_changes] == ["class", "method"]


def test_ingest_change_extracts_jsx_entities(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path
    src_dir = repo_root / "src"
    src_dir.mkdir()
    app_file = src_dir / "App.jsx"
    app_file.write_text(
        "export default function App() {\n"
        "  const handleSubmit = (value) => {\n"
        "    if (!value) {\n"
        "      throw new Error('value required')\n"
        "    }\n"
        "    return value.trim()\n"
        "  }\n"
        "\n"
        "  return <main>{handleSubmit('ok')}</main>\n"
        "}\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/src/App.jsx\n"
        "+++ b/src/App.jsx\n"
        "@@ -1,4 +1,10 @@\n"
        " export default function App() {\n"
        "+  const handleSubmit = (value) => {\n"
        "+    if (!value) {\n"
        "+      throw new Error('value required')\n"
        "+    }\n"
        "+    return value.trim()\n"
        "+  }\n"
        " \n"
        "-  return <main>Hello</main>\n"
        "+  return <main>{handleSubmit('ok')}</main>\n"
        " }\n"
    )

    state = WorkflowState(repo_path=str(repo_root), diff=diff)
    out = ingest_change(state)

    assert out.changed_files == ["src/App.jsx"]
    assert len(out.change_analysis) == 1
    assert out.change_analysis[0].file == "src/App.jsx"
    assert out.change_analysis[0].changes

    entities = {change.entity: change for change in out.change_analysis[0].changes}
    assert "App" in entities
    assert "handleSubmit" in entities
    assert "input_validation_added" in entities["handleSubmit"].semantic_tags
    assert "logic_branch_changed" in entities["handleSubmit"].semantic_tags
    assert entities["handleSubmit"].intent == "BUG_FIX"


def test_ingest_change_extracts_java_entities(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path
    src_dir = repo_root / "src"
    src_dir.mkdir()
    service_file = src_dir / "Service.java"
    service_file.write_text(
        "public class Service {\n"
        "    public int add(Integer a, Integer b) {\n"
        "        if (a == null || b == null) {\n"
        "            throw new IllegalArgumentException(\"inputs required\");\n"
        "        }\n"
        "        return a + b;\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/src/Service.java\n"
        "+++ b/src/Service.java\n"
        "@@ -1,5 +1,8 @@\n"
        " public class Service {\n"
        "     public int add(Integer a, Integer b) {\n"
        "+        if (a == null || b == null) {\n"
        "+            throw new IllegalArgumentException(\"inputs required\");\n"
        "+        }\n"
        "         return a + b;\n"
        "     }\n"
        " }\n"
    )

    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))

    entities = {change.entity: change for change in out.change_analysis[0].changes}
    assert "Service" in entities
    assert "add" in entities
    assert entities["add"].type == "method"
    assert "input_validation_added" in entities["add"].semantic_tags
    assert "null_check_added" in entities["add"].semantic_tags
    assert entities["add"].intent == "BUG_FIX"


def test_ingest_change_extracts_cpp_entities(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: False)
    repo_root = tmp_path
    src_dir = repo_root / "src"
    src_dir.mkdir()
    cpp_file = src_dir / "math.cpp"
    cpp_file.write_text(
        "class Math {\n"
        "public:\n"
        "    int add(int* a, int* b) {\n"
        "        if (a == nullptr || b == nullptr) {\n"
        "            throw std::runtime_error(\"inputs required\");\n"
        "        }\n"
        "        return *a + *b;\n"
        "    }\n"
        "};\n"
        "\n"
        "int main() { return 0; }\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/src/math.cpp\n"
        "+++ b/src/math.cpp\n"
        "@@ -1,7 +1,10 @@\n"
        " class Math {\n"
        " public:\n"
        "     int add(int* a, int* b) {\n"
        "+        if (a == nullptr || b == nullptr) {\n"
        "+            throw std::runtime_error(\"inputs required\");\n"
        "+        }\n"
        "         return *a + *b;\n"
        "     }\n"
        " };\n"
        " \n"
    )

    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))

    entities = {change.entity: change for change in out.change_analysis[0].changes}
    assert "Math" in entities
    assert "add" in entities
    assert entities["add"].type == "method"
    assert "null_check_added" in entities["add"].semantic_tags
    assert entities["add"].intent == "BUG_FIX"


def test_llm_refine_skipped_for_small_low_risk_change(tmp_path, monkeypatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: True)

    def fake_chat_json(*_a, **_k) -> dict:
        calls.append(1)
        return {"changes": []}

    monkeypatch.setattr(code_change_agent, "chat_json", fake_chat_json)

    repo_root = tmp_path
    app_file = repo_root / "app.py"
    app_file.write_text("def foo():\n    return 1\n", encoding="utf-8")
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,3 @@\n"
        " def foo():\n"
        "+    # note\n"
        "     return 1\n"
    )

    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))

    assert calls == []
    assert out.debug["code_change"]["llm_refine_files_skipped"] == 1
    assert out.debug["code_change"]["llm_refine_files_invoked"] == 0


def test_llm_refine_invoked_when_diff_exceeds_line_threshold(tmp_path, monkeypatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: True)

    def fake_chat_json(*_a, **_k) -> dict:
        calls.append(1)
        return {"changes": []}

    monkeypatch.setattr(code_change_agent, "chat_json", fake_chat_json)

    repo_root = tmp_path
    app_file = repo_root / "app.py"
    app_file.write_text("def foo():\n    return 1\n", encoding="utf-8")
    filler = "\n".join(f"+    # pad {i}" for i in range(31))
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,33 @@\n"
        " def foo():\n"
        f"{filler}\n"
        "     return 1\n"
    )

    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))

    assert len(calls) == 1
    assert out.debug["code_change"]["llm_refine_files_invoked"] == 1
    assert out.debug["code_change"]["llm_refine_files_skipped"] == 0


def test_llm_refine_invoked_for_logic_branch_tag(tmp_path, monkeypatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(code_change_agent, "llm_available", lambda: True)

    def fake_chat_json(*_a, **_k) -> dict:
        calls.append(1)
        return {"changes": []}

    monkeypatch.setattr(code_change_agent, "chat_json", fake_chat_json)

    repo_root = tmp_path
    app_file = repo_root / "app.py"
    app_file.write_text(
        "def foo(x):\n"
        "    return x\n",
        encoding="utf-8",
    )
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,4 @@\n"
        " def foo(x):\n"
        "+    if x < 0:\n"
        "+        return 0\n"
        "     return x\n"
    )

    out = ingest_change(WorkflowState(repo_path=str(repo_root), diff=diff))

    assert len(calls) == 1
    assert out.debug["code_change"]["llm_refine_files_invoked"] == 1


def test_extract_impact_seeds_denoises_jsx_but_keeps_components_routes_handlers() -> None:
    jsx = (
        "export default function Home() {\n"
        "  return (\n"
        "    <PageLayout>\n"
        "      <Link to=\"/x\" />\n"
        "      {items.map((id) => <ProjectCard onDone={handleSave} />)}\n"
        "    </PageLayout>\n"
        "  );\n"
        "}\n"
    )
    entity = {"diff_text": jsx, "code_context": "", "language": "javascript"}
    seeds = extract_impact_seeds(entity)
    names = {s.name for s in seeds}
    assert "map" not in names
    assert "return" not in names
    assert "items" not in names
    assert "PageLayout" in names
    assert "Link" in names
    assert "ProjectCard" in names
    assert "handleSave" in names
    assert "Home" in names


def test_change_requires_llm_refine_single_weak_tag_does_not_trigger() -> None:
    c = ChangeRecord(
        entity="About",
        type="function",
        change_type="MODIFY",
        semantic_tags=["dependency_call_changed"],
    )
    assert not code_change_agent.change_requires_llm_refine(c, "+foo()\n")


def test_change_requires_llm_refine_two_weak_tags_triggers() -> None:
    c = ChangeRecord(
        entity="Blog",
        type="function",
        change_type="MODIFY",
        semantic_tags=["dependency_call_changed", "return_value_changed"],
    )
    assert code_change_agent.change_requires_llm_refine(c, "+a()\n+b\n")


def test_change_requires_llm_refine_strong_tag_triggers_alone() -> None:
    c = ChangeRecord(
        entity="X",
        type="function",
        change_type="MODIFY",
        semantic_tags=["logic_branch_changed"],
    )
    assert code_change_agent.change_requires_llm_refine(c, "+if x:\n")
