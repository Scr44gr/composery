from pydantic import BaseModel, Field
from enum import Enum


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


class VideoOutputFormat(str, Enum):
    mp4 = "mp4"
    avi = "avi"
    mkv = "mkv"
    mov = "mov"
    webm = "webm"
    gif = "gif"


class VideoOutputCodec(str, Enum):
    """Video output codecs

    - libx264: H.264 codec
    - libx265: H.265 codec
    - libvpx: VP8 codec
    - libvpx_vp9: VP9 codec
    - libaom_av1: AV1 codec
    - libxvid: Xvid codec
    - mpeg4: MPEG-4 codec
    - h264_nvenc: NVIDIA NVENC H.264 codec
    - hevc_nvenc: NVIDIA NVENC H.265 codec
    - vp9_vaapi: VP9 codec with VA-API acceleration
    - av1_vaapi: AV1 codec with VA-API acceleration
    """

    libx264 = "libx264"
    libx265 = "libx265"
    libvpx = "libvpx"
    libvpx_vp9 = "libvpx-vp9"
    libaom_av1 = "libaom-av1"
    libxvid = "libxvid"
    mpeg4 = "mpeg4"
    h264_nvenc = "h264_nvenc"
    hevc_nvenc = "hevc_nvenc"
    vp9_vaapi = "vp9_vaapi"
    av1_vaapi = "av1_vaapi"


class PixelFormat(str, Enum):
    # TODO: Research more pixel formats
    rgb8 = "rgb8"
    rgb24 = "rgb24"
    yuv420p = "yuv420p"


SCALE_PATTERN = r"(\d+):(\d+)"


class VideoWriterOptions(BaseModel):
    preset: Preset = Field(
        default=Preset.medium, description="The preset of the video writer"
    )
    crf: int = Field(
        default=23, description="The constant rate factor of the video writer"
    )
    fps: int = Field(
        default=24, description="The frames per second of the video writer"
    )
    scale: str = Field(
        default="1920:1080",
        pattern=SCALE_PATTERN,
        description="The scale of the video writer",
    )
    format: VideoOutputFormat = Field(
        default=VideoOutputFormat.mp4, description="The format of the video writer"
    )
    bitrate: str = Field(default="1M", description="The bitrate of the video writer")
    codec: VideoOutputCodec = Field(
        default=VideoOutputCodec.libx264, description="The codec of the video writer"
    )
    pixel_format: PixelFormat = Field(
        default=PixelFormat.yuv420p, description="The pixel format of the video writer"
    )

    @property
    def ffmpeg_command(self) -> str:
        return f"-preset {self.preset} -crf {self.crf} -r {self.fps} -c:v {self.codec} -pix_fmt {self.pixel_format} -b:v {self.bitrate}"


DEFAULT_OPTIONS = VideoWriterOptions()
