import platform
from os import path
from typing import Callable, Literal, Optional, cast

from numpy import array, ndarray
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pydantic import BaseModel, Field, computed_field

from .component import Component, Position

system = platform.system()


class TextStyle(BaseModel):
    font_size: int = Field(..., description="The font size of the text")
    font_family: str = Field(..., description="The font family of the text")
    color: str = Field(..., description="The color of the text")
    background_color: str = Field(..., description="The background color of the text")

    @property
    def font_path(self) -> str:
        # verify first is font_family is path
        if path.exists(self.font_family):
            return self.font_family

        if system == "Darwin":
            return f"/Library/Fonts/{self.font_family}.ttf"
        elif system == "Linux":
            return f"/usr/share/fonts/{self.font_family}.ttf"
        elif system == "Windows":
            return f"C:/Windows/Fonts/{self.font_family}.ttf"
        else:
            raise ValueError(f"Unsupported system: {system}")


DEFAULT_TEXT_STYLE = TextStyle(
    font_size=34,
    font_family=r"C:\Users\Ebrain\Downloads\MSMINCHO.TTF",
    color="white",
    background_color="black",
)


class Text(Component):
    type: Literal["text"] = "text"
    content: str = Field(..., description="The content of the text component")
    style: TextStyle = Field(
        default=DEFAULT_TEXT_STYLE, description="The style of the text component"
    )

    def generate_frame(self):
        return self.make_text_frame(self.content, self.style)

    def make_text_frame(
        self,
        content: str,
        text_style: TextStyle,
    ):

        try:
            font = ImageFont.truetype(
                text_style.font_path,
                text_style.font_size,
            )
        except IOError:
            print(f"Font file not found: {text_style.font_path}")
            font = ImageFont.load_default()

        box = font.getbbox(content)
        width = int(box[2] - box[0])
        height = int(box[3] - box[1])
        offset = text_style.font_size // 2
        image = Image.new(
            "RGBA",
            (width + offset, height + offset),
            (255, 255, 255, 0),
        )

        with Pilmoji(image) as draw:
            draw.text(
                (offset // 2, offset // 2),
                content,
                font=font,
                fill=text_style.color,
                stroke_width=5,
                stroke_fill=text_style.background_color,
            )

        return image

    @computed_field(repr=False)
    @property
    def content_length(self) -> int:
        return len(self.content)
