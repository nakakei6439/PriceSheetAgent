from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from azure.core.exceptions import AzureError
from openai import OpenAIError

from app.agent import run as run_agent
from app.models import ExtractionResult
from app.settings import get_settings


app = FastAPI(title="PriceSheetAgent Price Sheet Extraction Agent")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractionResult)
async def extract(file: UploadFile = File(...)) -> ExtractionResult:
    if not file.filename or not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="PDF または画像 (PNG/JPG) のみ受け付けます")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="空のファイルです")
    if len(pdf_bytes) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes / 1024 / 1024
        raise HTTPException(status_code=413, detail=f"ファイルサイズは {max_mb:.0f}MB 以下にしてください")
    try:
        return run_agent(pdf_bytes)
    except AzureError as exc:
        raise HTTPException(status_code=502, detail=f"Azure Document Intelligence の呼び出しに失敗しました: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"Azure OpenAI の呼び出しに失敗しました: {exc}") from exc
