from fractions import Fraction
from time import perf_counter
from typing import Dict, Iterable, Optional

import numpy as np
from av.audio.frame import AudioFrame
from av.container import open as open_container
from av.video.frame import VideoFrame
from PIL import Image

from composery.components import Text, Video
from composery.logger import logger
from composery.reader import audio as audio_reader
from composery.reader import free as free_readers
from composery.reader.video import get_video_size
from composery.renderer.options import VideoWriterOptions
from composery.renderer.processors import video
from composery.timeline import Timeline


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
        "BLANK_AUDIO_FRAME",
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
        self.BLANK_AUDIO_FRAME = AudioFrame(
            format="fltp", layout="stereo", samples=self.options.audio_samples
        )
        self.BLANK_AUDIO_FRAME.sample_rate = self.options.audio_sample_rate

    def render(self, timeline: Timeline):
        self.timeline = timeline
        self.render_frames()

    def get_audio_frame_at_time(self, time: float, index: int) -> Optional[AudioFrame]:
        audio_frame = self.BLANK_AUDIO_FRAME
        for audio_component in self.timeline.composition.audio_components:
            if time > self.duration or not (
                audio_component.start_at <= time <= audio_component.end_at
            ):
                continue
            raw_audio_frame = audio_reader.get_audio_frame_from_video(
                audio_component.source, time
            )
            if not raw_audio_frame:
                continue
            audio_frame = raw_audio_frame
        audio_frame.rate = self.options.audio_sample_rate
        audio_frame.time_base = Fraction(1, self.options.audio_sample_rate)
        audio_frame.pts = int(index * self.options.audio_samples)
        return audio_frame

    def get_frame_at_time(self, time: float) -> VideoFrame:
        frame = Image.fromarray(self.BLANK_FRAME)
        for component in self.timeline.composition.components:
            if time > self.duration or not (
                component.start_at <= time <= component.end_at
            ):
                continue

            frame_time = time - component.start_at
            if isinstance(component, Video):

                video.process_frame(
                    frame,
                    component.source,
                    frame_time,
                    component.fixed_position(
                        frame.size,
                        get_video_size(component.source),
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
            video_stream.bit_rate = int(self.options.bitrate[:-1]) * 1000
            audio_stream.codec_context.time_base = Fraction(
                1, self.options.audio_sample_rate
            )
            audio_stream.bit_rate = int(self.options.audio_bitrate[:-1]) * 1000
            for i, frame in enumerate(self.iter_frames()):
                frame.pts = i
                output_container.mux(video_stream.encode(frame))
                del frame

            for i, audio_frame in enumerate(self.iter_audio_frames()):
                if audio_frame is None:
                    continue
                output_container.mux(audio_stream.encode(audio_frame))
                del audio_frame
            output_container.mux(video_stream.encode(None))
            output_container.mux(audio_stream.encode(None))
            output_container.close()

    def iter_frames(
        self,
    ) -> Iterable[VideoFrame]:
        video_frames = self.duration * self.framerate
        for frame_number in range(video_frames):
            video_frame = self.get_frame_at_time(frame_number / self.framerate)
            if video_frame is None:
                continue
            yield video_frame

    def iter_audio_frames(self) -> Iterable[AudioFrame]:
        audio_frames = (
            int(self.duration * self.options.audio_sample_rate) // 1000
        ) - self.duration
        for index in range(audio_frames):
            time = index / self.options.audio_sample_rate * 1000
            audio_frame = self.get_audio_frame_at_time(time, index)
            if audio_frame is None:
                continue
            yield audio_frame

    def __del__(self):
        free_readers()
        CPURenderer.COMPUTED_FRAMES = {}
