from os import path
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
from typing import List

from imageio_ffmpeg import get_ffmpeg_exe

from ..components.audio import Audio

FFMPEG_EXE = get_ffmpeg_exe()

TEMP_DIR = TemporaryDirectory(dir=r".\tmp")


def convert_s_to_hms(seconds: int | float) -> str:
    """Convert seconds to hours, minutes, and seconds.

    Args:
        seconds (int | float): The number of seconds

    Returns:
        str: The time in the format HH:MM:SS
    """
    assert seconds >= 0, "The number of seconds must be greater than or equal to 0."
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def extract_audio_from_video(
    video_path: str, start_time: int | float, end_time: int | float, output_path: str
) -> str:
    """Extract audio from a video file.

    Args:
        video_path (str): The path to the video file
        start_time (int | float): The start time in seconds
        end_time (int | float): The end time in seconds
        output_path (str): The path to the output audio file
    """
    duration = end_time - start_time

    if duration <= 0:
        raise ValueError("The duration must be greater than 0.")

    command = [
        "-y",
        "-ss",
        convert_s_to_hms(start_time),
        "-i",
        video_path,
        "-t",
        convert_s_to_hms(duration),
        output_path,
    ]

    with Popen(command, executable=FFMPEG_EXE, stdout=PIPE, stderr=PIPE) as process:
        process.communicate()
        if process.returncode != 0:
            raise ValueError("The audio extraction failed.")

    return output_path


def merge_audio_files(audio_components: List[Audio], output_path: str) -> str:
    """Compose audio files into one audio file.

    Args:
        audio_paths (list[str]): The paths to the audio files
        output_path (str): The path to the output audio file
    """
    output_path = path.join(TEMP_DIR.name, output_path)
    command = ["-y"]
    for audio in audio_components:
        assert audio.path, "The audio source must be set."
        command.extend(
            [
                "-i",
                audio.path,
                "-ss",
                convert_s_to_hms(audio.start_at),
                "-t",
                convert_s_to_hms(audio.duration),
            ]
        )
    command.extend(
        ["-filter_complex", f"concat=n={len(audio_components)}:v=0:a=1", output_path]
    )

    with Popen(command, executable=FFMPEG_EXE, stdout=PIPE, stderr=PIPE) as process:
        process.communicate()
        if process.returncode != 0:
            raise ValueError("The audio composing failed.")
    return output_path


def merge_audio_to_video(video_path: str, audio_path: str, options: dict):
    """Merge an audio file with a video file.

    Args:
        video_path (str): The path to the video file
        audio_path (str): The path to the audio file
        output_path (str): The path to the output video file
        options (dict): The options for the merging process
    """
    audio_path = path.join(TEMP_DIR.name, audio_path)
    command = [
        "-y",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-filter_complex",
        f"[0:a][1:a]amerge=inputs=2[a]",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        "-strict",
        "experimental",
        "-b:a",
        "192k",
    ]
    command.append("./final-output.mp4")

    with Popen(command, executable=FFMPEG_EXE, stdout=PIPE, stderr=PIPE) as process:
        process.communicate()
        if process.returncode != 0:
            raise ValueError("The audio composing failed.")


def free():
    TEMP_DIR.cleanup()


__all__ = ["extract_audio_from_video", "merge_audio_files", "free"]
