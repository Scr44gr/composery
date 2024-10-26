import platform
from os import path
from typing import Literal

from PIL import Image, ImageFont
from pilmoji import Pilmoji, getsize
from pydantic import Field, computed_field

from .component import Component, Styles

system = platform.system()


class TextStyle(Styles):
    text_align: Literal["left", "center", "right"] = Field(
        "center", description="The alignment of the text"
    )
    font_size: int = Field(..., description="The font size of the text")
    font_family: str = Field(..., description="The font family of the text")
    color: str = Field(..., description="The color of the text")
    stroke_width: int = Field(default=0, description="The stroke width of the text")
    stroke_color: str = Field(
        default="none", description="The stroke color of the text"
    )

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
    font_size=72,
    font_family=r"Arial",
    color="white",
    background_color="black",
    text_align="center",
    stroke_width=5,
    stroke_color="black",
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
            font = ImageFont.load_default()

        width, height = getsize(content.strip(), font=font)
        offset = text_style.font_size // 2
        image = Image.new(
            "RGBA",
            (width + offset, height + offset),
            (255, 255, 255, 0),
        )
        has_background = text_style.background_color != "transparent"
        with Pilmoji(image) as pilmoji:

            pilmoji.text(
                (offset // 2, offset // 2),
                content,
                font=font,
                fill=text_style.color,
                align=text_style.text_align,
                stroke_width=text_style.stroke_width,
                stroke_fill=text_style.background_color,
            )

        return image

    @computed_field(repr=False)
    @property
    def content_length(self) -> int:
        return len(self.content)
