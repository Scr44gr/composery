import av
from numpy import array, ndarray, zeros
from PIL import Image, ImageDraw, ImageFont

from composery import Timeline
from composery.components import Text, Video
from composery.components.component import Position

if __name__ == "as":
    timeline = Timeline()

    timeline.add_composition(
        [
            Text(content="Hello, World!", start_at=0, end_at=10, duration=10),
            Video(
                source="test-video.mp4",
                start_at=10,
                end_at=60,
                duration=60,
                width=1080,
                height=1920,
            ),
        ]
    ).with_duration(30).with_framerate(24).build()

    text = Text(
        content="🔥 EL GEROME CACOSO 🔥 <:beauty:1129274453356970094>",
        position=Position(x="center", y="center"),
        start_at=0,
        end_at=10,
        duration=10,
    )
    frame = zeros((1080, 1920, 3), dtype="uint8")
    text_frame = text.generate_frame()
    Image.fromarray(text_frame).save("./text.jpeg")


if __name__ == "__main__":
    timeline = Timeline()

    # Agregar el video
    video_component = Video(
        source="./assets/gandesto.mp4",
        start_at=0,
        end_at=60,
        duration=60,
        width=1080,
        height=1920,
        z_index=0,
        position=Position(x="center", y="center"),
    )

    # Lista de subtítulos con sus tiempos de inicio y fin
    subtitles = [
        {"content": "ガンデスト大好き 🚀", "start_at": 0, "end_at": 5},
        {"content": "この動画を楽しんでください！ 🎉", "start_at": 5, "end_at": 10},
        {"content": "すべての人に感謝しています。 🙏", "start_at": 10, "end_at": 15},
        {"content": "一緒に楽しみましょう！ 😄", "start_at": 15, "end_at": 20},
        {"content": "またお会いしましょう！ 👋", "start_at": 20, "end_at": 25},
    ]

    # Agregar los subtítulos al timeline
    composition = [video_component]
    for subtitle in subtitles:
        text_component = Text(
            content=subtitle["content"],
            start_at=subtitle["start_at"] + 1,
            end_at=subtitle["end_at"],
            duration=subtitle["end_at"] - subtitle["start_at"],
            z_index=1,
            position=Position(x="center", y="bottom"),
        )
        composition.append(text_component)  # type: ignore

    # Agregar el video al timeline
    timeline.add_composition(composition).with_duration(60).with_framerate(24).build()

    # Configurar el timeline y renderizar
    timeline.render("./output.mp4")
