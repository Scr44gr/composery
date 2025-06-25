<p align="center">
    <img width="248" height="250" src="https://github.com/user-attachments/assets/31828009-02b7-442b-9e70-7d1c4c04d53e" alt="Composery logo">
</p>

# Composery

[Composery](https://github.com/Scr44gr/composery) is a library to create/edit videos in a fast and easy way using python, an alternative to the famous [MoviePy](https://github.com/Zulko/moviepy) library.

> ⚠️ we are in a very early development stage so the api will probably change in the near future.

## Quickstart
To install `composery` use this command

```bash
pip install git+https://github.com/Scr44gr/composery.git
```

Then you can create your first "Hello World" video:

```python
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

```
