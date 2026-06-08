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

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

from .owis_base import OWISAdvancedAxis, OWISAdvancedBase

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PS90PlusAxis(OWISAdvancedAxis):
    """Axis channel for the PS 90+, extending :class:`OWISAdvancedAxis` with
    PS 90+-specific axis commands.

    The PS 90+ supports up to nine axes (numbers 1–9).
    """

    #: Axis-state characters that indicate active motion on the PS 90+.
    #: Extends the base set with joystick (J), WMS-assisted trapezoidal /
    #: S-curve / velocity modes (W, X, Y), continuous path control (C) and
    #: piezo follow-up mode (N).
    MOVING_STATES = frozenset("TVPFJHSWXYCN")

    # ── Axis signals (extended 16-bit layout for PS 90+) ─────────────────────

    axis_signals = Channel.measurement(
        "?AXSIGNALS{ch}",
        """Get the raw hardware axis signals as a binary string (16 bits).

        * Bit 0 – encoder CHA
        * Bit 1 – encoder CHB
        * Bit 2 – encoder Index
        * Bit 3 – encoder Home
        * Bit 4 – MAXSTOP
        * Bit 5 – MINSTOP
        * Bit 6 – AxisIn-Pin
        * Bit 7 – Hall A
        * Bit 8 – Hall B
        * Bit 9 – Hall C
        * Bit 10 – AxisOut-Pin
        * Bits 11–15 – reserved
        """,
        cast=str,
    )

    # ── PS 90+-specific axis parameters ──────────────────────────────────────

    bldc_commutation = Channel.control(
        "?BLDCCT{ch}", "BLDCCT{ch}=%d",
        """Control the commutation mode for BLDC axes (int).

        * ``0`` – block commutation with Hall sensors
        * ``1`` – sine commutation with encoder
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    joystick_auto_off = Channel.control(
        "?JAUTOMOFF{ch}", "JAUTOMOFF{ch}=%d",
        """Control automatic motor switch-off in joystick mode when the axis
        reaches its target position (int, DC mode only).
        ``1`` = auto-off enabled, ``0`` = disabled.
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )


class PS90Plus(OWISAdvancedBase):
    """OWIS PS 90+ up to nine-axis universal position control unit driver.

    The PS 90+ is a modular, configurable controller capable of driving up to
    nine axes with DC brush, stepper, or BLDC motors (up to six nano-hybrid
    axes).  It communicates over USB 2.0, RS-232 or Ethernet using an ASCII
    protocol.

    :param adapter: A string VISA resource name (e.g.
        ``'ASRL/dev/ttyUSB0::INSTR'``, ``'ASRL3::INSTR'`` for COM3) or an
        :class:`~pymeasure.adapters.Adapter` subclass object.
    :param name: Instrument name string.

    Example usage::

        from pymeasure.instruments.owis import PS90Plus

        ctrl = PS90Plus('ASRL/dev/ttyUSB0::INSTR')
        ctrl.axis1.initialize()
        ctrl.axis1.positioning_mode = 'ABSOL'
        ctrl.axis1.target_position = 10000
        ctrl.axis1.max_velocity = 20000
        ctrl.axis1.acceleration = 100000
        ctrl.axis1.start_positioning()
        ctrl.axis1.wait_for_stop()
    """

    axis1 = Instrument.ChannelCreator(PS90PlusAxis, 1)
    axis2 = Instrument.ChannelCreator(PS90PlusAxis, 2)
    axis3 = Instrument.ChannelCreator(PS90PlusAxis, 3)
    axis4 = Instrument.ChannelCreator(PS90PlusAxis, 4)
    axis5 = Instrument.ChannelCreator(PS90PlusAxis, 5)
    axis6 = Instrument.ChannelCreator(PS90PlusAxis, 6)
    axis7 = Instrument.ChannelCreator(PS90PlusAxis, 7)
    axis8 = Instrument.ChannelCreator(PS90PlusAxis, 8)
    axis9 = Instrument.ChannelCreator(PS90PlusAxis, 9)

    _axis_ids = tuple(range(1, 10))

    def __init__(self, adapter, name="OWIS PS 90+", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def is_moving(self):
        """Return ``True`` if any axis is currently executing a motion command.

        Uses the PS 90+-extended :attr:`PS90PlusAxis.MOVING_STATES` set which
        includes joystick mode, WMS-assisted moves, and piezo follow-up states
        in addition to the base moving states.
        """
        return any(c in PS90PlusAxis.MOVING_STATES for c in self.axis_state)

    # ── PS 90+-specific I/O ───────────────────────────────────────────────────

    sps_inputs = Instrument.measurement(
        "?INPSPS",
        """Get the current state of all SPS inputs as an 8-character binary
        string.
        """,
        cast=str,
    )

    sps_outputs = Instrument.measurement(
        "?OUTSPS",
        """Get the current state of all SPS outputs as a binary string.""",
        cast=str,
    )

    input_mode = Instrument.control(
        "?INMODE", "INMODE=%d",
        """Control the active input level (int).

        * ``0`` – TTL inputs
        * ``1`` – SPS inputs
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    io_config = Instrument.measurement(
        "?IOCONFIG",
        """Get the current I/O configuration value (int).""",
        cast=int,
    )

    # ── PS 90+ multi-axis commands ────────────────────────────────────────────

    def multi_axis_start_positioning(self, axis_mask):
        """Start trapezoidal positioning for multiple axes simultaneously.

        :param axis_mask: Binary axis mask string (bit 0 = axis 1, …,
            bit 8 = axis 9).  E.g. ``'000000011'`` starts axes 1 and 2.
        """
        self.write("MPGO=%s" % str(axis_mask))

    def multi_axis_start_velocity(self, axis_mask):
        """Start velocity mode for multiple axes simultaneously.

        :param axis_mask: Binary axis mask string (bit 0 = axis 1, …,
            bit 8 = axis 9).
        """
        self.write("MVGO=%s" % str(axis_mask))

    def multi_axis_stop(self, axis_mask):
        """Stop multiple axes simultaneously using their preset deceleration
        ramps.

        :param axis_mask: Binary axis mask string (bit 0 = axis 1, …,
            bit 8 = axis 9).
        """
        self.write("MSTOP=%s" % str(axis_mask))

    # ── PS 90+ SPS output control ─────────────────────────────────────────────

    def set_sps_output(self, port, value):
        """Set an SPS digital output.

        :param port: Output port number (integer, 1-based).
        :param value: Output state (``0`` = low, ``1`` = high).
        """
        value = strict_discrete_set(int(value), [0, 1])
        self.write("OUTSPS%d=%d" % (int(port), value))

    # ── PS 90+ analog output ──────────────────────────────────────────────────

    def get_analog_output(self, port):
        """Read the current value of an analog (DAC) output.

        :param port: Analog output port number (1-based).
        :returns: Integer 0–1023.
        """
        return int(self.ask("?DAOUT%d" % int(port)))

    def set_analog_output(self, port, value):
        """Set the value of an analog (DAC) output.

        :param port: Analog output port number (1-based).
        :param value: Output value (0–1023 for a 10-bit DAC).
        """
        value = strict_range(int(value), [0, 1023])
        self.write("DAOUT%d=%d" % (int(port), value))
