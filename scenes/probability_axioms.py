import shutil

from manim import *

LATEX_AVAILABLE = shutil.which("latex") is not None


def make_label(latex: str, plain: str | None = None, font_size: int = 36) -> Mobject:
    """Render math with MathTex when LaTeX is installed, else readable Text."""
    if LATEX_AVAILABLE:
        return MathTex(latex, font_size=font_size)
    return Text(plain if plain is not None else latex, font_size=font_size)


class ProbabilityFromAxioms(Scene):
    def construct(self):
        title = Text("Probability from the axioms", font_size=48)
        subtitle = Text("Deriving the basic laws", font_size=30, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=UP * 0.25), FadeIn(subtitle), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.8)

        header = Text("Kolmogorov axioms", font_size=40)
        header.to_edge(UP, buff=0.5)

        ax1 = make_label(
            r"\textbf{(A1)}\quad P(A)\ge 0\ \text{ for any event }A",
            plain="(A1)  P(A) ≥ 0   for any event A",
            font_size=34,
        )
        ax2 = make_label(
            r"\textbf{(A2)}\quad P(\Omega)=1",
            plain="(A2)  P(Ω) = 1",
            font_size=34,
        )
        ax3 = make_label(
            r"\textbf{(A3)}\quad A_i\cap A_j=\varnothing\ (i\ne j)\Rightarrow"
            r"\ P\!\left(\bigcup_i A_i\right)=\sum_i P(A_i)",
            plain="(A3)  If events are disjoint:  P(⋃ A_i) = Σ P(A_i)",
            font_size=32,
        )

        axioms = VGroup(ax1, ax2, ax3).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        axioms.next_to(header, DOWN, buff=0.6).to_edge(LEFT, buff=0.9)

        self.play(FadeIn(header), run_time=0.8)
        self.play(Write(ax1), run_time=1.2)
        self.play(Write(ax2), run_time=1.0)
        self.play(Write(ax3), run_time=1.6)
        self.wait(0.6)

        divider = Line(LEFT * 6.6, RIGHT * 6.6, stroke_width=2, color=GRAY_D)
        divider.next_to(axioms, DOWN, buff=0.55)

        laws_header = Text("Derived laws", font_size=40)
        laws_header.next_to(divider, DOWN, buff=0.45).align_to(header, LEFT)

        self.play(Create(divider), FadeIn(laws_header), run_time=0.8)

        laws_anchor = laws_header.get_bottom() + DOWN * 0.45

        def show_law(law: Mobject, proof: VGroup | None = None, hold: float = 0.8):
            law.move_to(laws_anchor, aligned_edge=LEFT)
            self.play(FadeIn(law, shift=DOWN * 0.15), run_time=0.6)
            if proof is not None:
                proof.next_to(law, DOWN, buff=0.35).align_to(law, LEFT)
                self.play(FadeIn(proof, lag_ratio=0.08), run_time=0.7)
                self.wait(hold)
                self.play(FadeOut(proof), run_time=0.4)
            else:
                self.wait(hold)
            self.play(FadeOut(law), run_time=0.4)

        # Law 1: P(empty) = 0
        law1 = make_label(
            r"P(\varnothing)=0",
            plain="P(∅) = 0",
            font_size=44,
        )
        proof1 = VGroup(
            make_label(
                r"\varnothing\cup\varnothing=\varnothing\ \text{ and disjoint}",
                plain="∅ ∪ ∅ = ∅   and disjoint",
                font_size=30,
            ),
            make_label(
                r"P(\varnothing)=P(\varnothing)+P(\varnothing)\Rightarrow P(\varnothing)=0",
                plain="P(∅) = P(∅) + P(∅)  ⇒  P(∅) = 0",
                font_size=30,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        show_law(law1, proof1, hold=1.0)

        # Law 2: Complement rule
        law2 = make_label(
            r"P(A^c)=1-P(A)",
            plain="P(Aᶜ) = 1 − P(A)",
            font_size=44,
        )
        proof2 = VGroup(
            make_label(
                r"A\cup A^c=\Omega\ \text{ and }A\cap A^c=\varnothing",
                plain="A ∪ Aᶜ = Ω   and   A ∩ Aᶜ = ∅",
                font_size=30,
            ),
            make_label(
                r"1=P(\Omega)=P(A)+P(A^c)\Rightarrow P(A^c)=1-P(A)",
                plain="1 = P(Ω) = P(A) + P(Aᶜ)  ⇒  P(Aᶜ) = 1 − P(A)",
                font_size=30,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        show_law(law2, proof2, hold=1.0)

        # Law 3: Monotonicity
        law3 = make_label(
            r"A\subseteq B\Rightarrow P(A)\le P(B)",
            plain="If A ⊆ B, then P(A) ≤ P(B)",
            font_size=40,
        )
        proof3 = VGroup(
            make_label(
                r"B=A\cup(B\setminus A)\ \text{ and disjoint}",
                plain="B = A ∪ (B \\ A)   and disjoint",
                font_size=30,
            ),
            make_label(
                r"P(B)=P(A)+P(B\setminus A)\ge P(A)",
                plain="P(B) = P(A) + P(B \\ A)  ≥  P(A)",
                font_size=30,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        show_law(law3, proof3, hold=1.0)

        # Law 4: Inclusion–exclusion (two sets)
        law4 = make_label(
            r"P(A\cup B)=P(A)+P(B)-P(A\cap B)",
            plain="P(A ∪ B) = P(A) + P(B) − P(A ∩ B)",
            font_size=38,
        )
        proof4 = VGroup(
            make_label(
                r"A\cup B = A\ \cup\ (B\setminus A)\ \text{ (disjoint)}",
                plain="A ∪ B = A ∪ (B \\ A)   (disjoint)",
                font_size=30,
            ),
            make_label(
                r"P(A\cup B)=P(A)+P(B\setminus A)",
                plain="P(A ∪ B) = P(A) + P(B \\ A)",
                font_size=30,
            ),
            make_label(
                r"P(B)=P(B\setminus A)+P(A\cap B)\Rightarrow P(B\setminus A)=P(B)-P(A\cap B)",
                plain="P(B) = P(B \\ A) + P(A ∩ B)  ⇒  P(B \\ A) = P(B) − P(A ∩ B)",
                font_size=28,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        show_law(law4, proof4, hold=1.1)

        takeaway = Text("All of these follow from (A1)–(A3).", font_size=36)
        takeaway.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(takeaway), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(takeaway), FadeOut(header), FadeOut(axioms), FadeOut(divider), FadeOut(laws_header), run_time=1.2)

