from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
from agent_handler import addAPIKey, tester

app = FastAPI(title="Squarenetes API")

origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    subprompt: str
    api_keys: List[str]
    n: int

@app.post("/execute", tags=["execute"])
async def execute_prompt(request: PromptRequest):
    for f in ["output.txt", "output.zip"]:
        if os.path.exists(f):
            os.remove(f)

    labels = ["openai", "anthropic", "google"]
    for i, key in enumerate(request.api_keys):
        if i < len(labels):
            addAPIKey(labels[i], key)

    tester(request.subprompt, request.n)
    return {"status": "success", "download_url": "/download"}

@app.get("/download", tags=["download"])
async def download_output():
    if os.path.exists("output.zip"):
        return FileResponse(
            path="output.zip",
            filename="output.zip",
            media_type="application/zip"
        )
    return {"error": "No output file available"}
