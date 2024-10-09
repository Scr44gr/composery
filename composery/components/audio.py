from os import path
from typing import Literal, Optional

from pydantic import Field, ValidationInfo, field_validator

from .component import Component, Trim


class Audio(Component):
    type: Literal["audio"] = "audio"
    source: str = Field(..., description="The source of the audio component")
    start_at: int | float = Field(
        0, ge=0, description="The start time of the audio component"
    )
    end_at: int | float = Field(
        None, gt=0, description="The end time of the audio component"
    )
    trim: Trim = Field(
        default_factory=lambda: Trim(start=0, end=0),
        description="The trim of the audio component",
    )
    volume: float = Field(
        1.0, ge=0, le=1, description="The volume of the audio component"
    )

    @field_validator("source", mode="before")
    def validate_source(cls, value: str) -> str:
        if not path.exists(value):
            raise FileNotFoundError(f"File not found: {value}")
        return value

    @property
    def path(self) -> Optional[str]:
        audio_formats = ["aac", "mp3", "wav", "ogg"]
        if self.source.endswith(tuple(audio_formats)):
            return self.source
        return
