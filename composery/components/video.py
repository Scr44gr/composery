from typing import Literal
from pydantic import BaseModel, Field
from .component import Component
from os import path


class Video(Component):
    type: Literal["video"] = "video"
    width: int = Field(..., description="The width of the video component")
    height: int = Field(..., description="The height of the video component")
    source: str = Field(..., description="The source of the video component")

    @property
    def ffmpeg_input_command(self) -> str:
        assert path.exists(self.source), f"File {self.source} does not exist"
        # get full path of the source file
        source = path.abspath(self.source)

        return f'"{source}" -t {self.duration}'

    @property
    def ffmpeg_filter_command(self) -> str:
        return f""
