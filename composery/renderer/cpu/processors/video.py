from PIL import Image

from composery.reader import video as reader


def process_frame(
    frame: Image.Image, source: str, time: float, position: tuple[int, int]
) -> Image.Image:
    """Get a frame from a video and paste it into another frame

    Args:
        frame (Image.Image): The frame to paste the video frame
        source (str): The video source
        time (float): The time to get the frame
        position (tuple[int, int]): The position to paste the video frame

    Returns:
        Image.Image: The frame with the video frame pasted
    """

    video_frame = reader.get_frame_from_video(source, time)
    if not video_frame:
        return frame

    video_frame = video_frame.to_image()
    frame.paste(video_frame, position)
    return frame
