from typing import List

from ..components.component import Component, TComponent
from .options import DEFAULT_OPTIONS, VideoWriterOptions
from subprocess import run


class VideoComposer:

    def __init__(self):
        self._components: List[Component] = []

    def with_component(self, component: Component) -> "VideoComposer":
        assert isinstance(component, Component)
        self._components.append(component)
        return self

    def build_command(self) -> str:
        """Build the ffmpeg command for the video composer"""
        ffmpeg_input = ""
        ffmpeg_filter = ""

        for component in self._components:
            if component.type == "video":
                ffmpeg_input += f"-i {component.ffmpeg_input_command} "
            ffmpeg_filter += f"{component.ffmpeg_filter_command}"
        return f'{ffmpeg_input} -vf "{ffmpeg_filter}"'


class VideoWriter:

    def __init__(self, command: str, video_composer: VideoComposer):
        self._video_composer = video_composer
        self._command = command

    def write(self, output_path: str, options: VideoWriterOptions = DEFAULT_OPTIONS):

        command = f"ffmpeg -hide_banner -loglevel error {self._command} {options.ffmpeg_command} -c:a copy {output_path}"
        run(command, shell=True)
