import os
import uuid
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from inference import load_model, analyze_audio
from report import generate_pdf

app = FastAPI(
    title="VoiceVault API",
    description="Real-time deepfake voice detection powered by RawNet2",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading RawNet2 model...")
model = load_model()
print("Model ready. Server starting...\n")

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
MAX_FILE_SIZE_MB   = 50


@app.get("/")
def root():
    return {
        "name":     "VoiceVault API",
        "version":  "1.0.0",
        "status":   "running",
        "endpoints": ["POST /analyze", "POST /report"]
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": "RawNet2", "auc": 0.9929}

async def _save_upload(file: UploadFile) -> tuple[str, str, bytes]:

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. "
                   f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Maximum is {MAX_FILE_SIZE_MB} MB."
        )

    tmp = tempfile.NamedTemporaryFile(
        suffix=ext, delete=False, dir=tempfile.gettempdir()
    )
    tmp.write(content)
    tmp.close()
    return tmp.name, ext, content

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    tmp_path = None
    try:
        tmp_path, ext, _ = await _save_upload(file)
        result = analyze_audio(model, tmp_path)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/report")
async def report(file: UploadFile = File(...)):

    tmp_path = None
    try:
        tmp_path, ext, _ = await _save_upload(file)

        result = analyze_audio(model, tmp_path)

        pdf_bytes = generate_pdf(result, filename=file.filename or f"audio{ext}")

        safe_name = Path(file.filename or "audio").stem
        download_name = f"voicevault_report_{safe_name}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{download_name}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)