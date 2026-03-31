from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

ImpactKind = Literal["file", "symbol", "seed", "focus"]


class GenerateTestsRequest(BaseModel):
    repo_path: str = Field(..., description="被分析的Python项目路径（本地路径）")
    diff: str = Field(..., description="git diff 文本（建议为`git diff`原始输出）")
    run_eval: bool = Field(
        default=False,
        description="是否尝试在目标项目中执行pytest并返回摘要（需要安装.[eval]依赖）",
    )


class TestStrategyItem(BaseModel):
    type: str
    target: str
    priority: float = Field(ge=0.0, le=1.0, default=0.5)


class ImpactedItem(BaseModel):
    kind: ImpactKind
    id: str
    score: float = Field(ge=0.0, le=1.0)
    reason: str
    test_strategy: list[TestStrategyItem] = Field(default_factory=list)
    system_impact: list[str] = Field(default_factory=list)
    initial_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    impact_type: list[str] = Field(
        default_factory=list,
        description="与候选对齐的影响类型，供下游测试规划桥接",
    )


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
    test_focus: list[str] = Field(
        default_factory=list,
        description="由 semantic_tags 映射的测试设计关注点（如 branch_coverage、integration）",
    )
    intent: Literal["BUG_FIX", "FEATURE", "REFACTOR"] = "REFACTOR"
    impact_seeds: list[ImpactSeed] = Field(default_factory=list)


class FileChangeSummary(BaseModel):
    file: str
    changes: list[ChangeRecord] = Field(default_factory=list)


class ChangeGraphNode(BaseModel):
    """变更图顶点：文件 / 变更符号 / impact_seed / 测试关注点。"""

    id: str
    kind: Literal["file", "symbol", "seed", "focus"]
    label: str
    meta: dict[str, Any] = Field(default_factory=dict)


class ChangeGraphEdge(BaseModel):
    """有向边，供影响传播与测试优先级加权。"""

    src: str
    dst: str
    relation: Literal["contains_change", "emits_seed", "test_focus"] = "contains_change"
    weight: float = Field(default=1.0, ge=0.0, le=10.0)


class ChangeGraph(BaseModel):
    nodes: list[ChangeGraphNode] = Field(default_factory=list)
    edges: list[ChangeGraphEdge] = Field(default_factory=list)


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
    kind: ImpactKind
    id: str
    via: str
    depth: int = 0
    impact_type: list[str] = Field(default_factory=list)
    propagation_path: list[str] = Field(default_factory=list)
    propagation_depth: int = 0
    propagation_type: str = "direct"
    meta: dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    repo_path: str
    diff: str
    run_eval: bool = False

    changed_files: list[str] = Field(default_factory=list)
    diff_hunks: dict[str, Any] = Field(default_factory=dict)
    change_analysis: list[FileChangeSummary] = Field(default_factory=list)
    change_graph: Optional[ChangeGraph] = None

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
