import shutil

import numpy as np
from manim import *

LATEX_AVAILABLE = shutil.which("latex") is not None


def make_label(latex: str, plain: str | None = None, font_size: int = 36) -> Mobject:
    """Render math with MathTex when LaTeX is installed, else readable Text."""
    if LATEX_AVAILABLE:
        return MathTex(latex, font_size=font_size)
    return Text(plain if plain is not None else latex, font_size=font_size)


class SinExplainer(Scene):
    def construct(self):
        self.act_title()
        circle_group, graph_group, tracker = self.act_build_circle()
        self.act_link_circle_to_graph(circle_group, graph_group, tracker)
        self.act_key_values(circle_group, graph_group, tracker)
        self.act_summary()

    def act_title(self):
        title = make_label(
            r"\text{What is } \sin(x)\text{?}",
            plain="What is sin(x)?",
            font_size=52,
        )
        subtitle = Text("The height on the unit circle", font_size=32, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(FadeIn(title, shift=UP * 0.3), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=1)

    def act_build_circle(self):
        circle_axes = Axes(
            x_range=[-1.5, 1.5, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=4.5,
            y_length=4.5,
            axis_config={"include_tip": False, "font_size": 24},
        )
        circle_axes_labels = circle_axes.get_axis_labels(
            x_label=make_label("x", font_size=28),
            y_label=make_label("y", font_size=28),
        )

        unit_circle = Circle(radius=circle_axes.x_axis.get_unit_size(), color=BLUE)
        unit_circle.move_to(circle_axes.c2p(0, 0))

        origin_label = make_label("O", font_size=28).next_to(
            circle_axes.c2p(0, 0), DL, buff=0.15
        )
        radius_label = make_label("1", font_size=24).next_to(
            circle_axes.c2p(0.5, 0.5), UR, buff=0.1
        )

        tracker = ValueTracker(PI / 4)

        radius_line = always_redraw(
            lambda: DashedLine(
                circle_axes.c2p(0, 0),
                circle_axes.c2p(np.cos(tracker.get_value()), np.sin(tracker.get_value())),
                color=WHITE,
                dash_length=0.08,
            )
        )

        point_dot = always_redraw(
            lambda: Dot(
                circle_axes.c2p(np.cos(tracker.get_value()), np.sin(tracker.get_value())),
                color=YELLOW,
                radius=0.08,
            )
        )

        angle_arc = always_redraw(
            lambda: Arc(
                radius=0.45,
                start_angle=0,
                angle=tracker.get_value(),
                arc_center=circle_axes.c2p(0, 0),
                color=GREEN,
            )
        )

        angle_label = always_redraw(
            lambda: make_label("x", font_size=28).move_to(
                circle_axes.c2p(
                    0.55 * np.cos(tracker.get_value() / 2),
                    0.55 * np.sin(tracker.get_value() / 2),
                )
            )
        )

        sin_line = always_redraw(
            lambda: Line(
                circle_axes.c2p(np.cos(tracker.get_value()), 0),
                circle_axes.c2p(
                    np.cos(tracker.get_value()),
                    np.sin(tracker.get_value()),
                ),
                color=YELLOW,
                stroke_width=5,
            )
        )

        sin_label = always_redraw(
            lambda: make_label(r"\sin(x)", plain="sin(x)", font_size=28)
            .set_color(YELLOW)
            .next_to(
                circle_axes.c2p(
                    np.cos(tracker.get_value()),
                    np.sin(tracker.get_value()) / 2,
                ),
                RIGHT,
                buff=0.15,
            )
        )

        circle_panel_title = Text("Unit circle", font_size=30).next_to(
            circle_axes, UP, buff=0.3
        )

        circle_group = VGroup(
            circle_panel_title,
            circle_axes,
            circle_axes_labels,
            unit_circle,
            origin_label,
            radius_label,
            radius_line,
            angle_arc,
            angle_label,
            sin_line,
            sin_label,
            point_dot,
        )

        graph_axes = Axes(
            x_range=[0, TAU, PI / 2],
            y_range=[-1.3, 1.3, 1],
            x_length=5.5,
            y_length=4.5,
            axis_config={"include_tip": False, "font_size": 24},
            tips=False,
        )
        graph_axes_labels = graph_axes.get_axis_labels(
            x_label=make_label("x", font_size=28),
            y_label=make_label(r"\sin(x)", plain="sin(x)", font_size=28),
        )
        graph_panel_title = Text("Sine graph", font_size=30).next_to(
            graph_axes, UP, buff=0.3
        )
        graph_group = VGroup(graph_panel_title, graph_axes, graph_axes_labels)

        panels = VGroup(circle_group, graph_group).arrange(RIGHT, buff=1.2)
        panels.to_edge(DOWN, buff=0.5)

        self.play(
            FadeIn(circle_panel_title),
            Create(circle_axes),
            FadeIn(circle_axes_labels),
            Create(unit_circle),
            FadeIn(origin_label),
            FadeIn(radius_label),
            run_time=2,
        )
        self.play(
            Create(radius_line),
            Create(angle_arc),
            FadeIn(angle_label),
            FadeIn(point_dot),
            run_time=2,
        )
        self.play(Create(sin_line), FadeIn(sin_label), run_time=2)
        self.wait(1)

        self.play(
            FadeIn(graph_panel_title),
            Create(graph_axes),
            FadeIn(graph_axes_labels),
            run_time=2,
        )
        self.wait(0.5)

        return circle_group, graph_group, tracker

    def act_link_circle_to_graph(self, circle_group, graph_group, tracker):
        circle_axes = circle_group[1]
        graph_axes = graph_group[1]

        graph_dot = always_redraw(
            lambda: Dot(
                graph_axes.c2p(tracker.get_value(), np.sin(tracker.get_value())),
                color=YELLOW,
                radius=0.08,
            )
        )

        projection_line = always_redraw(
            lambda: DashedLine(
                circle_axes.c2p(
                    np.cos(tracker.get_value()),
                    np.sin(tracker.get_value()),
                ),
                graph_axes.c2p(tracker.get_value(), np.sin(tracker.get_value())),
                color=GRAY_B,
                dash_length=0.08,
                stroke_width=2,
            )
        )

        trace = TracedPath(
            graph_dot.get_center,
            stroke_color=BLUE,
            stroke_width=4,
            dissipating_time=None,
        )

        circle_group.add(projection_line, graph_dot, trace)

        self.add(projection_line, graph_dot, trace)
        tracker.set_value(0)

        self.play(
            tracker.animate.set_value(TAU),
            run_time=20,
            rate_func=linear,
        )
        self.wait(1)

    def act_key_values(self, circle_group, graph_group, tracker):
        circle_axes = circle_group[1]
        graph_axes = graph_group[1]

        key_angles = [
            (0, r"\sin(0) = 0", "sin(0) = 0"),
            (PI / 2, r"\sin\left(\frac{\pi}{2}\right) = 1", "sin(π/2) = 1"),
            (PI, r"\sin(\pi) = 0", "sin(π) = 0"),
            (3 * PI / 2, r"\sin\left(\frac{3\pi}{2}\right) = -1", "sin(3π/2) = −1"),
        ]

        for angle, label_text, plain_text in key_angles:
            tracker.set_value(angle)

            circle_highlight = Dot(
                circle_axes.c2p(np.cos(angle), np.sin(angle)),
                color=YELLOW,
                radius=0.12,
            )
            graph_highlight = Dot(
                graph_axes.c2p(angle, np.sin(angle)),
                color=YELLOW,
                radius=0.12,
            )
            label = make_label(label_text, plain=plain_text, font_size=32).to_edge(
                UP, buff=0.5
            )

            self.play(
                FadeIn(circle_highlight),
                FadeIn(graph_highlight),
                FadeIn(label),
                run_time=0.6,
            )
            self.play(
                Indicate(circle_highlight, color=YELLOW),
                Indicate(graph_highlight, color=YELLOW),
                run_time=0.8,
            )
            self.play(
                FadeOut(circle_highlight),
                FadeOut(graph_highlight),
                FadeOut(label),
                run_time=0.4,
            )

        self.wait(0.5)

    def act_summary(self):
        takeaway = Text(
            "sin(x) = y-coordinate of a point on the unit circle",
            font_size=34,
        )
        takeaway.to_edge(UP, buff=0.8)

        self.play(FadeIn(takeaway, shift=DOWN * 0.2), run_time=1.5)
        self.wait(2.5)
        self.play(FadeOut(takeaway), run_time=1)
