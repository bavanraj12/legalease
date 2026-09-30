from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    """
    Data received from the Streamlit frontend
    when generating a legal document.
    """

    document_type: str = Field(
        min_length=2,
        max_length=120,
    )

    parties: str = Field(
        min_length=2,
        max_length=5000,
    )

    terms: str = Field(
        min_length=2,
        max_length=12000,
    )

    dates: str = Field(
        min_length=2,
        max_length=300,
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates",
    )
    @classmethod
    def strip_values(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be blank."
            )

        return value


class ExportRequest(BaseModel):
    """
    Data received when exporting a generated document.
    """

    text: str = Field(
        min_length=2,
        max_length=50000,
    )

    document_type: str = Field(
        default="Legal Document",
        max_length=120,
    )

    terms: str = Field(
        default="",
        max_length=12000,
    )

    logo_base64: str | None = None