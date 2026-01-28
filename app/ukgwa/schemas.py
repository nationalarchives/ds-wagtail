import hashlib
import json

from app.ukgwa.utils import normalize_archive_letter
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PositiveInt,
    computed_field,
)


class ArchiveRecordSchema(BaseModel):
    """
    Pydantic schema for validating archive entries from JSON.

    - Validates data structure, types, and business rules before saving to the database.
    - Computes derived fields (hash, sort_name, first_character).
    """

    profile_name: str = Field(alias="profileName", min_length=1)
    record_url: HttpUrl = Field(alias="entryUrl")
    archive_link: HttpUrl = Field(alias="archiveLink")
    domain_type: str = Field(default="", alias="domainType")
    first_capture_display: str = Field(alias="firstCaptureDisplay")
    latest_capture_display: str = Field(alias="latestCaptureDisplay")
    ongoing: bool = Field(default=False)
    wam_id: PositiveInt = Field(alias="wamId")
    description: str | None = Field(alias="description")

    model_config = ConfigDict(
        validate_by_alias=True,  # Allow alias names from JSON (camelCase)
        str_strip_whitespace=True,
    )

    @computed_field
    @property
    def sort_name(self) -> str:
        """
        Compute normalized name for sorting by removing leading 'the ' (case-insensitive).
        """
        if not self.profile_name:
            return ""

        name = self.profile_name.strip()
        name_lower = name.lower()

        # Strip leading "THE "
        if name_lower.startswith("the "):
            name = name[4:].strip()

        return name

    @computed_field
    @property
    def first_character(self) -> str:
        """
        Compute first character for navigation.

        Returns:
            lowercase letter (a-z) or '0-9' for digits and symbols.
        """
        if not self.sort_name:
            return "0-9"

        first_char = self.sort_name[0]

        normalized = normalize_archive_letter(first_char)

        # If normalization returns empty (invalid input), default to '0-9'
        return normalized if normalized else "0-9"

    @computed_field
    @property
    def record_hash(self) -> str:
        """
        Compute MD5 hash of record data for change detection.
        """
        # Get model data excluding wam_id and computed fields
        data = self.model_dump(
            mode="json",  # Converts HttpUrl JSON-serializable value
            exclude={"wam_id", "sort_name", "first_character", "record_hash"},
            by_alias=False,
        )

        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
