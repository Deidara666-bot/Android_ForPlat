from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_agent, get_db
from app.core import constants
from app.core.config import get_settings
from app.models.agent import Agent
from app.schemas.evidence import EvidenceOut, EvidenceUploadForm
from app.services.evidence_service import EvidenceService, UploadRejectedError
from app.services.evidence_storage_service import EvidenceStorageService

router = APIRouter(prefix="/evidence", tags=["evidence"])

_BACKEND_DIR = Path(__file__).resolve().parents[3]


class _UploadRequest(EvidenceUploadForm):
    """The agent's multipart body: the metadata fields plus the evidence file."""

    file: UploadFile


def get_evidence_storage() -> EvidenceStorageService:
    root = Path(get_settings().evidence_root)
    return EvidenceStorageService(root if root.is_absolute() else _BACKEND_DIR / root)


@router.post(
    "/upload",
    response_model=EvidenceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload raw evidence (agent token)",
)
async def upload_evidence(
    agent: Annotated[Agent, Depends(get_current_agent)],
    db: Annotated[Session, Depends(get_db)],
    storage: Annotated[EvidenceStorageService, Depends(get_evidence_storage)],
    request: Annotated[_UploadRequest, Form()],
) -> EvidenceOut:
    # The client's file name is ignored; the stored name is built by the server.
    data = await request.file.read(constants.MAX_UPLOAD_BYTES + 1)
    form = EvidenceUploadForm(**request.model_dump(exclude={"file"}))
    if len(data) > constants.MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, detail="evidence file too large")
    try:
        evidence, matches = EvidenceService(db, storage).ingest(agent, form, data)
    except UploadRejectedError as exc:
        raise HTTPException(exc.status_code, detail=exc.detail) from None
    if not matches:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "jenis": "Sha256Mismatch",
                "pesan": "hash SHA-256 server tidak sama dengan hash agen; berkas tidak disimpan",
                "evidence_id": str(evidence.id),
            },
        )
    return EvidenceOut.model_validate(evidence, from_attributes=True)
