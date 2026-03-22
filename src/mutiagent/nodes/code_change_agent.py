from __future__ import annotations

import ast
import os
import re
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from unidiff import PatchSet

from mutiagent.graph.state import ChangeRecord, FileChangeSummary, ImpactSeed, WorkflowState
from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_json
from mutiagent.utils.diff import parse_unified_diff

try:
    from tree_sitter import Language, Parser
    import tree_sitter_cpp
    import tree_sitter_java
    import tree_sitter_javascript
    from tree_sitter_typescript import language_tsx, language_typescript
except ImportError:  # pragma: no cover - optional at runtime until deps are installed
    Language = None
    Parser = None
    tree_sitter_cpp = None
    tree_sitter_java = None
    tree_sitter_javascript = None
    language_tsx = None
    language_typescript = None

ALLOWED_SEMANTIC_TAGS = {
    "api_signature_changed",
    "dependency_call_changed",
    "exception_handling_changed",
    "input_validation_added",
    "logic_branch_changed",
    "null_check_added",
    "return_value_changed",
}
ALLOWED_INTENTS = {"BUG_FIX", "FEATURE", "REFACTOR"}
BUILTIN_NAMES = {"True", "False", "None", "self", "cls"}
SKIP_PATH_MARKERS = ("/dist/", "/build/", "/coverage/", "/node_modules/")
SUPPORTED_SOURCE_KINDS = {
    ".py": "python",
    ".java": "java",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
}


@dataclass
class EntityInfo:
    name: str
    qualified_name: str
    entity_type: str
    start_line: int
    end_line: int
    node: Any = None
    language: str = "python"


def _read_repo_source(repo_path: str, rel_path: str) -> str:
    if not repo_path or not rel_path:
        return ""
    try:
        return (Path(repo_path) / rel_path).read_text(encoding="utf-8")
    except Exception:
        return ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _log_file_path() -> Path:
    log_dir = _repo_root() / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "code_change_agent.log"


def _debug_enabled() -> bool:
    return os.getenv("MUTIAGENT_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _log_debug(message: str) -> None:
    if _debug_enabled():
        line = f"[CodeChangeAgent] {message}"
        print(line, file=sys.stderr, flush=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with _log_file_path().open("a", encoding="utf-8") as fp:
                fp.write(f"{timestamp} {line}\n")
        except Exception:
            pass


def _source_kind(rel_path: str) -> str | None:
    return SUPPORTED_SOURCE_KINDS.get(Path(rel_path).suffix.lower())


def _should_skip_path(rel_path: str) -> bool:
    normalized = "/" + rel_path.replace("\\", "/").lstrip("/")
    return any(marker in normalized for marker in SKIP_PATH_MARKERS)


def _should_analyze_file(rel_path: str) -> bool:
    return _source_kind(rel_path) is not None and not _should_skip_path(rel_path)


def _collect_ast_entities(source: str) -> list[EntityInfo]:
    if not source:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    entities: list[EntityInfo] = []
    class_stack: list[str] = []
    func_stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
            qualified = ".".join(class_stack + [node.name])
            entities.append(
                EntityInfo(
                    name=node.name,
                    qualified_name=qualified,
                    entity_type="class",
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    node=node,
                    language="python",
                )
            )
            class_stack.append(node.name)
            self.generic_visit(node)
            class_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            entity_type = "method" if class_stack else "function"
            qualified = ".".join(class_stack + func_stack + [node.name])
            entities.append(
                EntityInfo(
                    name=node.name,
                    qualified_name=qualified,
                    entity_type=entity_type,
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    node=node,
                    language="python",
                )
            )
            func_stack.append(node.name)
            self.generic_visit(node)
            func_stack.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
            entity_type = "method" if class_stack else "function"
            qualified = ".".join(class_stack + func_stack + [node.name])
            entities.append(
                EntityInfo(
                    name=node.name,
                    qualified_name=qualified,
                    entity_type=entity_type,
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    node=node,
                    language="python",
                )
            )
            func_stack.append(node.name)
            self.generic_visit(node)
            func_stack.pop()

    Visitor().visit(tree)
    return entities


@lru_cache(maxsize=8)
def _tree_sitter_language(source_kind: str) -> Language | None:
    if Language is None or Parser is None:
        return None
    if source_kind == "java" and tree_sitter_java is not None:
        return Language(tree_sitter_java.language())
    if source_kind == "cpp" and tree_sitter_cpp is not None:
        return Language(tree_sitter_cpp.language())
    if source_kind == "javascript" and tree_sitter_javascript is not None:
        return Language(tree_sitter_javascript.language())
    if source_kind == "typescript" and language_typescript is not None:
        return Language(language_typescript())
    if source_kind == "tsx" and language_tsx is not None:
        return Language(language_tsx())
    return None


def _node_text(source_bytes: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")


def _js_name_from_node(source_bytes: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    named_name = node.child_by_field_name("name")
    if named_name is not None:
        return _node_text(source_bytes, named_name)
    named_property = node.child_by_field_name("property")
    if named_property is not None:
        return _node_text(source_bytes, named_property)
    for child in getattr(node, "named_children", []):
        if child.type in {"identifier", "property_identifier", "type_identifier", "private_property_identifier"}:
            return _node_text(source_bytes, child)
    return ""


def _cpp_function_name(source_bytes: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    declarator = node.child_by_field_name("declarator") or node.child_by_field_name("name")
    if declarator is None:
        return ""
    current = declarator
    while current is not None:
        named_children = getattr(current, "named_children", [])
        if current.type in {
            "identifier",
            "field_identifier",
            "qualified_identifier",
            "destructor_name",
            "operator_name",
        }:
            return _node_text(source_bytes, current)
        for child in named_children:
            if child.type in {
                "identifier",
                "field_identifier",
                "qualified_identifier",
                "destructor_name",
                "operator_name",
            }:
                return _node_text(source_bytes, child)
        current = current.child_by_field_name("declarator")
    return ""


def _collect_tree_sitter_entities(source: str, source_kind: str) -> list[EntityInfo]:
    language = _tree_sitter_language(source_kind)
    if language is None:
        return []

    parser = Parser(language)
    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)
    entities: list[EntityInfo] = []

    def walk(node: Any, class_stack: list[str]) -> None:
        if source_kind == "java":
            if node.type == "class_declaration":
                name = _js_name_from_node(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name])
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="class",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
                    body = node.child_by_field_name("body")
                    if body is not None:
                        for child in getattr(body, "named_children", []):
                            walk(child, class_stack + [name])
                    return

            if node.type == "method_declaration":
                name = _js_name_from_node(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name]) if class_stack else name
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="method" if class_stack else "function",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
                return

        if source_kind == "cpp":
            if node.type == "class_specifier":
                name = _js_name_from_node(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name])
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="class",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
                    body = node.child_by_field_name("body")
                    if body is not None:
                        for child in getattr(body, "named_children", []):
                            walk(child, class_stack + [name])
                    return

            if node.type == "function_definition":
                name = _cpp_function_name(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name]) if class_stack else name
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="method" if class_stack else "function",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
                return

        if node.type == "class_declaration":
            name = _js_name_from_node(source_bytes, node)
            if name:
                qualified = ".".join(class_stack + [name])
                entities.append(
                    EntityInfo(
                        name=name,
                        qualified_name=qualified,
                        entity_type="class",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        node=node,
                        language=source_kind,
                    )
                )
                body = node.child_by_field_name("body")
                if body is not None:
                    for child in getattr(body, "named_children", []):
                        walk(child, class_stack + [name])
                return

        if node.type == "method_definition":
            name = _js_name_from_node(source_bytes, node)
            if name:
                qualified = ".".join(class_stack + [name]) if class_stack else name
                entities.append(
                    EntityInfo(
                        name=name,
                        qualified_name=qualified,
                        entity_type="method",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        node=node,
                        language=source_kind,
                    )
                )
            return

        if node.type == "field_definition":
            value_node = node.child_by_field_name("value")
            if value_node is not None and value_node.type in {"arrow_function", "function_expression"}:
                name = _js_name_from_node(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name]) if class_stack else name
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="method" if class_stack else "function",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
            return

        if node.type == "function_declaration":
            name = _js_name_from_node(source_bytes, node)
            if name:
                qualified = ".".join(class_stack + [name]) if class_stack else name
                entities.append(
                    EntityInfo(
                        name=name,
                        qualified_name=qualified,
                        entity_type="method" if class_stack else "function",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        node=node,
                        language=source_kind,
                    )
                )

        if node.type == "variable_declarator":
            value_node = node.child_by_field_name("value")
            if value_node is not None and value_node.type in {"arrow_function", "function_expression"}:
                name = _js_name_from_node(source_bytes, node)
                if name:
                    qualified = ".".join(class_stack + [name]) if class_stack else name
                    entities.append(
                        EntityInfo(
                            name=name,
                            qualified_name=qualified,
                            entity_type="function",
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            node=node,
                            language=source_kind,
                        )
                    )
                return

        for child in getattr(node, "named_children", []):
            walk(child, class_stack)

    walk(tree.root_node, [])
    return entities


def _collect_entities(source: str, rel_path: str) -> list[EntityInfo]:
    source_kind = _source_kind(rel_path)
    if source_kind == "python":
        return _collect_ast_entities(source)
    if source_kind in {"javascript", "typescript", "tsx", "java", "cpp"}:
        return _collect_tree_sitter_entities(source, source_kind)
    return []


def _line_range(start: int, length: int) -> tuple[int, int]:
    safe_start = max(1, int(start or 1))
    safe_length = max(1, int(length or 1))
    return safe_start, safe_start + safe_length - 1


def _ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def _match_entities_to_range(entities: list[EntityInfo], start: int, length: int) -> list[EntityInfo]:
    hit_range = _line_range(start, length)
    hits = [e for e in entities if _ranges_overlap(hit_range, (e.start_line, e.end_line))]
    hits.sort(key=lambda e: (e.start_line, e.end_line - e.start_line, e.qualified_name))
    return hits


def _infer_hunk_change_type(hunk: Any) -> str:
    added = sum(1 for line in hunk if line.is_added)
    removed = sum(1 for line in hunk if line.is_removed)
    if added and removed:
        return "MODIFY"
    if added:
        return "ADD"
    if removed:
        return "DELETE"
    return "MODIFY"


def _python_definition_from_line(line: str, line_no: int) -> EntityInfo | None:
    match = re.match(r"^(\s*)(async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", line)
    if not match:
        return None
    indent, keyword, name = match.groups()
    if keyword == "class":
        entity_type = "class"
    elif indent:
        entity_type = "method"
    else:
        entity_type = "function"
    return EntityInfo(
        name=name,
        qualified_name=name,
        entity_type=entity_type,
        start_line=line_no,
        end_line=line_no,
        node=None,
        language="python",
    )


def _js_definition_from_line(line: str, line_no: int, source_kind: str) -> EntityInfo | None:
    class_match = re.match(r"^\s*(?:export\s+default\s+|export\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)", line)
    if class_match:
        name = class_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="class",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language=source_kind,
        )

    func_match = re.match(r"^\s*(?:export\s+default\s+|export\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)", line)
    if func_match:
        name = func_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="function",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language=source_kind,
        )

    variable_match = re.match(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s*:\s*[^=]+)?\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_][A-Za-z0-9_]*\s*=>)",
        line,
    )
    if variable_match:
        name = variable_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="function",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language=source_kind,
        )

    method_match = re.match(
        r"^\s*(?:static\s+)?(?:async\s+)?(?:get\s+|set\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        line,
    )
    if method_match and line.startswith((" ", "\t")):
        name = method_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="method",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language=source_kind,
        )

    return None


def _java_definition_from_line(line: str, line_no: int) -> EntityInfo | None:
    class_match = re.match(
        r"^\s*(?:public|private|protected|abstract|final|static|\s)*class\s+([A-Za-z_][A-Za-z0-9_]*)",
        line,
    )
    if class_match:
        name = class_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="class",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language="java",
        )

    method_match = re.match(
        r"^\s*(?:public|private|protected|static|final|abstract|synchronized|native|\s)+"
        r"[\w<>\[\], ?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        line,
    )
    if method_match:
        name = method_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="method",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language="java",
        )
    return None


def _cpp_definition_from_line(line: str, line_no: int) -> EntityInfo | None:
    class_match = re.match(r"^\s*(?:template\s*<[^>]+>\s*)?(?:class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)", line)
    if class_match:
        name = class_match.group(1)
        return EntityInfo(
            name=name,
            qualified_name=name,
            entity_type="class",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language="cpp",
        )

    if line.lstrip().startswith(("public:", "private:", "protected:")):
        return None

    func_match = re.match(
        r"^\s*(?:inline\s+|static\s+|virtual\s+|constexpr\s+|friend\s+|explicit\s+|typename\s+)*"
        r"[\w:<>,~*&\s]+\s+([A-Za-z_~][A-Za-z0-9_:~]*)\s*\(",
        line,
    )
    if func_match:
        raw_name = func_match.group(1).split("::")[-1]
        return EntityInfo(
            name=raw_name,
            qualified_name=raw_name,
            entity_type="method" if line.startswith((" ", "\t")) else "function",
            start_line=line_no,
            end_line=line_no,
            node=None,
            language="cpp",
        )
    return None


def _definition_from_line(line: str, line_no: int, rel_path: str) -> EntityInfo | None:
    source_kind = _source_kind(rel_path)
    if source_kind == "python":
        return _python_definition_from_line(line, line_no)
    if source_kind == "java":
        return _java_definition_from_line(line, line_no)
    if source_kind == "cpp":
        return _cpp_definition_from_line(line, line_no)
    if source_kind in {"javascript", "typescript", "tsx"}:
        return _js_definition_from_line(line, line_no, source_kind)
    return None


def _extract_deleted_entities(patched_file: Any, rel_path: str) -> list[EntityInfo]:
    deleted: list[EntityInfo] = []
    for hunk in patched_file:
        source_line = int(hunk.source_start or 1)
        for line in hunk:
            if line.is_removed:
                entity = _definition_from_line(line.value.rstrip("\n"), source_line, rel_path)
                if entity:
                    deleted.append(entity)
                source_line += 1
            elif line.is_context:
                source_line += 1
    return deleted


def _extract_inline_entities_from_hunk(hunk: Any, change_type: str, rel_path: str) -> list[EntityInfo]:
    entities: list[EntityInfo] = []
    source_line = int(hunk.source_start or 1)
    target_line = int(hunk.target_start or 1)
    for line in hunk:
        if line.is_removed:
            if change_type in {"DELETE", "MODIFY"}:
                entity = _definition_from_line(line.value.rstrip("\n"), source_line, rel_path)
                if entity:
                    entities.append(entity)
            source_line += 1
        elif line.is_added:
            if change_type in {"ADD", "MODIFY"}:
                entity = _definition_from_line(line.value.rstrip("\n"), target_line, rel_path)
                if entity:
                    entities.append(entity)
            target_line += 1
        else:
            source_line += 1
            target_line += 1
    return entities


def _merge_change_type(left: str, right: str) -> str:
    if left == right:
        return left
    if "MODIFY" in {left, right}:
        return "MODIFY"
    if {left, right} == {"ADD", "DELETE"}:
        return "MODIFY"
    return right


def _resolve_entity_change_type(base_change_type: str, entity: EntityInfo, inline_hits: list[EntityInfo]) -> str:
    if base_change_type != "ADD":
        return base_change_type
    inline_keys = {(item.name, item.entity_type) for item in inline_hits}
    if (entity.name, entity.entity_type) in inline_keys:
        return "ADD"
    return "MODIFY"


def _hunk_to_text(hunk: Any) -> str:
    lines: list[str] = []
    for line in hunk:
        prefix = "+"
        if line.is_removed:
            prefix = "-"
        elif line.is_context:
            prefix = " "
        lines.append(prefix + line.value.rstrip("\n"))
    return "\n".join(lines)


def _entity_context(source: str, entity: EntityInfo | None) -> str:
    if not source or entity is None:
        return ""
    lines = source.splitlines()
    start = max(1, entity.start_line - 3)
    end = min(len(lines), entity.end_line + 3)
    return "\n".join(lines[start - 1 : end])


def extract_changed_entities(diff: str, repo_path: str = "") -> dict[str, list[dict[str, Any]]]:
    patch = PatchSet(diff.splitlines(True))
    result: dict[str, list[dict[str, Any]]] = {}

    for patched_file in patch:
        rel_path = patched_file.path
        if not rel_path:
            continue

        if not _should_analyze_file(rel_path):
            result[rel_path] = []
            continue

        source = _read_repo_source(repo_path, rel_path)
        ast_entities = _collect_entities(source, rel_path)
        deleted_entities = _extract_deleted_entities(patched_file, rel_path)
        entity_map: dict[str, dict[str, Any]] = {}

        for hunk in patched_file:
            change_type = _infer_hunk_change_type(hunk)
            current_hits = _match_entities_to_range(ast_entities, hunk.target_start, hunk.target_length)
            deleted_hits = _match_entities_to_range(deleted_entities, hunk.source_start, hunk.source_length)
            inline_hits = _extract_inline_entities_from_hunk(hunk, change_type, rel_path)

            selected = list(current_hits)
            if change_type == "DELETE":
                selected = list(deleted_hits)
            if not selected:
                selected = list(inline_hits or deleted_hits)

            hunk_text = _hunk_to_text(hunk)
            for entity in selected:
                key = entity.qualified_name or entity.name
                entity_change_type = _resolve_entity_change_type(change_type, entity, inline_hits)
                if key not in entity_map:
                    entity_map[key] = {
                        "entity": entity.name,
                        "qualified_name": entity.qualified_name,
                        "type": entity.entity_type,
                        "change_type": entity_change_type,
                        "start_line": entity.start_line,
                        "end_line": entity.end_line,
                        "node": entity.node,
                        "language": entity.language,
                        "code_context": _entity_context(source, entity),
                        "diff_texts": [hunk_text],
                    }
                else:
                    item = entity_map[key]
                    item["change_type"] = _merge_change_type(item["change_type"], entity_change_type)
                    item["start_line"] = min(int(item["start_line"]), entity.start_line)
                    item["end_line"] = max(int(item["end_line"]), entity.end_line)
                    item["diff_texts"].append(hunk_text)

        ordered = sorted(entity_map.values(), key=lambda item: (int(item["start_line"]), item["entity"]))
        result[rel_path] = ordered

    return result


def infer_semantic_tags(diff: str, code_context: str) -> list[str]:
    added_lines = [
        line[1:].strip()
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    removed_lines = [
        line[1:].strip()
        for line in diff.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]
    changed_lines = [line for line in added_lines + removed_lines if line]
    tags: set[str] = set()

    if any(
        re.search(
            r"\bis\s+None\b|\b==\s*None\b|\b!=\s*None\b|\b===?\s*null\b|\b!==?\s*null\b|"
            r"\bundefined\b|\bnullptr\b|\bnull\b",
            line,
        )
        for line in added_lines
    ):
        tags.add("null_check_added")

    if any(
        re.search(
            r"\bisinstance\s*\(|\bassert\b|\braise\s+(ValueError|TypeError|AssertionError)\b|"
            r"\bthrow\s+new\s+(Error|TypeError|RangeError|IllegalArgumentException|RuntimeException)\b|"
            r"\bif\s*\(\s*!\w+",
            line,
        )
        for line in added_lines
    ):
        tags.add("input_validation_added")

    if any(
        re.match(r"^(if |elif |else:|match |case |for |while |if\s*\(|switch\s*\()", line)
        for line in changed_lines
    ):
        tags.add("logic_branch_changed")

    if any(re.match(r"^(try:|except |except:|raise |try\s*\{|catch\s*\(|throw\b)", line) for line in changed_lines):
        tags.add("exception_handling_changed")

    if any(re.match(r"^(return\b|=>)", line) for line in changed_lines):
        tags.add("return_value_changed")

    if any(
        re.match(
            r"^(def |async def |class |export\s+default\s+function|export\s+function|function |"
            r"export\s+class|class |(?:const|let|var)\s+\w+)",
            line,
        )
        for line in changed_lines
    ):
        tags.add("api_signature_changed")

    if any(re.search(r"[A-Za-z_][A-Za-z0-9_\.]*\s*\(", line) for line in changed_lines):
        tags.add("dependency_call_changed")

    if "except" in code_context and "raise" in code_context and "exception_handling_changed" not in tags:
        tags.add("exception_handling_changed")

    return sorted(tag for tag in tags if tag in ALLOWED_SEMANTIC_TAGS)


def classify_change_intent(semantic_tags: list[str], change_type: str = "MODIFY") -> str:
    tags = set(semantic_tags)
    if tags & {"input_validation_added", "null_check_added", "exception_handling_changed", "return_value_changed"}:
        return "BUG_FIX"
    if change_type == "ADD":
        return "FEATURE"
    if "logic_branch_changed" in tags and "api_signature_changed" in tags:
        return "FEATURE"
    if tags <= {"dependency_call_changed", "api_signature_changed"}:
        return "REFACTOR"
    if "logic_branch_changed" in tags:
        return "BUG_FIX"
    return "REFACTOR"


def _seed_from_call(node: ast.AST) -> ImpactSeed | None:
    if isinstance(node, ast.Name):
        return ImpactSeed(kind="function", name=node.id, source="ast")
    if isinstance(node, ast.Attribute):
        return ImpactSeed(kind="dependency", name=node.attr, source="ast")
    return None


def _regex_impact_seeds_from_text(text: str, source: str) -> list[ImpactSeed]:
    seeds: dict[tuple[str, str], ImpactSeed] = {}

    def add_seed(seed: ImpactSeed | None) -> None:
        if seed is None or not seed.name or seed.name in BUILTIN_NAMES:
            return
        seeds[(seed.kind, seed.name)] = seed

    for params in re.findall(r"\(([^)]*)\)\s*(?:=>|\{)", text):
        for name in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", params):
            add_seed(ImpactSeed(kind="variable", name=name, source=source))  # type: ignore[arg-type]

    for name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        add_seed(ImpactSeed(kind="function", name=name, source=source))  # type: ignore[arg-type]

    for _, name in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        add_seed(ImpactSeed(kind="dependency", name=name, source=source))  # type: ignore[arg-type]

    for name in re.findall(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        add_seed(ImpactSeed(kind="variable", name=name, source=source))  # type: ignore[arg-type]

    return [seeds[key] for key in sorted(seeds)[:12]]


def extract_impact_seeds(entity: Any) -> list[ImpactSeed]:
    node = entity.get("node") if isinstance(entity, dict) else getattr(entity, "node", None)
    diff_text = entity.get("diff_text", "") if isinstance(entity, dict) else ""
    code_context = entity.get("code_context", "") if isinstance(entity, dict) else ""
    language = entity.get("language", "python") if isinstance(entity, dict) else getattr(entity, "language", "python")
    seeds: dict[tuple[str, str], ImpactSeed] = {}

    def add_seed(seed: ImpactSeed | None) -> None:
        if seed is None or not seed.name or seed.name in BUILTIN_NAMES:
            return
        seeds[(seed.kind, seed.name)] = seed

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = list(node.args.args) + list(node.args.kwonlyargs)
        if node.args.vararg:
            args.append(node.args.vararg)
        if node.args.kwarg:
            args.append(node.args.kwarg)
        for arg in args:
            add_seed(ImpactSeed(kind="variable", name=arg.arg, source="ast"))

    if isinstance(node, ast.ClassDef):
        for base in node.bases:
            if isinstance(base, ast.Name):
                add_seed(ImpactSeed(kind="dependency", name=base.id, source="ast"))
            elif isinstance(base, ast.Attribute):
                add_seed(ImpactSeed(kind="dependency", name=base.attr, source="ast"))

    if isinstance(node, ast.AST):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                add_seed(_seed_from_call(child.func))
            elif isinstance(child, ast.Name) and child.id not in BUILTIN_NAMES:
                add_seed(ImpactSeed(kind="variable", name=child.id, source="ast"))

    if language in {"javascript", "typescript", "tsx"}:
        text = code_context or diff_text
        for seed in _regex_impact_seeds_from_text(text, "diff"):
            add_seed(seed)

    if not seeds and diff_text:
        for name in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", diff_text):
            add_seed(ImpactSeed(kind="function", name=name, source="diff"))
        for name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", diff_text):
            if name not in BUILTIN_NAMES and not name.isupper():
                add_seed(ImpactSeed(kind="variable", name=name, source="diff"))
            if len(seeds) >= 12:
                break

    return [seeds[key] for key in sorted(seeds)[:12]]


def _llm_refine_change_summary(file_path: str, file_diff: str, source: str, summary: FileChangeSummary) -> FileChangeSummary:
    if not llm_available() or not summary.changes:
        if summary.changes:
            _log_debug(f"skip llm refine for {file_path}: llm unavailable")
        return summary

    system = (
        "你是代码变更语义分析器。你只能基于输入中的已有变更实体补充 semantic_tags 与 intent。"
        "不要新增实体，不要修改 change_type/type。"
        "semantic_tags 只能从以下集合中选择："
        f"{sorted(ALLOWED_SEMANTIC_TAGS)}。"
        "intent 只能是 BUG_FIX / FEATURE / REFACTOR。"
        "输出 JSON：{\"changes\": [{\"entity\": \"...\", \"semantic_tags\": [...], \"intent\": \"...\"}]}"
    )
    payload = {
        "file": file_path,
        "changes": [
            {
                "entity": change.entity,
                "type": change.type,
                "change_type": change.change_type,
                "semantic_tags": change.semantic_tags,
                "intent": change.intent,
            }
            for change in summary.changes
        ],
        "diff": file_diff[:4000],
        "code_context": source[:4000],
    }

    _log_debug(f"llm refine start: {file_path} ({len(summary.changes)} changes)")
    started_at = time.perf_counter()
    try:
        resp = chat_json(system, f"输入如下（JSON）：\n{payload}\n\n请输出JSON。", temperature=0.0)
    except Exception as exc:
        _log_debug(f"llm refine failed: {file_path} ({type(exc).__name__}: {exc})")
        return summary
    elapsed = time.perf_counter() - started_at
    _log_debug(f"llm refine done: {file_path} ({elapsed:.2f}s)")

    llm_items = {item.get("entity"): item for item in resp.get("changes", []) if isinstance(item, dict)}
    refined: list[ChangeRecord] = []
    for change in summary.changes:
        llm_item = llm_items.get(change.entity, {})
        llm_tags = [
            tag
            for tag in llm_item.get("semantic_tags", [])
            if isinstance(tag, str) and tag in ALLOWED_SEMANTIC_TAGS
        ]
        merged_tags = sorted(set(change.semantic_tags) | set(llm_tags))
        llm_intent = llm_item.get("intent")
        intent = change.intent
        if isinstance(llm_intent, str) and llm_intent in ALLOWED_INTENTS:
            intent = llm_intent
        refined.append(
            ChangeRecord(
                entity=change.entity,
                type=change.type,
                change_type=change.change_type,
                semantic_tags=merged_tags,
                intent=intent,
                impact_seeds=change.impact_seeds,
            )
        )

    return FileChangeSummary(file=file_path, changes=refined)


def _build_file_diff_map(diff: str) -> dict[str, str]:
    patch = PatchSet(diff.splitlines(True))
    out: dict[str, str] = {}
    for patched_file in patch:
        rel_path = patched_file.path
        if not rel_path:
            continue
        parts: list[str] = []
        for hunk in patched_file:
            parts.append(
                f"@@ -{hunk.source_start},{hunk.source_length} +{hunk.target_start},{hunk.target_length} @@"
            )
            parts.append(_hunk_to_text(hunk))
        out[rel_path] = "\n".join(parts)
    return out


def _build_change_analysis(diff: str, repo_path: str) -> list[FileChangeSummary]:
    _log_debug("extract changed entities start")
    entities_by_file = extract_changed_entities(diff, repo_path=repo_path)
    _log_debug(f"extract changed entities done: {len(entities_by_file)} files")
    file_diffs = _build_file_diff_map(diff)
    out: list[FileChangeSummary] = []

    for rel_path in sorted(entities_by_file):
        _log_debug(f"analyzing file: {rel_path}")
        source = _read_repo_source(repo_path, rel_path)
        changes: list[ChangeRecord] = []
        for item in entities_by_file[rel_path]:
            merged_diff = "\n".join(item.pop("diff_texts", []))
            item["diff_text"] = merged_diff
            semantic_tags = infer_semantic_tags(merged_diff, item.get("code_context", ""))
            intent = classify_change_intent(semantic_tags, item.get("change_type", "MODIFY"))
            impact_seeds = extract_impact_seeds(item)
            changes.append(
                ChangeRecord(
                    entity=item["entity"],
                    type=item["type"],
                    change_type=item["change_type"],
                    semantic_tags=semantic_tags,
                    intent=intent,
                    impact_seeds=impact_seeds,
                )
            )

        summary = FileChangeSummary(file=rel_path, changes=changes)
        _log_debug(f"file summary before llm: {rel_path} ({len(changes)} changes)")
        summary = _llm_refine_change_summary(rel_path, file_diffs.get(rel_path, ""), source, summary)
        out.append(summary)
        _log_debug(f"file summary complete: {rel_path} ({len(summary.changes)} changes)")

    return out


def ingest_change(state: WorkflowState) -> WorkflowState:
    started_at = time.perf_counter()
    _log_debug(f"ingest start: repo={state.repo_path}")
    _log_debug("parse unified diff start")
    parsed = parse_unified_diff(state.diff)
    _log_debug(f"parse unified diff done: files={len(parsed['changed_files'])}")
    state.changed_files = parsed["changed_files"]
    state.diff_hunks = parsed["hunks_by_file"]
    state.change_analysis = _build_change_analysis(state.diff, state.repo_path)
    state.debug["diff_stats"] = parsed["stats"]
    state.debug["code_change"] = {
        "files_analyzed": len(state.change_analysis),
        "changes": sum(len(file_summary.changes) for file_summary in state.change_analysis),
        "used_llm": llm_available(),
        "elapsed_seconds": round(time.perf_counter() - started_at, 3),
    }
    _log_debug(
        "ingest done: "
        f"files_analyzed={len(state.change_analysis)} "
        f"changes={state.debug['code_change']['changes']} "
        f"elapsed={state.debug['code_change']['elapsed_seconds']}s"
    )
    return state

