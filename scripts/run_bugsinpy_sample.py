#!/usr/bin/env python3
"""用 BugsInPy 的一条 bug 驱动 mutiagent 工作流（需已 clone BugsInPy 并完成 checkout）。"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_checkout(bugsinpy_root: Path, project: str, bug_id: int, workspace: Path) -> Path:
    project_dir = workspace / project
    if project_dir.is_dir() and (project_dir / ".git").is_dir():
        return project_dir.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    bin_dir = bugsinpy_root / "framework" / "bin"
    if not (bin_dir / "bugsinpy-checkout").is_file():
        print(f"未找到 bugsinpy-checkout: {bin_dir}", file=sys.stderr)
        sys.exit(1)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    cmd = [
        str(bin_dir / "bugsinpy-checkout"),
        "-p",
        project,
        "-v",
        "0",
        "-i",
        str(bug_id),
        "-w",
        str(workspace.resolve()),
    ]
    print("运行:", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, env=env, cwd=str(bugsinpy_root))
    if r.returncode != 0:
        sys.exit(r.returncode)
    return project_dir.resolve()


def main() -> None:
    p = argparse.ArgumentParser(description="BugsInPy 样本 + mutiagent run_workflow")
    p.add_argument("--project", default="httpie")
    p.add_argument("--bug-id", type=int, default=1)
    p.add_argument(
        "--bugsinpy",
        type=Path,
        default=_repo_root() / "external" / "BugsInPy",
        help="BugsInPy 仓库根目录",
    )
    p.add_argument(
        "--workspace",
        type=Path,
        default=_repo_root() / ".mutiagent" / "bugsinpy_workspace",
        help="checkout 工作目录（与 bugsinpy-checkout -w 一致）",
    )
    p.add_argument("--run-eval", action="store_true", help="开启 pytest 执行（默认关闭以加快试跑）")
    p.add_argument(
        "--auto-venv",
        action="store_true",
        help="在仓库 .mutiagent/mutiagent_pytest_venv 自动创建 venv 并安装依赖后跑 pytest（与 API auto_venv 一致）",
    )
    p.add_argument("--skip-checkout", action="store_true", help="跳过 checkout（已存在工作副本时）")
    args = p.parse_args()

    root = _repo_root()
    bugsinpy = args.bugsinpy.resolve()
    patch_path = bugsinpy / "projects" / args.project / "bugs" / str(args.bug_id) / "bug_patch.txt"
    if not patch_path.is_file():
        print(f"找不到补丁文件: {patch_path}", file=sys.stderr)
        print("请先: git clone https://github.com/soarsmu/BugsInPy.git external/BugsInPy", file=sys.stderr)
        sys.exit(1)

    diff_text = patch_path.read_text(encoding="utf-8")
    workspace = args.workspace.resolve()

    if args.skip_checkout:
        repo_path = workspace / args.project
        if not (repo_path / ".git").is_dir():
            print(f"--skip-checkout 但目录无效: {repo_path}", file=sys.stderr)
            sys.exit(1)
    else:
        repo_path = _ensure_checkout(bugsinpy, args.project, args.bug_id, workspace)

    os.chdir(root)
    sys.path.insert(0, str(root / "src"))
    from mutiagent.graph.workflow import run_workflow

    print(f"repo_path={repo_path}", flush=True)
    print(f"patch={patch_path}", flush=True)
    out = run_workflow(
        repo_path=str(repo_path),
        diff=diff_text,
        run_eval=args.run_eval,
        auto_venv=args.auto_venv,
    )

    print("changed_files:", out.get("changed_files"))
    plan = out.get("test_plan") or {}
    if isinstance(plan, dict):
        print("test_plan.summary:", plan.get("summary"))
    gt = out.get("generated_tests") or []
    paths = []
    for item in gt:
        if hasattr(item, "path"):
            paths.append(item.path)
        elif isinstance(item, dict):
            paths.append(item.get("path"))
    print("generated_tests:", paths)
    dbg = out.get("debug") or {}
    if dbg:
        print("debug keys:", list(dbg.keys()))


if __name__ == "__main__":
    main()
