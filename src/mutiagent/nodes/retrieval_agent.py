from __future__ import annotations

from mutiagent.graph.state import WorkflowState


def retrieval_agent(state: WorkflowState) -> WorkflowState:
    """
    MVP占位：不接向量库，只返回一个空检索结果。
    后续接 Pinecone/Chroma：在这里把相关历史测试/相似代码片段塞进 retrieved_context。
    """
    state.retrieved_context = {"enabled": False, "items": []}
    state.debug["retrieval_agent"] = {"enabled": False}
    return state

