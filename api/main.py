"""
FastAPI REST API for the AI BIM House Generator.

Exposes endpoints for generating IFC files from natural language prompts
or structured HousePlan payloads.

Usage:
    uvicorn api.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent.agent import run_agent, run_agent_with_plan
from models.schema import HousePlan

app = FastAPI(
    title="AI BIM House Generator API",
    description="Convert natural language prompts into IFC building models",
    version="0.1.0",
)


# --- Request/Response Models ---


class GenerateRequest(BaseModel):
    """Request payload for prompt-based generation."""

    prompt: str
    output: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "casa moderna de 12x8 metros com telhado",
                "output": "modern_house.ifc",
            }
        }


class GenerateResponse(BaseModel):
    """Response with generated file path and summary."""

    file: str
    summary: str


# --- Endpoints ---


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "AI BIM House Generator API",
        "version": "0.1.0",
        "endpoints": {
            "POST /generate": "Generate IFC from natural language prompt",
            "POST /generate/plan": "Generate IFC from structured HousePlan",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint for orchestrators (K8s, ECS)."""
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerateResponse)
def generate_from_prompt(request: GenerateRequest):
    """Generate an IFC file from a natural language prompt.

    Args:
        request: GenerateRequest with prompt and optional output path.

    Returns:
        GenerateResponse with file path and summary.

    Raises:
        HTTPException: 500 if generation fails.
    """
    try:
        file_path, summary = run_agent(request.prompt, output=request.output)
        return GenerateResponse(file=file_path, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IFC generation failed: {str(e)}")


@app.post("/generate/plan", response_model=GenerateResponse)
def generate_from_plan(plan: HousePlan):
    """Generate an IFC file from a structured HousePlan.

    Args:
        plan: Validated HousePlan with all geometric parameters.

    Returns:
        GenerateResponse with file path and summary.

    Raises:
        HTTPException: 500 if generation fails.
    """
    try:
        file_path, summary = run_agent_with_plan(plan)
        return GenerateResponse(file=file_path, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IFC generation failed: {str(e)}")


@app.get("/download/{filename}")
def download_file(filename: str):
    """Download a generated IFC file.

    Args:
        filename: Name of the IFC file to download.

    Returns:
        FileResponse with the IFC file.

    Raises:
        HTTPException: 404 if file not found.
    """
    from pathlib import Path

    file_path = Path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        filename=filename,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
