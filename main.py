from composery import Timeline
from composery.components import Position, Text, Video

if __name__ == "__main__":
    timeline = Timeline()

    # Agregar el video
    video_component = Video(
        source="./assets/test-2.mp4",
        allow_audio=True,
        start_at=0,
        end_at=60,
        duration=60,
        width=1080,
        height=1920,
        z_index=0,
        position=Position(x="center", y="center"),
    )

    subtitles = [
        {"content": "ガンデスト大好き 🚀", "start_at": 0, "end_at": 5},
        {"content": "この動画を楽しんでください！ 🎉", "start_at": 5, "end_at": 10},
        {"content": "すべての人に感謝しています。 🙏", "start_at": 10, "end_at": 15},
        {"content": "一緒に楽しみましょう！ 😄", "start_at": 15, "end_at": 20},
        {"content": "またお会いしましょう！ 👋", "start_at": 20, "end_at": 60},
    ]

    composition = [video_component]
    for subtitle in subtitles:
        text_component = Text(
            content=subtitle["content"],
            start_at=subtitle["start_at"] + 1,
            end_at=subtitle["end_at"],
            duration=subtitle["end_at"] - subtitle["start_at"],
            z_index=1,
            position=Position(x="center", y="center"),
        )
        composition.append(text_component)  # type: ignore

    timeline.add_composition(composition).with_duration(10).with_framerate(
        60
    ).with_resolution(1920, 1080).build()

    timeline.render("./output.mp4")
