import multiprocessing as mp
import tempfile
from fractions import Fraction
from os import path
from typing import Dict, Iterable

import numpy as np
from av.container import open as open_container
from av.video.frame import VideoFrame
from PIL import Image

from ...components.audio import Audio
from ...components.text import Text
from ...components.video import Video
from ...reader import audio as audio_reader
from ...reader import video as video_reader
from ..timeline import Timeline


class CPURenderer:
    __slots__ = (
        "output_filename",
        "width",
        "height",
        "framerate",
        "duration",
        "timeline",
        "BLANK_FRAME",
    )
    READERS = {}
    COMPUTED_FRAMES: Dict[str, Image.Image] = {}

    def __init__(
        self,
        output_filename: str,
        width: int,
        height: int,
        duration: int,
        framerate: int,
    ):
        self.output_filename = output_filename
        self.width = width
        self.height = height
        self.framerate = framerate
        self.duration = duration
        self.BLANK_FRAME = np.zeros((height, width, 3), dtype=np.uint8)

    def render(self, timeline: Timeline):
        self.timeline = timeline
        self.render_frames()
        # self.process_audio()

    def get_frame_at_time(self, time: float) -> VideoFrame:
        frame = Image.fromarray(self.BLANK_FRAME)
        for component in self.timeline.composition.components:
            if not (component.start_at <= time <= component.end_at):
                continue
            frame_number = int(round((time - component.start_at) * self.framerate, 0))
            if isinstance(component, Video):
                try:
                    video_frame = video_reader.get_frame_from_video(
                        component.source, frame_number
                    )
                    if not video_frame:
                        continue

                    frame.paste(
                        video_frame,
                        component.fixed_position(
                            frame.size,
                            (video_frame.size[0], video_frame.size[1]),
                            0,
                        ),
                    )
                except IndexError:
                    continue
            elif isinstance(component, Text):
                if component.id not in CPURenderer.COMPUTED_FRAMES:
                    CPURenderer.COMPUTED_FRAMES[component.id] = (
                        component.generate_frame()
                    )
                computed_frame = CPURenderer.COMPUTED_FRAMES[component.id]
                frame.paste(
                    computed_frame,
                    component.fixed_position(
                        frame.size,
                        (
                            computed_frame.size[0] + component.content_length,
                            computed_frame.size[1],
                        ),
                        component.style.font_size,
                    ),
                    mask=computed_frame,
                )

        return VideoFrame.from_image(frame)

    def render_frames(self):
        packets = []

        with open_container(
            self.output_filename, "w", format="mp4"
        ) as output_container:
            stream = output_container.add_stream(
                "libx264",
                rate=self.framerate,
                options={
                    "crf": "18",
                    "preset": "fast",
                    "pix_fmt": "yuv420p",
                },
            )

            stream.width = self.width  # type: ignore
            stream.height = self.height  # type: ignore
            stream.thread_type = "AUTO"
            stream.codec_context.time_base = Fraction(1, self.framerate)

            for i, frame in enumerate(self.iter_frames()):
                print("frame", i)
                frame.pts = i
                frame.dts = i
                output_container.mux(stream.encode(frame))  # type: ignore
                del frame

            packets.clear()

            output_container.mux(stream.encode(None))  # type: ignore
            output_container.close()

    def iter_frames(
        self,
    ) -> Iterable[VideoFrame]:
        total_frames = self.duration * self.framerate
        for frame_number in range(total_frames):
            frame = self.get_frame_at_time(frame_number / self.framerate)
            if frame is None:
                continue
            yield frame

    def process_audio(self):

        components = [
            component
            for component in self.timeline.composition.components
            if isinstance(component, Audio)
        ]
        with tempfile.TemporaryDirectory(dir=r".\tmp") as tmpdirname:
            for component in components:
                filepath = path.join(tmpdirname, f"{component.id}.mp3")
                audio_reader.extract_audio_from_video(
                    component.source,
                    component.start_at,
                    component.end_at,
                    filepath,
                )
                component.source = filepath

            audio_reader.merge_audio_files(components, "output.mp3")
            audio_reader.merge_audio_to_video(self.output_filename, "output.mp3", {})

    def __del__(self):
        # Ensure readers are freed at the end
        video_reader.free()
        audio_reader.free()
        CPURenderer.COMPUTED_FRAMES = {}
