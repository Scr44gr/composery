from fractions import Fraction
from logging import getLogger
from time import perf_counter
from typing import Dict, Iterable, Optional, Sequence, Tuple, Type

import numpy as np
from av.audio.frame import AudioFrame
from av.container import open as open_container
from av.video.frame import VideoFrame
from PIL import Image

from ...components.text import Text
from ...components.video import Video
from ...reader import audio as audio_reader
from ...reader import free as free_readers
from ...reader import video as video_reader
from ..options import VideoWriterOptions
from ..timeline import Timeline

logger = getLogger(__name__)


class CPURenderer:
    __slots__ = (
        "output_filename",
        "width",
        "height",
        "framerate",
        "duration",
        "timeline",
        "options",
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
        options: VideoWriterOptions,
    ):
        self.output_filename = output_filename
        self.width = width
        self.height = height
        self.framerate = framerate
        self.duration = duration
        self.options = options
        self.BLANK_FRAME = np.zeros((height, width, 3), dtype=np.uint8)

    def render(self, timeline: Timeline):
        self.timeline = timeline
        self.render_frames()

    def get_audio_frame_at_time(self, time: float) -> Optional[AudioFrame]:
        audio_frame = None
        for audio_component in self.timeline.composition.audio_components:
            if time - 1 > self.duration or not (
                audio_component.start_at <= time <= audio_component.end_at
            ):
                continue
            raw_audio_frame = audio_reader.get_audio_frame_from_video(
                audio_component.source, time
            )
            if not raw_audio_frame:
                continue
            audio_frame = raw_audio_frame
        return audio_frame

    def get_frame_at_time(self, time: float) -> VideoFrame:
        frame = Image.fromarray(self.BLANK_FRAME)
        for component in self.timeline.composition.components:
            if not (component.start_at <= time <= component.end_at):
                continue
            frame_number = int(round((time - component.start_at) * self.framerate, 0))
            if isinstance(component, Video):
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

        with open_container(
            self.output_filename, "w", format="mp4"
        ) as output_container:
            video_stream = output_container.add_stream(
                codec_name="h264",
                rate=self.framerate,
                options={
                    "crf": str(self.options.crf),
                    "preset": self.options.preset.value,
                    "pix_fmt": self.options.pixel_format.value,
                },
            )
            assert self.options.audio_codec == "aac"
            audio_stream = output_container.add_stream(
                self.options.audio_codec,
                rate=self.options.audio_sample_rate,
            )
            video_stream.width = self.width  # type: ignore
            video_stream.height = self.height  # type: ignore
            video_stream.thread_type = "AUTO"
            video_stream.codec_context.time_base = Fraction(1, self.framerate)
            audio_stream.codec_context.time_base = Fraction(
                1, self.options.audio_sample_rate
            )
            for i, frame in enumerate(self.iter_frames()):
                frame.pts = i
                output_container.mux(video_stream.encode(frame))
                del frame

            for audio_frame in self.iter_audio_frames():
                assert audio_frame.pts is not None
                output_container.mux(audio_stream.encode(audio_frame))
                del audio_frame

            output_container.mux(video_stream.encode(None))
            output_container.close()

    def iter_frames(
        self,
    ) -> Iterable[VideoFrame]:
        video_frames = self.duration * self.framerate
        start_time = perf_counter()
        for frame_number in range(video_frames):
            video_frame = self.get_frame_at_time(frame_number / self.framerate)
            if video_frame is None:
                continue
            yield video_frame
        logger.debug(f"iter frames took {perf_counter() - start_time}")

    def iter_audio_frames(self) -> Iterable[AudioFrame]:
        audio_frames = int(self.duration * self.options.audio_sample_rate) // 1000
        for index in range(audio_frames):
            time = index / self.options.audio_sample_rate * 1000
            audio_frame = self.get_audio_frame_at_time(time)
            if audio_frame is None:
                continue
            yield audio_frame

    def __del__(self):
        free_readers()
        CPURenderer.COMPUTED_FRAMES = {}
