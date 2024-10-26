from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Preset(str, Enum):
    ultrafast = "ultrafast"
    superfast = "superfast"
    veryfast = "veryfast"
    faster = "faster"
    fast = "fast"
    medium = "medium"
    slow = "slow"
    slower = "slower"
    veryslow = "veryslow"


class PixelFormat(str, Enum):
    # TODO: Research more pixel formats
    rgb8 = "rgb8"
    rgb24 = "rgb24"
    yuv420p = "yuv420p"


SCALE_PATTERN = r"(\d+):(\d+)"


class VideoWriterOptions(BaseModel):
    width: int = Field(default=1920, description="The width of the video writer")
    height: int = Field(default=1080, description="The height of the video writer")
    framerate: int = Field(default=24, description="The framerate of the video writer")
    preset: Preset = Field(
        default=Preset.medium, description="The preset of the video writer"
    )
    crf: int = Field(
        default=23, description="The constant rate factor of the video writer"
    )
    scale: str = Field(
        default="1920:1080",
        pattern=SCALE_PATTERN,
        description="The scale of the video writer",
    )
    format: Literal["mp4", "gif"] = Field(
        default="mp4", description="The format of the video writer"
    )
    bitrate: str = Field(default="2000k", description="The bitrate of the video writer")
    codec: Literal["h264", "mpeg4"] = Field(
        default="h264", description="The codec of the video writer"
    )
    pixel_format: PixelFormat = Field(
        default=PixelFormat.yuv420p, description="The pixel format of the video writer"
    )
    audio_bitrate: str = Field(
        default="192k", description="The audio bitrate of the video writer"
    )
    audio_codec: Literal["pcm_s16le", "aac", "mp3", "mp2"] = Field(
        default="aac", description="The audio codec of the video writer"
    )
    audio_samples: int = Field(
        default=1024, description="The audio samples of the video writer"
    )
    audio_sample_rate: int = Field(default=44100, description="Audio sample rate")
    audio_channels: int = Field(default=2, description="Audio channels")


DEFAULT_OPTIONS = VideoWriterOptions()
