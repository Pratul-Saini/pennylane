# Copyright 2018-2021 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This module contains the MPLDrawer class for creating circuit diagrams with matplotlib
"""
from collections.abc import Iterable

import matplotlib.pyplot as plt
from matplotlib import patches


def _to_tuple(a):
    """converts int or iterable to always tuple"""
    if a is None:
        return tuple()
    if isinstance(a, Iterable):
        return tuple(a)
    return (a,)


class MPLDrawer:
    r"""Allows easy creation of graphics representing circuits with Matplotlib

    Args:
        n_layers (Int): the number of layers
        n_wires (Int): the number of wires

    Keyword Args:
<<<<<<< HEAD
        wire_color=None: MPL compatible color for the wires
        figsize=None (Iterable): Allows user's to manually specify the size of the figure.  Defaults
=======
        figsize=None (Iterable): Allows users to manually specify the size of the figure.  Defaults
>>>>>>> 51f8842209e451a995ead93d71d635d50d89fdf3
           to scale with the size of the circuit via ``n_layers`` and ``n_wires``.

    **Example**

    .. code-block:: python

        drawer = MPLDrawer(n_wires=5,n_layers=5)

        drawer.label(["0","a",r"$|\Psi\rangle$",r"$|\theta\rangle$", "aux"])

        drawer.box_gate(0, [0,1,2,3,4], "Entangling Layers", rotate_text=True)
        drawer.box_gate(1, [0, 1], "U(θ)")
        drawer.box_gate(1, 4, "X", color='lightcoral')

        drawer.SWAP(1, (2, 3))
        drawer.CNOT(2, (0,2), color='forestgreen')

        drawer.ctrl(3, [1,3])
        drawer.box_gate(3, 2, "H", zorder_base=2)

        drawer.ctrl(4, [1,2])

        drawer.measure(5, 0)

        drawer.fig.suptitle('My Circuit', fontsize='xx-large')

    .. figure:: ../../_static/drawer/example_basic.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

    .. UsageDetails::

    This class uses matplotlib and pyplot.  The figure and axes objects can be accessed via ``drawer.fig``
    and ``drawer.ax`` respectively for further configuration. For example, the above example circuit manipulates the
    pyplot figure to set a title using ``drawer.fig.suptitle``. You can also save the images using ``plt.savefig``.

    Each gate takes arguments in order of ``layer`` followed by ``wires``.  These translate to ``x`` and
    ``y`` coordinates in the graph. Layer number (``x``) increases as you go right, and wire number
    (``y``) increases as you go up.  This also means you can pass non-integer values to either keyword.
    For example, if you have a long label, the gate can span multiple layers and have extra width:

    .. code-block:: python

        drawer = MPLDrawer(2,2)
        drawer.box_gate(layer=0, wires=1, text="X")
        drawer.box_gate(layer=1, wires=1, text="Y")

        # Gate between two layers
        drawer.box_gate(layer=0.5, wires=0, text="Big Gate", extra_width=0.5)

    .. figure:: ../../_static/drawer/float_layer.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

    Each gate type accepts a ``color`` argument to customize an individual gate, but you can also set a
    pyplot style or edit ``plt.rcParams`` yourself to get a different look. See available styles with
    ``plt.style.available``. For example, we can set the
    ``'Solarize_Light2'`` style with the same graph as drawn above:

    .. code-block:: python

        plt.style.use('Solarize_Light2')
        drawer = MPLDrawer(n_wires=5,n_layers=5)

        drawer.label(["0","a",r"$|\Psi\rangle$",r"$|\theta\rangle$", "aux"])

        drawer.box_gate(0, [0,1,2,3,4], "Entangling Layers", rotate_text=True)
        drawer.box_gate(1, [0, 1], "U(θ)")
        drawer.box_gate(1, 4, "X", color='lightcoral')

        drawer.SWAP(1, (2, 3))
        drawer.CNOT(2, (0,2), color='forestgreen')

        drawer.ctrl(3, [1,3])
        drawer.box_gate(3, 2, "H", zorder_base=2)

        drawer.ctrl(4, [1,2])

        drawer.measure(5, 0)

        drawer.fig.suptitle('My Circuit', fontsize='xx-large')

    .. figure:: ../../_static/drawer/example_Solarize_Light2.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

    Many methods accept a ``zorder_base`` keyword. Higher ``zorder`` objects are drawn 
    on top of lower ``zorder`` objects. In the above example, we have to set a ``zorder_base``
    to a value of ``2`` in order to draw it *on top* of the control wires, instead of below them.
    """

    def __init__(self, n_layers, n_wires, wirecolor=None, figsize=None):

        self.n_layers = n_layers
        self.n_wires = n_wires

        # half the width of a box
        # is difference between center and edge
        self._box_dx = 0.4

        self._circ_rad = 0.3
        self._ctrl_rad = 0.1
        self._swap_dx = 0.2

        ## Creating figure and ax

        if figsize is None:
            figsize = (self.n_layers + 3, self.n_wires + 1)

        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_axes(
            [0, 0, 1, 1],
            xlim=(-2, self.n_layers + 1),
            ylim=(-1, self.n_wires),
            xticks=[],
            yticks=[],
        )
        
        self.ax.invert_yaxis()

        # adding wire lines
        for wire in range(self.n_wires):
            line = plt.Line2D((-1, self.n_layers), (wire, wire), zorder=1, color=wirecolor)
            self.ax.add_line(line)

    def label(self, labels, text_kwargs=None):
        """Label each wire.

        Args:
            labels [Iterable[str]]: Iterable of labels for the wires

        Keyword Args:
            text_kwargs (dict): any matplotlib keywords for a text object, such as font or size.

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=2, n_layers=1)
            drawer.label(["a", "b"])

        .. figure:: ../../_static/drawer/labels.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """
        if text_kwargs is None:
            text_kwargs = dict()

        for wire, ii_label in enumerate(labels):
            self.ax.text(-1.5, wire, ii_label, **text_kwargs)

    def box_gate(
        self, layer, wires, text="", extra_width=0, rotate_text=False, zorder_base=0,
        box_kwargs=None, text_kwargs=None
    ):
        """Draws a box and adds label text to its center.

        Args:
            layer (Int)
            wires (Union[Int, Iterable[Int]])
            text (str)

        Kwargs:
            extra_width (float): Extra box width
            rotate_text (Bool): whether to rotate text 90 degrees. Helpful to long labels and
                multi-wire boxes.
            zorder_base=0 (Int): increase number to draw on top of other objects, like control wires
            box_kwargs=None (dict): Any matplotlib keywords for the Rectangle patch
            text_kwargs=None (dict): Any matplotlib keywords for the text

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=2, n_layers=2)

            drawer.box_gate(layer=0, wires=0, text="Y")
            drawer.box_gate(layer=1, wires=(0,1), text="CRy(0.1)", rotate_text=True)

        .. figure:: ../../_static/drawer/box_gates.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """
        if box_kwargs is None:
            box_kwargs = dict()
        if text_kwargs is None:
            text_kwargs = dict()

        wires = _to_tuple(wires)

        box_min = min(wires)
        box_max = max(wires)
        box_len = box_max - box_min
        box_center = (box_max + box_min) / 2.0

        if rotate_text:
            rotation = "vertical"
        else:
            rotation = "horizontal"

        box = plt.Rectangle(
            (layer - self._box_dx - extra_width / 2, box_min - self._box_dx),
            2 * self._box_dx + extra_width,
            (box_len + 2 * self._box_dx),
            zorder=2 + zorder_base,
            **box_kwargs
        )
        self.ax.add_patch(box)

        default_text_kwargs = {"ha": "center", "va": "center", "fontsize": "x-large"}
        default_text_kwargs.update(text_kwargs)

        self.ax.text(
            layer,
            box_center,
            text,
            zorder=3 + zorder_base,
            #rotation=rotation,
            **default_text_kwargs
        )

    def ctrl(self, layer, wire_ctrl, wire_target=None, color=None):
        """Add an arbitrary number of control wires

        Args:
            layer (Int): the layer to draw the object in
            wire_ctrl (Union[Int, Iterable[Int]]): set of wires to control on

        Keyword Args:
            wire_target=None (Union[Int, Iterable[Int]]): target wires. Used to determine min
                and max wires for the vertical line
            color=None: mpl compatible color designation

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=2, n_layers=2)

            drawer.ctrl(layer=0, wire_ctrl=0, wire_target=1)
            drawer.ctrl(layer=1, wire_ctrl=(0,1))

        .. figure:: ../../_static/drawer/ctrl.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """
        wire_ctrl = _to_tuple(wire_ctrl)
        wire_target = _to_tuple(wire_target)

        wires_all = wire_ctrl + wire_target
        min_wire = min(wires_all)
        max_wire = max(wires_all)

        line = plt.Line2D((layer, layer), (min_wire, max_wire), zorder=2, color=color)
        self.ax.add_line(line)

        for wire in wire_ctrl:
            circ_ctrl = plt.Circle((layer, wire), radius=self._ctrl_rad, zorder=2, color=color)
            self.ax.add_patch(circ_ctrl)

    def CNOT(self, layer, wires, color=None):
        """Draws a CNOT gate.

        Args:
            layer (Int): layer to draw in
            wires (Int, Int): tuple of (control, target)

        Keyword Args:
            color (None or str): mpl compatible color designation

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=2, n_layers=2)

            drawer.CNOT(0, (0,1))
            drawer.CNOT(1, (1,0))

        .. figure:: ../../_static/drawer/cnot.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """
        target = wires[1]

        self.ctrl(layer, *wires, color=color)
        self._target_x(layer, target, color=color)

    def _target_x(self, layer, wire, color=None):
        """Draws the circle used to represent a CNOT's target

        Args:
            layer (Int): layer to draw on
            wire (Int): wire to draw on

        Keyword Args:
            color=None: mpl compatible color designation
        """
        if color is not None:
            edgecolor = color
        else:
            edgecolor = plt.rcParams["lines.color"]

        target_circ = plt.Circle(
            (layer, wire),
            radius=self._circ_rad,
            zorder=3,
            fill=False,
            edgecolor=edgecolor,
            linewidth=plt.rcParams["lines.linewidth"],
        )
        target_v = plt.Line2D(
            (layer, layer), (wire - self._circ_rad, wire + self._circ_rad), zorder=4, color=color
        )
        self.ax.add_patch(target_circ)
        self.ax.add_line(target_v)

    def SWAP(self, layer, wires, color=None):
        """Draws a SWAP gate

        Args:
            layer (Int): layer to draw on
            wires (Int, Int): Two wires the SWAP acts on

        Keyword Args:
            color=None: mpl compatible color designation

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=2, n_layers=1)

            drawer.SWAP(0, (0,1))

        .. figure:: ../../_static/drawer/SWAP.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """
        line = plt.Line2D((layer, layer), wires, zorder=2, color=color)
        self.ax.add_line(line)

        for wire in wires:
            self._swap_x(layer, wire, color=color)

    def _swap_x(self, layer, wire, color=None):
        """Draw an x such as used in drawing a swap gate

        Args:
            layer (Int): the layer
            wire (Int): the wire

        Keyword Args:
            color=None: mpl compatible color designation

        """
        l1 = plt.Line2D(
            (layer - self._swap_dx, layer + self._swap_dx),
            (wire - self._swap_dx, wire + self._swap_dx),
            zorder=2,
            color=color,
        )
        l2 = plt.Line2D(
            (layer - self._swap_dx, layer + self._swap_dx),
            (wire + self._swap_dx, wire - self._swap_dx),
            zorder=2,
            color=color,
        )

        self.ax.add_line(l1)
        self.ax.add_line(l2)

    def measure(self, layer, wire, zorder_base=0, color=None):
        """Draw a Measurement graphic at designated layer, wire combination.

        Args:
            layer (Int): the layer
            wire (Int): the wire

        Keyword Args:
            zorder_base=0 (Int): amount to shift in zorder from the default
            color=None: mpl compatible color designation

        **Example**

        .. code-block:: python

            drawer = MPLDrawer(n_wires=1, n_layers=1)
            drawer.measure(0, 0)

        .. figure:: ../../_static/drawer/measure.png
            :align: center
            :width: 60%
            :target: javascript:void(0);

        """

        box = plt.Rectangle(
            (layer - self._box_dx, wire - self._box_dx),
            2 * self._box_dx,
            2 * self._box_dx,
            zorder=2 + zorder_base,
            color=color,
        )
        self.ax.add_patch(box)

        arc = patches.Arc(
            (layer, wire - self._box_dx / 8),
            1.2 * self._box_dx,
            1.1 * self._box_dx,
            theta1=0,
            theta2=180,
            zorder=3 + zorder_base,
        )
        self.ax.add_patch(arc)

        # can experiment with the specific numbers to make it look decent
        arrow_start_x = layer - 0.33 * self._box_dx
        arrow_start_y = wire - 0.5 * self._box_dx
        arrow_width = 0.6 * self._box_dx
        arrow_height = 1.0 * self._box_dx

        arrow = plt.arrow(
            arrow_start_x,
            arrow_start_y,
            arrow_width,
            arrow_height,
            head_width=self._box_dx / 4,
            zorder=4 + zorder_base,
            facecolor=color,
        )
        self.ax.add_line(arrow)