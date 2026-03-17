from __future__ import annotations

import ast
from pathlib import Path

import networkx as nx

from mutiagent.graph.state import WorkflowState
from mutiagent.utils.repo_scan import iter_python_files


def _module_name(repo_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(repo_root).as_posix()
    if rel.endswith(".py"):
        rel = rel[:-3]
    if rel.endswith("/__init__"):
        rel = rel[: -len("/__init__")]
    return rel.replace("/", ".")


def build_code_graph(state: WorkflowState) -> WorkflowState:
    repo_root = Path(state.repo_path)
    files = iter_python_files(state.repo_path)

    module_dep = nx.DiGraph()
    call_graph = nx.DiGraph()

    mod_to_file: dict[str, str] = {}
    for fp in files:
        mod = _module_name(repo_root, fp)
        mod_to_file[mod] = str(fp)

    for fp in files:
        mod = _module_name(repo_root, fp)
        module_dep.add_node(mod)
        try:
            src = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_dep.add_edge(mod, alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_dep.add_edge(mod, node.module)

        func_stack: list[str] = []

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, n: ast.FunctionDef):  # noqa: N802
                func_stack.append(f"{mod}:{n.name}")
                self.generic_visit(n)
                func_stack.pop()

            def visit_AsyncFunctionDef(self, n: ast.AsyncFunctionDef):  # noqa: N802
                func_stack.append(f"{mod}:{n.name}")
                self.generic_visit(n)
                func_stack.pop()

            def visit_Call(self, n: ast.Call):  # noqa: N802
                if not func_stack:
                    return
                caller = func_stack[-1]
                callee = None
                if isinstance(n.func, ast.Name):
                    callee = f"{mod}:{n.func.id}"
                elif isinstance(n.func, ast.Attribute):
                    callee = f"{mod}:{n.func.attr}"
                if callee:
                    call_graph.add_edge(caller, callee)
                self.generic_visit(n)

        Visitor().visit(tree)

    state.module_graph = {
        "nodes": list(module_dep.nodes),
        "edges": [(u, v) for u, v in module_dep.edges],
        "mod_to_file": mod_to_file,
    }
    state.call_graph = {"nodes": list(call_graph.nodes), "edges": [(u, v) for u, v in call_graph.edges]}
    state.debug["graph_stats"] = {
        "modules": len(state.module_graph["nodes"]),
        "module_edges": len(state.module_graph["edges"]),
        "call_nodes": len(state.call_graph["nodes"]),
        "call_edges": len(state.call_graph["edges"]),
    }
    return state

