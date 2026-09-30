from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)

from .schemas import (
    DocumentRequest,
    ExportRequest,
)

from .services.exporters import (
    export_document,
)


router = APIRouter()


@router.post("/generate")
def generate_document(
    request: DocumentRequest,
):
    """
    Generate an AI-assisted legal document.
    """

    try:

        generator = GeminiDocumentGenerator()

        document = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return {
            "success": True,
            "document": document,
            "model": generator.model,
            "mock": generator.mock_ai,
        }

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Generation error: {exc}",
        ) from exc


@router.post("/export/{fmt}")
def export(
    fmt: str,
    request: ExportRequest,
):
    """
    Export a generated document as TXT, DOCX or PDF.
    """

    try:

        content, media_type, filename = export_document(
            fmt=fmt,
            text=request.text,
            doc_type=request.document_type,
            terms=request.terms,
            logo_base64=request.logo_base64,
        )

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            },
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Export error: {exc}",
        ) from exc