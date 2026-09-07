from typing import Tuple
from manim import *


SCALE = 0.2
DURATION = 0.2


class PolyArrow(TipableVMobject):
    def __init__(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        coords: NumberPlane,
        direction=RIGHT,
        **kwargs
    ):
        super().__init__(**kwargs)

        start = coords.c2p(*start, 0)
        end = coords.c2p(*end, 0)

        if start[0] == end[0] or start[1] == end[1]:
            self.add(
                Line(start=start, end=end, **kwargs)
                .set_stroke(width=2)
                .add_tip(tip_width=0.2, tip_length=0.2)
            )

        else:
            if np.all(direction == RIGHT) or np.all(direction == LEFT):
                middle = (start[0] + end[0]) / 2
                grid = VGroup(
                    Line(start=start, end=(middle, start[1], 0), **kwargs).set_stroke(
                        width=2
                    ),
                    Line(
                        start=(middle, start[1], 0), end=(middle, end[1], 0), **kwargs
                    ).set_stroke(width=2),
                    Line(start=(middle, end[1], 0), end=end, **kwargs)
                    .set_stroke(width=2)
                    .add_tip(tip_width=0.2, tip_length=0.2),
                )
                self.add(grid)

            elif np.all(direction == DOWN) or np.all(direction == UP):
                middle = (start[1] + end[1]) / 2
                grid = VGroup(
                    Line(start=start, end=(start[0], middle, 0), **kwargs).set_stroke(
                        width=2
                    ),
                    Line(
                        start=(start[0], middle, 0), end=(end[0], middle, 0), **kwargs
                    ).set_stroke(width=2),
                    Line(start=(end[0], middle, 0), end=end, **kwargs)
                    .set_stroke(width=2)
                    .add_tip(tip_width=0.2, tip_length=0.2),
                )
                self.add(grid)


class FlashAttention(Scene):
    def construct(self):
        coords = NumberPlane(
            x_range=[-13 * 4 // 2, 13 * 4 // 2, 1],
            y_range=[-9 * 4 // 2, 9 * 4 // 2, 1],
            x_length=13 * 4,
            y_length=9 * 4,
            background_line_style={"stroke_color": GREY, "stroke_width": 1},
        ).scale(SCALE)
        # self.add(coords)

        query, key, value, out = self.draw_qkvo(coords)
        query_tex, key_tex, value_tex, out_tex = self.draw_tex(coords)
        self.draw_anim(coords, query, key, value, out)

    def draw_qkvo(self, coords):
        query = [
            Rectangle(color=GREEN, height=1, width=4, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(-12, -i - 0.5 + 6, 0))
            for i in range(12)
        ]
        for q in query:
            self.add(q)

        key = [
            Rectangle(color=BLUE, height=4, width=1, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(i + 0.5 - 6, 12, 0))
            for i in range(12)
        ]
        for k in key:
            self.add(k)

        value = [
            Rectangle(color=ORANGE, height=1, width=4, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(12, -i - 0.5 + 6, 0))
            for i in range(12)
        ]
        for v in value:
            self.add(v)

        out = [
            Rectangle(color=PURPLE, height=4, width=1, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(i + 0.5 - 6, -12, 0))
            for i in range(12)
        ]
        for o in out:
            self.add(o)

        return query, key, value, out

    def draw_tex(self, coords):
        query_tex = (
            Tex(r"$$\mathbf{Q} \in \mathbb{R}^{N \times d}$$")
            .scale(SCALE * 2)
            .move_to(coords.c2p(-18, 0, 0))
        )
        key_tex = (
            Tex(r"$$\mathbf{K}^{\top} \in \mathbb{R}^{d \times N}$$")
            .scale(SCALE * 2)
            .move_to(coords.c2p(0, 16, 0))
        )
        value_tex = (
            Tex(r"$$\mathbf{V} \in \mathbb{R}^{N \times d}$$")
            .scale(SCALE * 2)
            .move_to(coords.c2p(18, 0, 0))
        )
        out_tex = (
            Tex(
                r"$$\mathbf{O} = \operatorname{softmax} \left( \frac{\mathbf{Q} \mathbf{K}^{\top}}{\sqrt{d}} \right)"
                r"\mathbf{V} \in \mathbb{R}^{N \times d}$$"
            )
            .scale(SCALE * 2)
            .move_to(coords.c2p(0, -16, 0))
        )
        self.add(query_tex, key_tex, value_tex, out_tex)

        return query_tex, key_tex, value_tex, out_tex

    def draw_anim(self, coords, query, key, value, out):
        # for i in range(12):
        for i in [0, 1, 11]:
            key_arrow = (
                Line(
                    start=coords.c2p(i + 0.5 - 6, 10, 0),
                    end=coords.c2p(i + 0.5 - 6, 6 - i, 0),
                )
                .set_stroke(width=2)
                .add_tip(tip_width=0.2, tip_length=0.2)
            )
            # key_arrow.tip_length = 1
            value_arrow = (
                Line(
                    start=coords.c2p(10, -i - 0.5 + 6, 0),
                    end=coords.c2p(-5 + i, -i - 0.5 + 6, 0),
                )
                .set_stroke(width=2)
                .add_tip(tip_width=0.2, tip_length=0.2)
            )
            # value_arrow.tip_length = 1
            circle = (
                Circle(color=RED, fill_opacity=1, radius=0.5)
                .scale(SCALE)
                .move_to(coords.c2p(i + 0.5 - 6, -i - 0.5 + 6, 0))
            )

            # self.play(Create(key_arrow), subcaption_duration=DURATION)
            # self.wait(duration=DURATION)
            # self.play(Create(value_arrow), subcaption_duration=DURATION)
            # self.wait(duration=DURATION)

            # cur_key = key[i].copy()
            # cur_value = value[i].copy()
            # self.play(
            #     Create(key_arrow),
            #     Create(value_arrow),
            #     FadeTransform(cur_key, circle),
            #     FadeTransform(cur_value, circle),
            #     subcaption_duration=DURATION,
            # )
            self.play(
                Indicate(key[i]), Indicate(value[i]), subcaption_duration=DURATION
            )
            self.play(
                Create(key_arrow), Create(value_arrow), subcaption_duration=DURATION
            )
            self.play(Create(circle), subcaption_duration=DURATION)
            self.wait(duration=DURATION)

            # for j in range(12):
            for j in [0, 1, 11]:
                query_arrow = PolyArrow(
                    start=(-10, -j - 0.5 + 6),
                    end=(-6 + i, -i - 0.5 + 6),
                    coords=coords,
                    direction=RIGHT,
                )
                out_arrow_up = PolyArrow(
                    start=(j + 0.5 - 6, -10),
                    end=(i + 0.5 - 6, -i + 5),
                    coords=coords,
                    direction=UP,
                )
                out_arrow_down = PolyArrow(
                    start=(i + 0.5 - 6, -i + 5),
                    end=(j + 0.5 - 6, -10),
                    coords=coords,
                    direction=DOWN,
                )
                # cur_query = query[j].copy()
                # cur_out = out[j]
                # cur_circle = circle.copy()

                # self.play(Create(query_arrow), subcaption_duration=DURATION)
                # self.wait(duration=DURATION)
                # self.play(FadeTransform(cur_query, cur_circle), subcaption_duration=DURATION)
                # self.wait(duration=DURATION)
                # self.play(
                #     Create(query_arrow),
                #     FadeTransform(cur_query, cur_circle),
                #     subcaption_duration=DURATION,
                # )
                self.play(
                    Indicate(query[j]), Indicate(out[j]), subcaption_duration=DURATION
                )
                self.play(
                    Create(query_arrow),
                    Create(out_arrow_up),
                    subcaption_duration=DURATION,
                )
                self.play(Indicate(circle), subcaption_duration=DURATION)
                self.wait(duration=DURATION)

                comp_score = (
                    MathTex(
                        r"\mathbf{S}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} = \mathbf{Q}_{"
                        + str(j + 1)
                        + r"} \mathbf{K}^{\top}_{"
                        + str(i + 1)
                        + r"}"
                    )
                    .scale(SCALE * 2)
                    .move_to(coords.c2p(14, -14, 0))
                )
                part_softmax = (
                    MathTex(
                        r"\tilde{m}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} &= \operatorname{rowmax} (\mathbf{S}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"}) \\ \tilde{\mathbf{P} }_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} &= \exp (\mathbf{S}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} - \tilde{m}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"}) \\ \tilde{l}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} &= \operatorname{rowsum} (\tilde{\mathbf{P} }_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"})"
                    )
                    .scale(SCALE * 2)
                    .move_to(coords.c2p(14, -14, 0))
                )

                self.play(Write(comp_score), subcaption_duration=DURATION)
                self.wait()
                self.play(
                    FadeTransform(comp_score, part_softmax),
                    subcaption_duration=DURATION,
                )
                self.wait()
                self.play(
                    Unwrite(part_softmax),
                    Uncreate(query_arrow),
                    Uncreate(out_arrow_up),
                    subcaption_duration=DURATION,
                )
                self.wait(duration=DURATION)

                # self.play(Create(out_arrow), subcaption_duration=DURATION)
                # self.wait(duration=DURATION)
                # self.play(FadeTransform(cur_circle, cur_out), subcaption_duration=DURATION)
                # self.wait(duration=DURATION)
                # self.play(
                #     Create(out_arrow),
                #     FadeTransform(cur_circle, cur_out),
                #     subcaption_duration=DURATION,
                # )
                self.play(Indicate(circle), subcaption_duration=DURATION)
                self.play(Create(out_arrow_down), subcaption_duration=DURATION)
                self.play(Indicate(out[j]), subcaption_duration=DURATION)
                self.wait(duration=DURATION)

                update_max_sum = (
                    MathTex(
                        r"m_{"
                        + str(j + 1)
                        + r"}^{\mathrm{new} } &= \max (m_{"
                        + str(j + 1)
                        + r"}, \tilde{m}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"}) \\ \ell_{"
                        + str(j + 1)
                        + r"}^{\mathrm{new} } &= e^{m_{"
                        + str(j + 1)
                        + r"} - m_{"
                        + str(j + 1)
                        + r"}^{\mathrm{new} } } \ell_{"
                        + str(j + 1)
                        + r"} \\ &+ e^{\tilde{m}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} - m_{"
                        + str(j + 1)
                        + r"}^{\mathrm{new} } } \tilde{l}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"}"
                    )
                    .scale(SCALE * 2)
                    .move_to(coords.c2p(14, -14, 0))
                )
                update_out = (
                    MathTex(
                        r"\mathbf{O}_{"
                        + str(j + 1)
                        + r"} &= \operatorname{diag}(\ell_{"
                        + str(j + 1)
                        + r"}^{\mathrm {new}})^{-1} \times \\ & \Big( \operatorname{diag}(\ell_{"
                        + str(j + 1)
                        + r"}) e^{m_{"
                        + str(j + 1)
                        + r"}-m_{"
                        + str(j + 1)
                        + r"}^{\mathrm {new}}} \mathbf{O}_{"
                        + str(j + 1)
                        + r"} \\ &+ e^{\tilde{m}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"}-m_{"
                        + str(j + 1)
                        + r"}^{\mathrm {new}}} \tilde{\mathbf{P}}_{"
                        + str(j + 1)
                        + ", "
                        + str(i + 1)
                        + r"} \mathbf{V}_{"
                        + str(i + 1)
                        + r"} \Big)"
                    )
                    .scale(SCALE * 2)
                    .move_to(coords.c2p(14, -14, 0))
                )

                self.play(Write(update_max_sum), subcaption_duration=DURATION)
                self.wait()
                self.play(
                    FadeTransform(update_max_sum, update_out),
                    subcaption_duration=DURATION,
                )
                self.wait()

                self.play(
                    Uncreate(query_arrow),
                    Uncreate(out_arrow_down),
                    Unwrite(update_out),
                    subcaption_duration=DURATION,
                )
                self.wait(duration=DURATION)

            self.play(
                Uncreate(key_arrow),
                Uncreate(value_arrow),
                Uncreate(circle),
                subcaption_duration=DURATION,
            )
            self.wait(duration=DURATION)


class FlashAttentionTest(Scene):
    def construct(self):
        coords = NumberPlane(
            x_range=[-13 * 4 // 2, 13 * 4 // 2, 1],
            y_range=[-9 * 4 // 2, 9 * 4 // 2, 1],
            x_length=13 * 4,
            y_length=9 * 4,
            background_line_style={"stroke_color": GREY, "stroke_width": 1},
        ).scale(SCALE)
        # self.add(coords)

        self.draw_qkvo(coords)

        i, j = 1, 2

        comp_score = (
            MathTex(
                r"\mathbf{S}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} = \mathbf{Q}_{"
                + str(i + 1)
                + r"} \mathbf{K}^{\top}_{"
                + str(j + 1)
                + r"}"
            )
            .scale(SCALE * 2)
            .move_to(coords.c2p(14, -14, 0))
        )
        # self.add(comp_score)

        part_softmax = (
            MathTex(
                r"\tilde{m}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} &= \operatorname{rowmax} (\mathbf{S}_{"
                + str(i + 1)
                + str(j + 1)
                + r"}) \\ \tilde{\mathbf{P} }_{"
                + str(i + 1)
                + str(j + 1)
                + r"} &= \exp (\mathbf{S}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} - \tilde{m}_{"
                + str(i + 1)
                + str(j + 1)
                + r"}) \\ \tilde{l}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} &= \operatorname{rowsum} (\tilde{\mathbf{P} }_{"
                + str(i + 1)
                + str(j + 1)
                + r"})"
            )
            .scale(SCALE * 2)
            .move_to(coords.c2p(14, -14, 0))
        )
        # self.add(part_softmax)

        update_max_sum = (
            MathTex(
                r"m_{"
                + str(i + 1)
                + r"}^{\mathrm{new} } &= \max (m_{"
                + str(i + 1)
                + r"}, \tilde{m}_{"
                + str(i + 1)
                + str(j + 1)
                + r"}) \\ \ell_{"
                + str(i + 1)
                + r"}^{\mathrm{new} } &= e^{m_{"
                + str(i + 1)
                + r"} - m_{"
                + str(i + 1)
                + r"}^{\mathrm{new} } } \ell_{"
                + str(i + 1)
                + r"} \\ &+ e^{\tilde{m}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} - m_{"
                + str(i + 1)
                + r"}^{\mathrm{new} } } \tilde{l}_{"
                + str(i + 1)
                + str(j + 1)
                + r"}"
            )
            .scale(SCALE * 2)
            .move_to(coords.c2p(14, -14, 0))
        )
        self.add(update_max_sum)

        update_out = (
            MathTex(
                r"\mathbf{O}_{"
                + str(i + 1)
                + r"} &= \operatorname{diag}(\ell_{"
                + str(i + 1)
                + r"}^{\mathrm {new}})^{-1} \times \\ & \Big( \operatorname{diag}(\ell_{"
                + str(i + 1)
                + r"}) e^{m_{"
                + str(i + 1)
                + r"}-m_{"
                + str(i + 1)
                + r"}^{\mathrm {new}}} \mathbf{O}_{"
                + str(i + 1)
                + r"} \\ &+ e^{\tilde{m}_{"
                + str(i + 1)
                + str(j + 1)
                + r"}-m_{"
                + str(i + 1)
                + r"}^{\mathrm {new}}} \tilde{\mathbf{P}}_{"
                + str(i + 1)
                + str(j + 1)
                + r"} \mathbf{V}_{"
                + str(j + 1)
                + r"} \Big)"
            )
            .scale(SCALE * 2)
            .move_to(coords.c2p(14, -14, 0))
        )
        # self.add(update_out)

    def draw_qkvo(self, coords):
        query = [
            Rectangle(color=GREEN, height=1, width=4, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(-12, -i - 0.5 + 6, 0))
            for i in range(12)
        ]
        for q in query:
            self.add(q)

        key = [
            Rectangle(color=BLUE, height=4, width=1, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(i + 0.5 - 6, 12, 0))
            for i in range(12)
        ]
        for k in key:
            self.add(k)

        value = [
            Rectangle(color=ORANGE, height=1, width=4, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(12, -i - 0.5 + 6, 0))
            for i in range(12)
        ]
        for v in value:
            self.add(v)

        out = [
            Rectangle(color=PURPLE, height=4, width=1, fill_opacity=0.5)
            .scale(SCALE)
            .move_to(coords.c2p(i + 0.5 - 6, -12, 0))
            for i in range(12)
        ]
        for o in out:
            self.add(o)

        return query, key, value, out
