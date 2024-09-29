from typing import Literal
from pydantic import BaseModel, Field
from .component import Component
import platform

system = platform.system()


class TextStyle(BaseModel):
    font_size: int = Field(..., description="The font size of the text")
    font_family: str = Field(..., description="The font family of the text")
    color: str = Field(..., description="The color of the text")
    background_color: str = Field(..., description="The background color of the text")

    @property
    def font_path(self) -> str:

        if system == "Darwin":
            return f"/Library/Fonts/{self.font_family}.ttf"
        elif system == "Linux":
            return f"/usr/share/fonts/{self.font_family}.ttf"
        elif system == "Windows":
            return f"C:/Windows/Fonts/{self.font_family}.ttf"
        else:
            raise ValueError(f"Unsupported system: {system}")


DEFAULT_TEXT_STYLE = TextStyle(
    font_size=50, font_family="arial", color="white", background_color="black"
)


class Text(Component):
    type: Literal["text"] = "text"
    content: str = Field(..., description="The content of the text component")
    style: TextStyle = Field(
        default=DEFAULT_TEXT_STYLE, description="The style of the text component"
    )

    @property
    def ffmpeg_filter_command(self) -> str:
        from os import path

        if not path.exists(self.style.font_path):
            raise ValueError(f"Font file not found: {self.style.font_path}")

        return (
            f"drawtext=text='{self.content}':fontfile='{self.style.font_path}':"
            f"fontsize={self.style.font_size}:fontcolor={self.style.color}:"
            f"borderw=0:bordercolor={self.style.background_color}:"
            f"x=(W-text_w)/2:y=(H-text_h)/2"
            f":enable='between(t,{self.start_at},{self.end_at})',"
        )
