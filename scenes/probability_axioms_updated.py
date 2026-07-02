import shutil

import numpy as np
from manim import *

LATEX_AVAILABLE = shutil.which("latex") is not None

BOARD_CENTER = LEFT * 2.2
BOARD_WIDTH = 5.2
BOARD_HEIGHT = 3.6


def make_label(latex: str, plain: str | None = None, font_size: int = 36) -> Mobject:
    if LATEX_AVAILABLE:
        return MathTex(latex, font_size=font_size)
    return Text(plain if plain is not None else latex, font_size=font_size)


def caption(text: str) -> Text:
    return Text(text, font_size=26, color=GRAY_B)


def make_board() -> RoundedRectangle:
    board = RoundedRectangle(
        width=BOARD_WIDTH,
        height=BOARD_HEIGHT,
        corner_radius=0.18,
        color=WHITE,
        stroke_width=3,
    )
    board.move_to(BOARD_CENTER)
    return board


def make_meter(height: float = 3.2) -> VGroup:
    frame = Rectangle(width=0.35, height=height, color=GRAY_C, stroke_width=2)
    fill = Rectangle(width=0.35, height=0.01, color=YELLOW, fill_opacity=0.9, stroke_width=0)
    fill.align_to(frame, DOWN)
    label = Text("P", font_size=24).next_to(frame, UP, buff=0.15)
    value = Text("0", font_size=22).next_to(frame, RIGHT, buff=0.2)
    return VGroup(frame, fill, label, value)


def set_meter(meter: VGroup, probability: float, run_time: float = 0.8):
    frame, fill, label, value = meter
    max_height = frame.height
    target_height = max(0.01, probability * max_height)
    new_fill = Rectangle(
        width=fill.width,
        height=target_height,
        color=YELLOW,
        fill_opacity=0.9,
        stroke_width=0,
    )
    new_fill.align_to(frame, DOWN)
    new_value = Text(f"{probability:.2f}", font_size=22).move_to(value)
    return AnimationGroup(
        Transform(fill, new_fill),
        Transform(value, new_value),
        lag_ratio=0,
        run_time=run_time,
    )


def board_point(x_frac: float, y_frac: float) -> np.ndarray:
    """Map normalized board coordinates in [0,1] to scene coordinates."""
    left = BOARD_CENTER[0] - BOARD_WIDTH / 2
    bottom = BOARD_CENTER[1] - BOARD_HEIGHT / 2
    return np.array([left + x_frac * BOARD_WIDTH, bottom + y_frac * BOARD_HEIGHT, 0])


def region_rect(
    x0: float, y0: float, x1: float, y1: float, color: ManimColor, opacity: float = 0.55
) -> Rectangle:
    rect = Rectangle(
        width=(x1 - x0) * BOARD_WIDTH,
        height=(y1 - y0) * BOARD_HEIGHT,
        color=color,
        fill_color=color,
        fill_opacity=opacity,
        stroke_width=2,
    )
    center = board_point((x0 + x1) / 2, (y0 + y1) / 2)
    rect.move_to(center)
    return rect


def make_dart(color: ManimColor = RED) -> VGroup:
    tip = Triangle(color=color, fill_opacity=1).scale(0.12)
    tip.rotate(-PI / 2)
    shaft = Line(ORIGIN, RIGHT * 0.35, color=color, stroke_width=4)
    shaft.next_to(tip, RIGHT, buff=0)
    return VGroup(tip, shaft)


class ProbabilityFromAxioms(Scene):
    def construct(self):
        self.act_hook()
        board, meter, omega_label, dart = self.act_sample_space()
        self.act_axiom_non_negative()
        self.act_axiom_normalization()
        self.act_axiom_additivity()
        self.act_law_empty_set()
        self.act_law_complement()
        self.act_law_monotonicity()
        self.act_law_inclusion_exclusion()
        self.act_finale(board, meter, omega_label, dart)

    def show_banner(self, title: str, subtitle: str):
        banner_title = Text(title, font_size=40)
        banner_sub = caption(subtitle)
        banner_sub.next_to(banner_title, DOWN, buff=0.3)
        group = VGroup(banner_title, banner_sub).to_edge(UP, buff=0.45)
        self.play(FadeIn(group, shift=DOWN * 0.2), run_time=0.8)
        return group

    def act_hook(self):
        board = make_board()
        board.set_fill(color=BLUE_E, opacity=0.15)
        dart = make_dart()
        dart.move_to(board.get_top() + UP * 0.8)

        title = Text("Probability Laws", font_size=50, color=YELLOW)
        subtitle = caption("Built from three simple rules about a landing board")
        subtitle.next_to(title, DOWN, buff=0.35)
        title_group = VGroup(title, subtitle)

        self.play(FadeIn(title_group), run_time=1)
        self.play(FadeIn(board), run_time=0.8)
        self.play(dart.animate.move_to(board.get_center() + UP * 0.3), run_time=1.2)
        self.play(
            dart.animate.rotate(-PI / 6).shift(DOWN * 0.6),
            run_time=0.5,
        )
        self.play(
            dart.animate.move_to(board_point(0.62, 0.58)).rotate(PI / 6),
            run_time=0.9,
        )
        landing = Dot(board_point(0.62, 0.58), color=RED, radius=0.07)
        ripple = Circle(radius=0.08, color=RED, stroke_width=3).move_to(landing)
        self.play(FadeIn(landing), GrowFromCenter(ripple), run_time=0.5)
        self.play(ripple.animate.scale(2.5).set_stroke(opacity=0), run_time=0.6)
        self.wait(0.5)
        self.play(
            FadeOut(title_group),
            FadeOut(board),
            FadeOut(dart),
            FadeOut(landing),
            FadeOut(ripple),
            run_time=0.8,
        )

    def act_sample_space(self):
        banner = self.show_banner(
            "The landing board",
            "Every outcome is a point on the board. The whole board is Ω.",
        )

        board = make_board()
        board.set_fill(color=BLUE_E, opacity=0.12)
        omega_label = make_label(r"\Omega", plain="Ω", font_size=42).next_to(board, UP, buff=0.2)
        meter = make_meter().to_edge(RIGHT, buff=0.8)

        grid = VGroup()
        for i in range(1, 4):
            x = board.get_left()[0] + i * BOARD_WIDTH / 4
            grid.add(
                Line(
                    [x, board.get_bottom()[1], 0],
                    [x, board.get_top()[1], 0],
                    color=GRAY_D,
                    stroke_width=1,
                )
            )
        for j in range(1, 3):
            y = board.get_bottom()[1] + j * BOARD_HEIGHT / 3
            grid.add(
                Line(
                    [board.get_left()[0], y, 0],
                    [board.get_right()[0], y, 0],
                    color=GRAY_D,
                    stroke_width=1,
                )
            )

        dart = make_dart().move_to(board.get_center() + UP * 1.2)

        self.play(Create(board), FadeIn(omega_label), FadeIn(meter), Create(grid), run_time=1.5)
        self.play(dart.animate.move_to(board.get_center()), run_time=1)
        self.play(Indicate(omega_label, color=YELLOW), board.animate.set_fill(opacity=0.25), run_time=1)
        self.wait(0.5)

        self.banner = banner
        self.board = board
        self.meter = meter
        self.grid = grid
        self.dart = dart
        return board, meter, omega_label, dart

    def act_axiom_non_negative(self):
        self.play(FadeOut(self.banner), run_time=0.4)
        banner = self.show_banner(
            "Axiom 1 — No negative area",
            "Any event A covers some portion of the board, never less than zero.",
        )

        region_a = region_rect(0.12, 0.18, 0.52, 0.72, BLUE)
        label_a = make_label("A", font_size=34, plain="A").next_to(region_a, LEFT, buff=0.15)
        formula = make_label(r"P(A)\ge 0", plain="P(A) ≥ 0", font_size=34)
        formula.to_edge(RIGHT, buff=0.55).shift(UP * 1.2)

        self.play(FadeIn(region_a), FadeIn(label_a), FadeIn(formula), run_time=1)
        self.play(self.play_meter(0.35), run_time=0.8)
        self.play(Indicate(region_a, color=BLUE), run_time=0.8)

        ghost = region_rect(0.55, 0.2, 0.88, 0.45, RED, opacity=0.2)
        cross = Cross(ghost, stroke_color=RED, stroke_width=6)
        neg_label = caption("Impossible: negative area").next_to(ghost, DOWN, buff=0.15)
        self.play(FadeIn(ghost), Create(cross), FadeIn(neg_label), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(ghost), FadeOut(cross), FadeOut(neg_label), run_time=0.5)

        self.region_a = region_a
        self.label_a = label_a
        self.formula1 = formula
        self.banner = banner

    def act_axiom_normalization(self):
        self.play(FadeOut(self.banner), run_time=0.4)
        banner = self.show_banner(
            "Axiom 2 — The whole board counts as 1",
            "All possible outcomes together use 100% of the board.",
        )

        glow = self.board.copy()
        glow.set_stroke(color=YELLOW, width=6)
        formula = make_label(r"P(\Omega)=1", plain="P(Ω) = 1", font_size=36)
        formula.next_to(self.meter, UP, buff=0.55)

        self.play(
            self.board.animate.set_fill(color=YELLOW, opacity=0.2),
            ShowPassingFlash(glow, time_width=0.6),
            FadeIn(formula),
            run_time=1.2,
        )
        self.play(self.play_meter(1.0), run_time=1)
        self.play(Indicate(self.board, color=YELLOW), run_time=0.8)
        self.wait(0.5)

        self.formula2 = formula
        self.banner = banner

    def act_axiom_additivity(self):
        self.play(
            FadeOut(self.banner),
            FadeOut(self.region_a),
            FadeOut(self.label_a),
            FadeOut(self.formula1),
            FadeOut(self.formula2),
            run_time=0.5,
        )
        banner = self.show_banner(
            "Axiom 3 — Add areas that do not overlap",
            "If events are disjoint, total area is the sum of parts.",
        )

        tile_a = region_rect(0.08, 0.15, 0.28, 0.85, BLUE, opacity=0.65)
        tile_b = region_rect(0.32, 0.15, 0.52, 0.85, GREEN, opacity=0.65)
        tile_c = region_rect(0.56, 0.15, 0.76, 0.85, TEAL, opacity=0.65)
        labels = VGroup(
            make_label("A_1", plain="A₁", font_size=28).move_to(tile_a),
            make_label("A_2", plain="A₂", font_size=28).move_to(tile_b),
            make_label("A_3", plain="A₃", font_size=28).move_to(tile_c),
        )

        bars = VGroup()
        bar_colors = [BLUE, GREEN, TEAL]
        values = [0.18, 0.18, 0.18]
        for i, (val, col) in enumerate(zip(values, bar_colors)):
            bar = Rectangle(width=0.5, height=val * 2.5, color=col, fill_opacity=0.8, stroke_width=0)
            bar.move_to(self.meter[0].get_center() + RIGHT * (1.2 + i * 0.7) + DOWN * (1.25 - val * 1.25))
            bars.add(bar)

        formula = make_label(
            r"P(A_1\cup A_2\cup A_3)=P(A_1)+P(A_2)+P(A_3)",
            plain="P(A₁ ∪ A₂ ∪ A₃) = P(A₁) + P(A₂) + P(A₃)",
            font_size=28,
        )
        formula.to_edge(RIGHT, buff=0.35).shift(DOWN * 1.5)

        self.play(
            LaggedStart(*[FadeIn(tile) for tile in [tile_a, tile_b, tile_c]], lag_ratio=0.25),
            FadeIn(labels),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.2),
            run_time=1.2,
        )
        self.play(self.play_meter(0.54), FadeIn(formula), run_time=1)
        self.wait(0.8)

        self.tiles = VGroup(tile_a, tile_b, tile_c, labels, bars, formula)
        self.banner = banner

    def act_law_empty_set(self):
        self.play(FadeOut(self.banner), FadeOut(self.tiles), run_time=0.5)
        banner = self.show_banner(
            "Law 1 — The empty event has zero area",
            "An impossible landing zone cannot take up space.",
        )

        tiny = Circle(radius=0.06, color=GRAY_B, stroke_width=2).move_to(
            board_point(0.9, 0.12)
        )
        empty_label = make_label(r"\varnothing", plain="∅", font_size=30).next_to(tiny, UP, buff=0.1)
        formula = make_label(r"P(\varnothing)=0", plain="P(∅) = 0", font_size=34)
        formula.to_edge(RIGHT, buff=0.5).shift(UP * 0.5)

        self.play(FadeIn(tiny), FadeIn(empty_label), FadeIn(formula), run_time=0.8)
        self.play(tiny.animate.scale(0.2).set_opacity(0), run_time=0.8)
        self.play(self.play_meter(0.0), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(tiny), FadeOut(empty_label), FadeOut(formula), run_time=0.4)
        self.banner = banner

    def act_law_complement(self):
        self.play(FadeOut(self.banner), run_time=0.4)
        banner = self.show_banner(
            "Law 2 — What is left over fills the rest",
            "Event A and its complement split the whole board.",
        )

        region_a = region_rect(0.08, 0.12, 0.46, 0.88, BLUE, opacity=0.7)
        region_ac = region_rect(0.46, 0.12, 0.92, 0.88, ORANGE, opacity=0.45)
        divider = Line(
            board_point(0.46, 0.12), board_point(0.46, 0.88), color=WHITE, stroke_width=3
        )
        label_a = make_label("A", font_size=32).move_to(region_a)
        label_ac = make_label("A^c", plain="Aᶜ", font_size=32).move_to(region_ac)

        puzzle_arrow = Arrow(
            region_a.get_right() + RIGHT * 0.1,
            region_ac.get_left() + LEFT * 0.1,
            color=YELLOW,
            buff=0.1,
        )
        formula = make_label(r"P(A^c)=1-P(A)", plain="P(Aᶜ) = 1 − P(A)", font_size=32)
        formula.to_edge(RIGHT, buff=0.45).shift(UP * 0.3)

        self.play(FadeIn(region_a), FadeIn(region_ac), Create(divider), run_time=1)
        self.play(FadeIn(label_a), FadeIn(label_ac), run_time=0.6)
        self.play(self.play_meter(0.38), run_time=0.7)
        self.play(GrowArrow(puzzle_arrow), FadeIn(formula), run_time=0.8)
        self.play(
            region_a.animate.shift(LEFT * 0.05),
            region_ac.animate.shift(RIGHT * 0.05),
            run_time=0.8,
        )
        self.play(
            region_a.animate.shift(RIGHT * 0.05),
            region_ac.animate.shift(LEFT * 0.05),
            FadeOut(puzzle_arrow),
            run_time=0.8,
        )
        self.wait(0.5)

        self.complement_group = VGroup(region_a, region_ac, divider, label_a, label_ac, formula)
        self.banner = banner

    def act_law_monotonicity(self):
        self.play(FadeOut(self.banner), FadeOut(self.complement_group), run_time=0.5)
        banner = self.show_banner(
            "Law 3 — Bigger region, bigger probability",
            "If A lies completely inside B, then P(A) ≤ P(B).",
        )

        outer = Circle(radius=1.05, color=GREEN, fill_color=GREEN, fill_opacity=0.35)
        inner = Circle(radius=0.55, color=BLUE, fill_color=BLUE, fill_opacity=0.65)
        outer.move_to(BOARD_CENTER)
        inner.move_to(BOARD_CENTER + LEFT * 0.15 + DOWN * 0.1)

        label_b = make_label("B", font_size=34).next_to(outer, UP, buff=0.1)
        label_a = make_label("A", font_size=30).move_to(inner)

        brace = BraceBetweenPoints(inner.get_right(), outer.get_right(), direction=RIGHT)
        brace_label = caption("extra area").next_to(brace, RIGHT, buff=0.1)
        formula = make_label(r"A\subseteq B\Rightarrow P(A)\le P(B)", plain="A ⊆ B  ⇒  P(A) ≤ P(B)", font_size=28)
        formula.to_edge(RIGHT, buff=0.4).shift(DOWN * 0.5)

        self.play(FadeIn(outer), FadeIn(label_b), run_time=0.8)
        self.play(FadeIn(inner), FadeIn(label_a), run_time=0.8)
        self.play(GrowFromCenter(brace), FadeIn(brace_label), FadeIn(formula), run_time=0.9)
        self.play(self.play_meter(0.62), run_time=0.8)
        self.play(Indicate(inner, color=BLUE), Indicate(outer, color=GREEN), run_time=1)
        self.wait(0.5)

        self.mono_group = VGroup(outer, inner, label_a, label_b, brace, brace_label, formula)
        self.banner = banner

    def act_law_inclusion_exclusion(self):
        self.play(FadeOut(self.banner), FadeOut(self.mono_group), run_time=0.5)
        banner = self.show_banner(
            "Law 4 — Overlaps are counted twice, so subtract once",
            "For two events, overlap area must be removed after adding.",
        )

        center = BOARD_CENTER + DOWN * 0.1
        circle_a = Circle(radius=0.95, color=BLUE, fill_color=BLUE, fill_opacity=0.45)
        circle_b = Circle(radius=0.95, color=RED, fill_color=RED, fill_opacity=0.45)
        circle_a.move_to(center + LEFT * 0.55)
        circle_b.move_to(center + RIGHT * 0.55)

        label_a = make_label("A", font_size=32).move_to(circle_a.get_center() + LEFT * 0.55)
        label_b = make_label("B", font_size=32).move_to(circle_b.get_center() + RIGHT * 0.55)

        overlap = Intersection(circle_a, circle_b)
        overlap.set_fill(color=PURPLE, opacity=0.85)
        overlap.set_stroke(color=PURPLE, width=2)
        overlap_label = make_label(r"A\cap B", plain="A ∩ B", font_size=26).move_to(overlap)

        only_a = Difference(circle_a, circle_b)
        only_a.set_fill(color=BLUE, opacity=0.55)
        only_b = Difference(circle_b, circle_a)
        only_b.set_fill(color=RED, opacity=0.55)

        step1 = caption("Step 1: take all of A").to_edge(DOWN, buff=0.55)
        step2 = caption("Step 2: add all of B").to_edge(DOWN, buff=0.55)
        step3 = caption("Step 3: subtract overlap once").to_edge(DOWN, buff=0.55)

        formula = make_label(
            r"P(A\cup B)=P(A)+P(B)-P(A\cap B)",
            plain="P(A ∪ B) = P(A) + P(B) − P(A ∩ B)",
            font_size=30,
        )
        formula.to_edge(RIGHT, buff=0.35).shift(UP * 1.4)

        self.play(FadeIn(circle_a), FadeIn(circle_b), FadeIn(label_a), FadeIn(label_b), run_time=1)
        self.play(FadeIn(step1), Indicate(only_a, color=BLUE), run_time=1)
        self.play(Transform(step1, step2), Indicate(circle_b, color=RED), run_time=1)
        self.play(
            Transform(step1, step3),
            FadeIn(overlap),
            FadeIn(overlap_label),
            run_time=1,
        )
        self.play(Flash(overlap, color=PURPLE, line_length=0.25), FadeIn(formula), run_time=1)
        self.play(self.play_meter(0.78), run_time=0.8)
        self.wait(0.8)

        self.venn_group = VGroup(
            circle_a,
            circle_b,
            label_a,
            label_b,
            overlap,
            overlap_label,
            only_a,
            only_b,
            step1,
            formula,
        )
        self.banner = banner

    def act_finale(self, board, meter, omega_label, dart):
        self.play(
            FadeOut(self.banner),
            FadeOut(self.venn_group),
            FadeOut(self.grid),
            run_time=0.6,
        )

        board.set_fill(color=BLUE_E, opacity=0.15)
        self.play(
            FadeIn(board),
            FadeIn(omega_label),
            FadeIn(meter),
            dart.animate.move_to(board.get_center()),
            run_time=1,
        )

        recap = VGroup(
            caption("A1: areas are never negative"),
            caption("A2: the whole board is 1"),
            caption("A3: disjoint pieces add"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.to_edge(RIGHT, buff=0.45).shift(UP * 0.3)

        takeaway = Text(
            "Every probability law is just careful bookkeeping of area.",
            font_size=30,
            color=YELLOW,
        )
        takeaway.to_edge(DOWN, buff=0.55)

        self.play(FadeIn(recap, lag_ratio=0.2), run_time=1)
        self.play(Write(takeaway), run_time=1)
        self.play(self.play_meter(1.0), Indicate(board, color=YELLOW), run_time=1)
        self.wait(2)
        self.play(
            FadeOut(recap),
            FadeOut(takeaway),
            FadeOut(board),
            FadeOut(omega_label),
            FadeOut(meter),
            FadeOut(dart),
            run_time=1.2,
        )

    def play_meter(self, value: float):
        frame, fill, label, value_mob = self.meter
        max_height = frame.height
        target_height = max(0.01, value * max_height)
        new_fill = Rectangle(
            width=fill.width,
            height=target_height,
            color=YELLOW,
            fill_opacity=0.9,
            stroke_width=0,
        )
        new_fill.align_to(frame, DOWN)
        new_value = Text(f"{value:.2f}", font_size=22).move_to(value_mob)
        return AnimationGroup(
            Transform(fill, new_fill),
            Transform(value_mob, new_value),
            lag_ratio=0,
        )
