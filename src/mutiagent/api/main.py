from fastapi import FastAPI

from mutiagent.graph.state import GenerateTestsRequest, GenerateTestsResponse
from mutiagent.graph.workflow import run_workflow

app = FastAPI(title="mutiagent-mvp", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/generate-tests", response_model=GenerateTestsResponse)
def generate_tests(req: GenerateTestsRequest) -> GenerateTestsResponse:
    result = run_workflow(repo_path=req.repo_path, diff=req.diff, run_eval=req.run_eval)
    return GenerateTestsResponse(**result)
