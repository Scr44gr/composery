import time as timer
from fractions import Fraction
from typing import Dict

import numpy as np
from av.container import open as open_container
from av.video.frame import VideoFrame
from imageio import get_reader
from PIL import Image

from ...components.text import Text
from ...components.video import Video
from ..timeline import Timeline


class CPURenderer:
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

    def get_frame_at_time(self, time: float) -> VideoFrame:
        frame = Image.fromarray(self.BLANK_FRAME)

        for component in self.timeline.composition.components:
            if not (component.start_at <= time <= component.end_at):
                continue
            frame_number = int(round((time - component.start_at) * self.framerate, 0))
            if isinstance(component, Video):
                try:
                    video_frame = self.get_video_frame(component.source, frame_number)
                    frame.paste(
                        Image.fromarray(video_frame),
                        component.fixed_position(
                            frame.size,
                            (video_frame.shape[1], video_frame.shape[0]),
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

    def get_video_frame(self, source: str, frame_num: int) -> np.ndarray:
        if source in CPURenderer.READERS:
            reader = CPURenderer.READERS[source]
        else:
            reader = get_reader(source)
            CPURenderer.READERS[source] = reader
        return reader.get_data(frame_num)

    def render_frames(self):
        current_pts: int = 0
        total_frames: int = self.duration * self.framerate
        packets = []

        with open_container(self.output_filename, "w", format="mp4") as container:
            stream = container.add_stream(
                "libx264",
                rate=self.framerate,
                options={
                    "crf": "18",
                    "preset": "medium",
                    "pix_fmt": "yuv420p",
                },
            )
            stream.width = self.width  # type: ignore
            stream.height = self.height  # type: ignore
            stream.thread_type = "AUTO"
            stream.codec_context.time_base = Fraction(1, self.framerate)
            start_time = timer.perf_counter()
            for frame_number in range(total_frames):
                start_time = timer.perf_counter()
                frame = self.get_frame_at_time(frame_number / self.framerate)
                print(f"Frame {frame_number} took {timer.perf_counter() - start_time}")
                if frame is None:
                    continue
                current_pts += 1
                for packet in stream.encode(frame):  # type: ignore
                    packets.append(packet)

            container.mux(packets)
            for packet in stream.encode(None):  # type: ignore
                container.mux(packet)
            container.close()

    def __del__(self):
        for reader in CPURenderer.READERS.values():
            reader.close()
        CPURenderer.READERS = {}
        CPURenderer.COMPUTED_FRAMES = {}
