from manimlib.imports import *


def heaviside(x):
    return int(x >= 0)

# NeuralNetworkMobject is not my code, from 3b1b/manim


class NeuralNetworkMobject(VGroup):
    CONFIG = {
        "neuron_radius": 0.15,
        "neuron_to_neuron_buff": MED_SMALL_BUFF,
        "layer_to_layer_buff": LARGE_BUFF,
        "neuron_stroke_color": BLUE,
        "neuron_stroke_width": 3,
        "neuron_fill_color": GREEN,
        "edge_color": LIGHT_GREY,
        "edge_stroke_width": 2,
        "edge_propogation_color": YELLOW,
        "edge_propogation_time": 1,
        "max_shown_neurons": 16,
        "brace_for_large_layers": True,
        "average_shown_activation_of_large_layer": True,
        "include_output_labels": False,
        "arrow": False,
        "arrow_tip_size": 0.1
    }

    def __init__(self, neural_network, size=0.15, *args, **kwargs):
        VGroup.__init__(self, *args, **kwargs)
        self.layer_sizes = neural_network
        self.neuron_radius = size
        self.add_neurons()
        self.add_edges()

    def add_neurons(self):
        layers = VGroup(*[
            self.get_layer(size)
            for size in self.layer_sizes
        ])
        layers.arrange_submobjects(RIGHT, buff=self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers)
        if self.include_output_labels:
            self.add_output_labels()

    def get_layer(self, size):
        layer = VGroup()
        n_neurons = size
        if n_neurons > self.max_shown_neurons:
            n_neurons = self.max_shown_neurons
        neurons = VGroup(*[
            Circle(
                radius=self.neuron_radius,
                stroke_color=self.neuron_stroke_color,
                stroke_width=self.neuron_stroke_width,
                fill_color=self.neuron_fill_color,
                fill_opacity=0,
            )
            for x in range(n_neurons)
        ])
        neurons.arrange_submobjects(
            DOWN, buff=self.neuron_to_neuron_buff
        )
        for neuron in neurons:
            neuron.edges_in = VGroup()
            neuron.edges_out = VGroup()
        layer.neurons = neurons
        layer.add(neurons)

        if size > n_neurons:
            dots = TexMobject("\\vdots")
            dots.move_to(neurons)
            VGroup(*neurons[:len(neurons) // 2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*neurons[len(neurons) // 2:]).next_to(
                dots, DOWN, MED_SMALL_BUFF
            )
            layer.dots = dots
            layer.add(dots)
            if self.brace_for_large_layers:
                brace = Brace(layer, LEFT)
                brace_label = brace.get_tex(str(size))
                layer.brace = brace
                layer.brace_label = brace_label
                layer.add(brace, brace_label)

        return layer

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = self.get_edge(n1, n2)
                edge_group.add(edge)
                n1.edges_out.add(edge)
                n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_edge(self, neuron1, neuron2):
        if self.arrow:
            return Arrow(
                neuron1.get_center(),
                neuron2.get_center(),
                buff=self.neuron_radius,
                stroke_color=self.edge_color,
                stroke_width=self.edge_stroke_width,
                tip_length=self.arrow_tip_size
            )
        return Line(
            neuron1.get_center(),
            neuron2.get_center(),
            buff=self.neuron_radius,
            stroke_color=self.edge_color,
            stroke_width=self.edge_stroke_width,
        )

    def add_input_labels(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[0].neurons):
            label = TexMobject(f"x_{n + 1}")
            label.set_height(0.3 * neuron.get_height())
            label.move_to(neuron)
            self.output_labels.add(label)
        self.add(self.output_labels)

    def add_y(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[-1].neurons):
            label = TexMobject("y")
            label.set_height(0.3 * neuron.get_height())
            label.move_to(neuron)
            self.output_labels.add(label)
        self.add(self.output_labels)

    def add_weight_labels(self):
        weight_group = VGroup()

        for n, i in enumerate(self.layers[0].neurons):
            edge = self.get_edge(i, self.layers[-1][0])
            text = TexMobject(f"w_{n + 1}", color=RED)
            text.move_to(edge)
            weight_group.add(text)
        self.add(weight_group)


class PerceptronMobject(NeuralNetworkMobject):
    def add_neurons(self):
        layers = VGroup(*[
            self.get_layer(size)
            for size in self.layer_sizes
        ])
        layers.arrange_submobjects(RIGHT, buff=self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers[1])
        if self.include_output_labels:
            self.add_output_labels()


def heaviside(x):
    return int(x >= 0)


class PerceptronOne(Scene):
    CONFIG = {
        "n_color": RED
    }

    def construct(self):
        x = ValueTracker(0)

        perc = PerceptronMobject(
            [1, 1, 1], arrow=True, arrow_tip_size=0.1, size=0.25, neuron_stroke_color=self.n_color)
        perc.scale(1.5)
        perc.shift(1.5 * UP + 3.5 * LEFT)

        circ = Circle(fill_opacity=0.5, color=self.n_color,
                      radius=0.25, stroke_opacity=0)

        def circ_updater(circle):
            new_circle = Circle(
                fill_opacity=0.5 * heaviside(x.get_value() - 20),
                color=self.n_color,
                radius=0.25,
                stroke_opacity=0
            )
            new_circle.scale(1.5)
            new_circle.shift(3.5 * LEFT + 1.5 * UP)
            circle.become(new_circle)

        circ.add_updater(circ_updater)

        l = NumberLine(x_min=0, x_max=30, numbers_with_elongated_ticks=[], unit_size=0.15, tick_frequency=5,
                       include_numbers=True, numbers_to_show=[i for i in range(0, 31, 5)])
        l.shift(5.75 * LEFT + 1.5 * DOWN)

        x_disp = TexMobject("0")

        def x_disp_updater(x_disp):
            new_disp = TexMobject(
                str(heaviside(x.get_value() - 20))
            )
            new_disp.shift(1 * LEFT + 1.5 * UP)
            x_disp.become(new_disp)

        x_disp.add_updater(x_disp_updater)

        ptr = Triangle(fill_opacity=1)

        def ptr_updater(ptr):
            new_ptr = Triangle(fill_opacity=1)
            new_ptr.rotate(180 * DEGREES)
            new_ptr.scale(0.15)
            new_ptr.shift([(x.get_value()-15) * 0.15 - 3.5, -1.6, 0])
            ptr.become(new_ptr)

        ptr.add_updater(ptr_updater)

        self.add(circ, perc, l, x_disp, Line(10*UP, 10*DOWN), ptr)
        self.wait()

        self.play(x.increment_value, 30, rate_func=linear, run_time=6)
        self.wait()
