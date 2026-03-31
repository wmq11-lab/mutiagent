from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ImpactKind = Literal["file", "symbol", "seed", "focus"]

SemanticUnitType = Literal["config", "exception", "api", "data_processing"]

TestPriorityTier = Literal["P0", "P1", "P2"]


class ImpactTestFocusDerived(BaseModel):
    """规则驱动的测试关注点，必须可追溯规则说明。"""

    type: str
    derived_from: str


class ExecutableTestStrategy(BaseModel):
    """可执行向的测试策略：供 TestGen / 人工直接落地为用例。"""

    model_config = ConfigDict(populate_by_name=True)

    scenario: str = ""
    input: str = Field(default="", description="建议输入或前置条件描述")
    mock: str = Field(default="", description="mock / patch / stub 说明")
    assert_: str = Field(default="", alias="assert", description="断言或期望行为")


class TopRiskEntry(BaseModel):
    """V4：高风险语义单元摘要，供报告与人工复核。"""

    semantic_unit_id: str
    reason: str


class SemanticUnit(BaseModel):
    """
    全局语义单元目录项（V4）：原子能力一条一目；含 upstream / edge_types；priority_score 拉开梯度。
    symbol 通过 semantic_unit_id 引用本条目。
    """

    semantic_unit_id: str = Field(..., description="原子 id，如 api:call_llm、config:getenv_app_key")
    type: SemanticUnitType
    source: str
    risk_score: float = Field(ge=0.0, le=1.0, description="局部风险分（意图×语义×传播衰减）")
    priority_score: float = Field(
        ge=0.0,
        le=1.0,
        description="V4：risk×change_weight×centrality×log(1+refs)×integration_bonus，映射到约 0.2~0.9",
    )
    test_priority: TestPriorityTier = Field(
        default="P2",
        description="P0：config/exception/外部 API；P1：高优先级数据处理；P2：其余",
    )
    centrality_factor: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="调用链中心性乘子（1.2/1.0/0.8 档），已参与 priority_score 计算并落盘供审计",
    )
    call_chain: list[str] = Field(
        default_factory=list,
        description="限定名路径，如 file.py:Class.method → 跨文件下游（1~2 跳）",
    )
    downstream: list[str] = Field(
        default_factory=list,
        description="跨文件/同文件下游符号 id（与 call_chain 互补的扁平列表）",
    )
    upstream: list[str] = Field(
        default_factory=list,
        description="V4：指向本符号的上游 symbol_id（由下游关系反推，启发式）",
    )
    edge_types: list[str] = Field(
        default_factory=list,
        description="V4：边类型标签，如 call / config / data",
    )
    integration_risk: bool = Field(
        default=False,
        description="多模块或跨文件下游时为 True，提示集成测试",
    )
    referenced_symbol_ids: list[str] = Field(
        default_factory=list,
        description="引用该单元的符号 id 列表（用于 frequency 与去重）",
    )
    propagation_depth: int = Field(default=0, ge=0, description="相对变更符号的传播深度")
    test_focus: list[ImpactTestFocusDerived] = Field(default_factory=list)
    test_strategy: list[ExecutableTestStrategy] = Field(default_factory=list)


class ImpactGraphSymbol(BaseModel):
    """文件内的变更符号（class / method / function）；仅引用语义单元 id。"""

    name: str
    entity_type: Literal["function", "class", "method"] = "function"
    symbol_id: str
    semantic_unit_ids: list[str] = Field(default_factory=list)
    centrality: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="符号级枢纽程度（多单元/集成边时升高），供展示与二次排序",
    )


class ImpactTestPlanEntry(BaseModel):
    """V3：按符号汇总的可执行向测试计划（ImpactAgent 直接产出）。"""

    target: str = Field(..., description="符号短名（类/函数）")
    symbol_id: str = Field(default="", description="file:type:entity")
    priority: TestPriorityTier = "P2"
    test_types: list[str] = Field(default_factory=list, description="如 integration、exception、unit、env、mock")
    estimated_cases: int = Field(default=0, ge=0)
    reason: str = Field(default="", description="聚合原因说明（中文）")


class ImpactGraphFile(BaseModel):
    """分层结构：文件 → 符号 → 语义单元。"""

    file: str
    symbols: list[ImpactGraphSymbol] = Field(default_factory=list)


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
    impact_graph: list[ImpactGraphFile] = Field(default_factory=list)
    semantic_units_catalog: list[SemanticUnit] = Field(
        default_factory=list,
        description="V3 全局语义单元目录（去重，可排序）",
    )
    impact_test_plan: list[ImpactTestPlanEntry] = Field(
        default_factory=list,
        description="V3 符号级测试计划摘要",
    )
    top_risks: list[TopRiskEntry] = Field(
        default_factory=list,
        description="V4：按 priority_score 排序的高风险语义单元",
    )
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
    impact_graph: list[ImpactGraphFile] = Field(
        default_factory=list,
        description="分层影响图：file → symbol → semantic_unit_id（主消费结构，V3）",
    )
    semantic_units_catalog: list[SemanticUnit] = Field(
        default_factory=list,
        description="语义单元全局目录：semantic_unit_id → 详情（V3）",
    )
    impact_test_plan: list[ImpactTestPlanEntry] = Field(
        default_factory=list,
        description="ImpactAgent 汇总的符号级测试计划（V3）",
    )
    top_risks: list[TopRiskEntry] = Field(
        default_factory=list,
        description="V4：高风险语义单元列表",
    )

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
