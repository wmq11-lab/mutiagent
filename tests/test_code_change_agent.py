from __future__ import annotations

from mutiagent.graph.state import WorkflowState
from mutiagent.nodes import code_change_agent
from mutiagent.nodes.code_change_agent import extract_changed_entities, ingest_change


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
    assert change.intent == "BUG_FIX"
    assert any(seed.kind == "variable" and seed.name == "value" for seed in change.impact_seeds)


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
