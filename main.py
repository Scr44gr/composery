from composery.renderer.video import VideoComposer, VideoWriter
from composery.components.text import Text
from composery.components.video import Video


def main():
    video_composer = VideoComposer()

    video_writer = VideoWriter(
        command=video_composer.with_component(
            Video(
                width=1920,
                height=1080,
                source="./assets/test-video.mp4",
                start_at=0,
                end_at=10,
                duration=10,
            )
        )
        .with_component(
            Text(content="Hello, World!", start_at=0, end_at=2, duration=10)
        )
        .build_command(),
        video_composer=video_composer,
    )
    video_writer.write("./output.mp4")


if __name__ == "__main__":
    main()
