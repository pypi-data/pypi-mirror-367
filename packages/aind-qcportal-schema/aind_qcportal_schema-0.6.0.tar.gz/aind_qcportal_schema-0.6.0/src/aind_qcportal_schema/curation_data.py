from pydantic import BaseModel, Field


class CurationData(BaseModel):
    """Schema for curation data fields in the QC portal.

    You should inherit from this schema to create custom curation data objects with additional fields.

    Using this schema enforces the requirement that a *reference* field be present,
    which will be used to display some attached media. All the same rules that apply to
    QC references apply here (valid URL, relative path from quality_control.json, etc)

    The other fields in the object will be displayed in a table in the QC portal."""

    reference: str = Field(
        ...,
        title="Reference",
        description="A valid reference to a media file (e.g., image, video) that is relevant to the curation data.",
    )
