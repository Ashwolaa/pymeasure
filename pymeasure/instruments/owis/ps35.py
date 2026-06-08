#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Instrument

from .owis_base import OWISAdvancedAxis, OWISAdvancedBase

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PS35Axis(OWISAdvancedAxis):
    """Axis channel for the PS 35.

    All per-axis properties are inherited from :class:`OWISAdvancedAxis`.
    This class exists as the concrete axis type for the PS 35 and can be
    extended with PS 35-specific axis commands if needed.
    """


class PS35(OWISAdvancedBase):
    """OWIS PS 35 three-axis universal position control unit driver.

    The PS 35 can simultaneously drive up to three axes with 2-phase open-loop
    stepper motors, 2-phase closed-loop stepper motors, or DC servo motors.
    It communicates over USB 2.0 or RS-232 using an ASCII protocol.

    :param adapter: A string VISA resource name (e.g.
        ``'ASRL/dev/ttyUSB0::INSTR'``, ``'ASRL3::INSTR'`` for COM3) or an
        :class:`~pymeasure.adapters.Adapter` subclass object.
    :param name: Instrument name string.

    Example usage::

        from pymeasure.instruments.owis import PS35

        ctrl = PS35('ASRL/dev/ttyUSB0::INSTR')
        ctrl.axis1.initialize()
        ctrl.axis2.initialize()
        ctrl.axis1.positioning_mode = 'ABSOL'
        ctrl.axis1.target_position = 10000
        ctrl.axis1.max_velocity = 20000
        ctrl.axis1.acceleration = 100000
        ctrl.axis1.start_positioning()
        ctrl.axis1.wait_for_stop()
    """

    axis1 = Instrument.ChannelCreator(PS35Axis, 1)
    axis2 = Instrument.ChannelCreator(PS35Axis, 2)
    axis3 = Instrument.ChannelCreator(PS35Axis, 3)

    _axis_ids = (1, 2, 3)

    def __init__(self, adapter, name="OWIS PS 35", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # ── PS 35 output stage reset ──────────────────────────────────────────────

    def reset_output_stage(self):
        """Activate output-stage module reset."""
        self.write("RESETAC")
