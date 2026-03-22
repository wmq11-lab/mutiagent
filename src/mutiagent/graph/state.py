from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class GenerateTestsRequest(BaseModel):
    repo_path: str = Field(..., description="被分析的Python项目路径（本地路径）")
    diff: str = Field(..., description="git diff 文本（建议为`git diff`原始输出）")
    run_eval: bool = Field(
        default=False,
        description="是否尝试在目标项目中执行pytest并返回摘要（需要安装.[eval]依赖）",
    )


class ImpactedItem(BaseModel):
    kind: Literal["file", "symbol"]
    id: str
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class TestPlanItem(BaseModel):
    target: str
    intent: str
    priority: Literal["high", "medium", "low"] = "medium"


class GeneratedTestFile(BaseModel):
    path: str
    content: str
    assumptions: list[str] = Field(default_factory=list)


class ImpactSeed(BaseModel):
    kind: Literal["function", "variable", "dependency"]
    name: str
    source: Literal["ast", "diff", "llm"] = "ast"


class ChangeRecord(BaseModel):
    entity: str
    type: Literal["function", "class", "method"]
    change_type: Literal["ADD", "MODIFY", "DELETE"]
    semantic_tags: list[str] = Field(default_factory=list)
    intent: Literal["BUG_FIX", "FEATURE", "REFACTOR"] = "REFACTOR"
    impact_seeds: list[ImpactSeed] = Field(default_factory=list)


class FileChangeSummary(BaseModel):
    file: str
    changes: list[ChangeRecord] = Field(default_factory=list)


class EvalSummary(BaseModel):
    ran: bool = False
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    coverage: Optional[float] = None


class GenerateTestsResponse(BaseModel):
    changed_files: list[str]
    change_analysis: list[FileChangeSummary] = Field(default_factory=list)
    impacted: list[ImpactedItem]
    test_plan: list[TestPlanItem]
    generated_tests: list[GeneratedTestFile]
    evaluation: Optional[EvalSummary] = None
    debug: dict[str, Any] = Field(default_factory=dict)


class ImpactedCandidate(BaseModel):
    kind: Literal["file", "symbol"]
    id: str
    via: str
    depth: int = 0


class WorkflowState(BaseModel):
    repo_path: str
    diff: str
    run_eval: bool = False

    changed_files: list[str] = Field(default_factory=list)
    diff_hunks: dict[str, Any] = Field(default_factory=dict)
    change_analysis: list[FileChangeSummary] = Field(default_factory=list)

    impacted: list[ImpactedCandidate] = Field(default_factory=list)
    impacted_ranked: list[ImpactedItem] = Field(default_factory=list)

    test_plan: list[TestPlanItem] = Field(default_factory=list)
    generated_tests: list[GeneratedTestFile] = Field(default_factory=list)

    evaluation: Optional[EvalSummary] = None
    debug: dict[str, Any] = Field(default_factory=dict)

    # agent outputs (aligned with diagram)
    bug_patterns: list[dict[str, Any]] = Field(default_factory=list)
    prioritized_plan: list[TestPlanItem] = Field(default_factory=list)
    retrieved_context: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    feedback: dict[str, Any] = Field(default_factory=dict)
