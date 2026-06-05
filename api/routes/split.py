"""POST /split endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import SplitRequest, SplitResponse
from api.services.description_parser import parse_description
from api.services.pipeline import run_split
from api.services.receipt_extractor import extract_receipt

router = APIRouter()


@router.post("/split", response_model=SplitResponse, response_model_by_alias=True)
async def split_bill(body: SplitRequest) -> SplitResponse:
    try:
        return await run_split(
            body.receipt_base64,
            body.description,
            extract_receipt=extract_receipt,
            parse_description=parse_description,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Split failed: {exc}") from exc
