from pathlib import Path
from uuid import uuid4
import subprocess

from fastapi import FastAPI, HTTPException
import httpx
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import os

SD_CLI = Path(os.getenv("SD_CLI", "sd-cli"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", "/models/sd-turbo/sd_turbo.safetensors"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/output"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(title="Local Image Inference API")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    width: int = 384
    height: int = 384
    steps: int = 1
    cfg_scale: float = 1.0
    seed: int = -1


class GenerateResponse(BaseModel):
    success: bool
    message: str

    image_id: str | None = None

    error: str | None = None


@app.on_event("startup")
def startup() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SD_CLI.exists():
        raise RuntimeError(f"sd-cli not found at {SD_CLI}")

    if not MODEL_PATH.exists():
        raise RuntimeError(f"model not found at {MODEL_PATH}")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    image_id = str(uuid4())
    output_path = OUTPUT_DIR / f"{image_id}.png"

    cmd = [
        str(SD_CLI),
        "-m",
        str(MODEL_PATH),
        "-p",
        req.prompt,
        "-o",
        str(output_path),
        "-W",
        str(req.width),
        "-H",
        str(req.height),
        "-t",
        "4",
        "--steps",
        str(req.steps),
        "--cfg-scale",
        str(req.cfg_scale),
        "--seed",
        str(req.seed),
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "image generation failed",
                "error": str(exc),
            },
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail={
                "success": False,
                "message": "image generation timed out",
                "error": str(exc),
            }
        ) from exc

    return GenerateResponse(
        success = True,
        message = "image generation succeeded",
        image_id=image_id,
    )

@app.get("/images/{image_id}")
def get_image(image_id: str) -> FileResponse:
    image_path = OUTPUT_DIR / f"{image_id}.png"

    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail="image not found",
        )

    return FileResponse(
        image_path,
        media_type="image/png",
    )
