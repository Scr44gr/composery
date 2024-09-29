from typing import TypeVar
from pydantic import BaseModel, Field, field_validator
from fastnanoid import generate

TComponent = TypeVar("TComponent")


class Position(BaseModel):
    x: int | str = Field(..., description="Position x")
    y: int | str = Field(..., description="Position y")

    @field_validator("x", "y")
    def validate_x_and_y(cls, value: int | str):
        if isinstance(value, int):
            return value

        ALLOWED_VALUES = ["center", "left", "right", "top", "bottom"]
        if value.lower() not in ALLOWED_VALUES:
            raise ValueError(f"X must be one of {ALLOWED_VALUES}")
        return value


# TODO: Create a validator for ID
class Component(BaseModel):
    id: str = Field(default_factory=lambda: generate(size=8))
    type: str = Field(..., description="The type of the component")
    start_at: int = Field(..., description="The start time of the component")
    end_at: int = Field(..., description="The end time of the component")
    duration: int = Field(..., description="The duration of the component")
    position: Position = Field(
        default_factory=lambda: Position(x="center", y="center"),
        description="The position of the component",
    )

    @property
    def ffmpeg_input_command(self) -> str:
        raise NotImplementedError(
            "ffmpeg_command must be implemented in the child class"
        )

    @property
    def ffmpeg_filter_command(self) -> str:
        raise NotImplementedError(
            "ffmpeg_command must be implemented in the child class"
        )
