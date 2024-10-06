from enum import Enum
from timeit import default_timer as timer
from typing import List, Optional, cast

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ..components.component import Component, TComponent
from .options import DEFAULT_OPTIONS, VideoWriterOptions


class RenderMode(str, Enum):
    """An enum for the rendering mode"""

    CPU = "cpu"
    GPU = "gpu"


class Composition(BaseModel):
    components: List[Component] = Field(
        ..., description="The components of the composition"
    )
    duration: Optional[int] = Field(
        default=None, gt=0, description="The duration of the composition"
    )
    framerate: Optional[int] = Field(
        default=None, ge=0, description="The framerate of the composition"
    )

    @field_validator("duration", mode="before")
    def validate_duration(cls, value: int, info: ValidationInfo) -> int:
        components: List[Component] = info.data.get("components", [])

        return max(value, sum(component.duration for component in components))


class Timeline:
    """A class representing a timeline of compositions

    A timeline is a collection of compositions that are played in sequence.
    """

    class CompositionBuilder:
        """A builder class for creating a Composition object"""

        def __init__(self, timeline: "Timeline"):
            self._timeline = timeline
            self._components: List[Component] = []
            self._duration: Optional[int] = None
            self._framerate: Optional[int] = None

        def with_component(self, component: Component) -> "Timeline.CompositionBuilder":
            self._components.append(component)
            return self

        def with_components(
            self, components: List[Component]
        ) -> "Timeline.CompositionBuilder":
            # Set the z-index of components if not set
            self._components.extend(sorted(components, key=lambda x: x.z_index))
            return self

        def with_duration(self, duration: int) -> "Timeline.CompositionBuilder":
            assert duration > 0, "Duration must be greater than 0"
            self._duration = duration
            return self

        def with_framerate(self, framerate: int) -> "Timeline.CompositionBuilder":
            assert framerate > 0, "Framerate must be greater than 0"
            self._framerate = framerate
            return self

        def build(self) -> None:
            assert self._components, "Components must not be empty"
            assert self._duration, "Duration must be set"
            assert self._framerate, "Framerate must be set"
            self._timeline.composition = Composition(
                components=self._components,
                duration=self._duration,
                framerate=self._framerate,
            )
            # Free the builder
            self.free()

        def free(self) -> None:
            self._components = []
            self._duration = None
            self._framerate = None

    def __init__(self):
        self._composition: Optional[Composition] = None

    def add_composition(
        self,
        composition: List[TComponent],
    ) -> "Timeline.CompositionBuilder":
        composition_casted = cast(List[Component], composition)
        return Timeline.CompositionBuilder(self).with_components(composition_casted)

    def render(
        self,
        filename: str,
        mode: RenderMode = RenderMode.CPU,
        options: VideoWriterOptions = DEFAULT_OPTIONS,
    ) -> None:
        """Render the timeline

        Args:
            filename (str): The filename to render the timeline to
            mode (RenderMode, optional): The rendering mode. Defaults to RenderMode.CPU.
            options (VideoWriterOptions, optional): The video writer options. Defaults to DEFAULT_OPTIONS.
        """

        if mode == RenderMode.CPU:
            from .cpu import CPURenderer

            renderer = CPURenderer(filename, 1920 // 2, 1080 // 2, 40, 24)
            start_time = timer()
            renderer.render(self)
            print(f"Rendered in {timer() - start_time} seconds")
        elif mode == RenderMode.GPU:
            raise NotImplementedError("GPU rendering is not supported yet")

    @property
    def composition(self) -> Composition:
        if not self._composition:
            raise ValueError("Composition is not set")
        return self._composition

    @composition.setter
    def composition(self, value: Composition) -> None:
        if not isinstance(value, Composition):
            raise TypeError("Composition must be an instance of Composition")
        self._composition = value
