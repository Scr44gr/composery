from typing import Callable, TypeVar, cast

from fastnanoid import generate
from pydantic import BaseModel, Field, ValidationInfo, computed_field, field_validator

TComponent = TypeVar("TComponent", bound="Component")


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


class Component(BaseModel):
    id: str = Field(default_factory=lambda: generate(size=8))
    type: str = Field(..., description="The type of the component")
    start_at: int = Field(..., ge=0, description="The start time of the component")
    end_at: int = Field(..., ge=0, description="The end time of the component")
    duration: int = Field(..., ge=0, description="The duration of the component")
    position: Position = Field(
        default_factory=lambda: Position(x="center", y="center"),
        description="The position of the component",
    )
    z_index: int = Field(default=0, description="The z-index of the component")

    @field_validator("end_at", mode="before")
    def validate_start_at(cls, value: int, info: ValidationInfo) -> int:

        if value is not None:
            start_at = info.data.get("start_at", 0)
            if value < start_at:
                raise ValueError("end_at must be greater than start_at")
        return value

    @property
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
