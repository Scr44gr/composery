from typing import Literal
import unittest
from pydantic import ValidationError
from composery.components.component import Component
from composery.renderer.timeline import Timeline, Composition


class TestComponent(Component):
    """A simple test component class"""

    type: Literal["test"] = "test"
    start_at: Literal[0] = 0
    end_at: Literal[0] = 0


class TestTimeline(unittest.TestCase):
    def test_composition_builder_with_single_component(self):
        timeline = Timeline()
        component = TestComponent(duration=10)
        builder = timeline.add_composition([component])
        builder.with_duration(10).with_framerate(24).build()

        self.assertEqual(len(timeline._compositions), 1)
        self.assertEqual(timeline._compositions[0].duration, 10)
        self.assertEqual(timeline._compositions[0].framerate, 24)
        self.assertEqual(len(timeline._compositions[0].components), 1)
        self.assertEqual(timeline._compositions[0].components[0].duration, 10)

    def test_composition_builder_with_multiple_components(self):
        timeline = Timeline()
        component1 = TestComponent(duration=10)
        component2 = TestComponent(duration=20)
        builder = timeline.add_composition([component1, component2])
        builder.with_duration(30).with_framerate(24).build()

        self.assertEqual(len(timeline._compositions), 1)
        self.assertEqual(timeline._compositions[0].duration, 30)
        self.assertEqual(timeline._compositions[0].framerate, 24)
        self.assertEqual(len(timeline._compositions[0].components), 2)
        self.assertEqual(timeline._compositions[0].components[0].duration, 10)
        self.assertEqual(timeline._compositions[0].components[1].duration, 20)

    def test_composition_builder_without_duration(self):
        timeline = Timeline()
        component = TestComponent(duration=10)
        builder = timeline.add_composition([component])
        builder.with_framerate(24)

        with self.assertRaises(AssertionError):
            builder.build()

    def test_composition_builder_without_framerate(self):
        timeline = Timeline()
        component = TestComponent(duration=10)
        builder = timeline.add_composition([component])
        builder.with_duration(10)

        with self.assertRaises(AssertionError):
            builder.build()

    def test_composition_builder_without_components(self):
        timeline = Timeline()
        builder = timeline.add_composition([])
        builder.with_duration(10).with_framerate(24)

        with self.assertRaises(AssertionError):
            builder.build()

    def test_composition_duration_calculation(self):
        component1 = TestComponent(duration=10)
        component2 = TestComponent(duration=20)
        composition = Composition(components=[component1, component2], duration=0)
        self.assertEqual(composition.duration, 30)

    def test_invalid_duration(self):
        with self.assertRaises(ValidationError):
            Composition(components=[], duration=-10)

    def test_invalid_framerate(self):
        with self.assertRaises(ValidationError):
            Composition(components=[], framerate=-24)


# run command: python -m unittest discover tests -v
