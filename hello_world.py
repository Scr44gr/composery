from composery import Timeline
from composery.components import Position, Text

if __name__ == "__main__":
    timeline = Timeline()
    composition = []
    text = Text(
        content="Hello world",
        position=Position(x="center", y="center"),
        start_at=0,
        duration=10,
    )
    composition.append(text)

    timeline.add_composition(composition).with_duration(10).with_framerate(
        24
    ).with_resolution(1280, 720).build()

    timeline.render("./output.mp4")
