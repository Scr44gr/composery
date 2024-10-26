from typing import Callable, Literal, Optional, TypeVar, cast

from fastnanoid import generate
from PIL import Image, ImageDraw
from pydantic import BaseModel, Field, ValidationInfo, computed_field, field_validator

TComponent = TypeVar("TComponent", bound="Component")


class Trim(BaseModel):
    """A class representing a trim which basically cuts a video or audio component from a start time to an end time"""

    start: float = Field(..., ge=0, description="The start time of the trim")
    end: float = Field(..., ge=0, description="The end time of the trim")


class Position(BaseModel):
    x: int | str = Field(..., description="Position x")
    y: int | str = Field(..., description="Position y")

    @field_validator("x", mode="before")
    def validate_x(cls, value: int | str):
        if isinstance(value, int):
            return value

        ALLOWED_VALUES = ["center", "left", "right"]
        if value.lower() not in ALLOWED_VALUES:
            raise ValueError(f"X must be one of {ALLOWED_VALUES}")
        return value

    @field_validator("y", mode="before")
    def validate_y(cls, value: int | str):
        if isinstance(value, int):
            return value

        ALLOWED_VALUES = ["center", "top", "bottom"]
        if value.lower() not in ALLOWED_VALUES:
            raise ValueError(f"Y must be one of {ALLOWED_VALUES}")
        return value


class Styles(BaseModel):
    background_color: str = Field(
        default="transparent", description="The background color of the component"
    )
    border_radius: int = Field(
        default=0, description="The border radius of the component"
    )
    border_color: str = Field(
        default="none", description="The border color of the component"
    )
    border_width: int = Field(
        default=0, description="The outline width of the component"
    )
    outline_width: int = Field(
        default=0, description="The outline width of the component"
    )
    outline_color: str = Field(
        default="none", description="The outline color of the component"
    )
    width: float | Literal["auto"] = Field(
        default="auto", description="The width of the component"
    )
    height: float | Literal["auto"] = Field(
        default="auto", description="The height of the component"
    )


DEFAULT_STYLES = Styles(
    background_color="black",
    border_radius=0,
    border_color="black",
    outline_width=0,
    outline_color="black",
    width="auto",
    height="auto",
)


class Component(BaseModel):
    id: str = Field(default_factory=lambda: generate(size=8))
    type: str = Field(..., description="The type of the component")
    start_at: float = Field(..., ge=0, description="The start time of the component")
    end_at: float = Field(default=-1, ge=0, description="The end time of the component")
    duration: float = Field(..., ge=0, description="The duration of the component")
    position: Position = Field(
        default_factory=lambda: Position(x="center", y="center"),
        description="The position of the component",
    )
    z_index: int = Field(default=0, description="The z-index of the component")
    styles: Styles = Field(
        default=DEFAULT_STYLES,
        description="The styles of the component",
    )

    @field_validator("end_at", mode="before")
    def validate_end_at(cls, value: float, info: ValidationInfo) -> float:

        if value == -1:
            start_at = info.data.get("start_at", 0)
            if value < start_at:
                raise ValueError("end_at must be greater than start_at")
            return value
        # in case valeu is none, return the duration value
        duration = info.data.get("duration")
        assert (
            duration is not None
        ), "duration must be provided if end_at is not provided"
        return duration

    def get_frame_at_time(self) -> Callable[[int], None]:
        raise NotImplementedError("get_frame_at_time method must be implemented")

    @computed_field(repr=False)
    @property
    def fixed_position(
        self,
    ) -> Callable[[tuple[int, int], tuple[int, int], int], tuple[int, int]]:

        def get_fixed_position(
            frame_size: tuple[int, int],
            component_size: tuple[int, int],
            offset: int,
        ) -> tuple[int, int]:
            x, y = self.position.x, self.position.y
            if isinstance(x, int) and isinstance(y, int):
                return x, y

            # X position
            elif x == "center":
                x = (frame_size[0] - component_size[0]) // 2
            elif x == "right":
                x = frame_size[1] - component_size[0]
            elif x == "left":
                x = 0

            # Y position
            if y == "center":
                y = (frame_size[1] - component_size[1]) // 2
            elif y == "bottom":
                y = frame_size[1] - component_size[1]
            elif y == "top":
                y = 0

            return cast(tuple[int, int], (x, y))

        return get_fixed_position

    def prerendered_box(self) -> Optional[Image.Image]:
        """Used to get the box of the component before rendering"""
        width, height = self.styles.width, self.styles.height
        if isinstance(width, str) or isinstance(height, str):
            # In case of auto width or height return None
            # because we don't know the size of the component
            # so, create the box in the custom component
            return
        has_border = self.styles.border_color != "none"
        border_width = self.styles.border_width
        img = Image.new(
            "RGBA",
            (int(width), int(height)),
            self.styles.background_color,
        )
        if has_border:
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle(
                (0, 0, int(width), int(height)),
                outline=self.styles.border_color,
                width=border_width,
            )
        return img
