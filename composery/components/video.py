from typing import Literal

from pydantic import Field

from .component import Component


class Video(Component):
    type: Literal["video"] = "video"
    width: int = Field(..., description="The width of the video component")
    height: int = Field(..., description="The height of the video component")
    source: str = Field(..., description="The source of the video component")
    allow_audio: bool = Field(
        default=True, description="Whether to allow audio in the video component"
    )
