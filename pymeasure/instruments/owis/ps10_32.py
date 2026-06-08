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
from pymeasure.instruments.validators import strict_discrete_set, strict_range

from .owis_base import OWISAxis, OWISBase

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PS10_32Axis(OWISAxis):
    """Axis channel for the PS 10-32, extending :class:`OWISAxis` with
    PS 10-32-specific axis commands.
    """

    amp_mode = Channel.control(
        "?AMPMODE{ch}", "AMPMODE{ch}=%d",
        """Control the amplifier mode register (int).

        * Bits 0–1 – de-excitation type
          (00=slow, 01=15 % mixed, 10=48 % mixed, 11=fast)
        * Bit 2 – blanking time (0=short, 1=long)
        * Bit 3 – external mode: de-excitation when enable goes low
        * Bit 4 – withdraw current at zero crossing
        * Bit 5 – invert rotational direction (stepper motor)
        """,
        cast=int,
    )

    amp_state = Channel.measurement(
        "?AMPST{ch}",
        """Get the amplifier status bits.

        * Bit 0 – temperature error
        * Bit 1 – emergency-stop triggered
        * Bit 2 – wrong motor code detected
        * Bit 3 – short-circuit protection activated
        """,
        cast=str,
    )


class PS10_32(OWISBase):
    """OWIS PS 10-32 single-axis position control unit driver.

    The PS 10-32 can drive either a 2-phase open-loop stepper motor (up to
    1.8 A) or a closed-loop DC servo motor (up to 3.5 A) over a USB ASCII
    interface.  Up to 32 units can be networked via a simplified CANopen bus;
    the unit connected to the PC by USB acts as master.  When networking,
    prepend a 2-digit slave ID to every command by passing ``slave_id`` on
    construction.

    :param adapter: A string VISA resource name (e.g.
        ``'ASRL/dev/ttyUSB0::INSTR'`` or ``'COM3'``) or an
        :class:`~pymeasure.adapters.Adapter` subclass object.
    :param name: Instrument name string.
    :param slave_id: Optional 2-digit slave ID (0–99) for CANopen networking.
        When ``None`` (default), commands are sent without a slave-address
        prefix (master / stand-alone mode).

    Example usage::

        from pymeasure.instruments.owis import PS10_32

        stage = PS10_32('ASRL/dev/ttyUSB0::INSTR')
        stage.axis1.initialize()
        stage.axis1.positioning_mode = 'ABSOL'
        stage.axis1.target_position = 10000
        stage.axis1.max_velocity = 20000
        stage.axis1.acceleration = 100000
        stage.axis1.start_positioning()
        stage.axis1.wait_for_stop()
    """

    axis1 = Instrument.ChannelCreator(PS10_32Axis, 1)

    # ── PS 10-32 specific instrument-level properties ────────────────────────

    output_mode = Instrument.control(
        "?OUTMODE", "OUTMODE=%d",
        """Control the operating mode of digital outputs Out1 and Out2 (int).

        * ``0`` – both outputs digital
        * ``1`` – Out1 digital, Out2 PWM
        * ``2`` – both outputs PWM
        """,
        validator=strict_discrete_set,
        values={0, 1, 2},
        cast=int,
    )

    slave_id_register = Instrument.control(
        "?SLAVEID", "SLAVEID=%d",
        """Control the CANopen slave ID stored on this unit (int, 0–99).

        This is the ID the unit uses on the CAN bus, not the ``slave_id``
        constructor parameter used by this driver to address the unit.
        """,
        validator=strict_range,
        values=[0, 99],
        cast=int,
    )

    # ── Construction ─────────────────────────────────────────────────────────

    def __init__(self, adapter, name="OWIS PS 10-32", slave_id=None, **kwargs):
        self._slave_id = slave_id
        super().__init__(adapter, name, **kwargs)

    def write(self, command):
        """Prepend the 2-digit slave ID when in networked (CANopen) mode."""
        if self._slave_id is not None:
            command = "%02d%s" % (self._slave_id, command)
        super().write(command)

    # ── PS 10-32 specific methods ─────────────────────────────────────────────

    def save_parameters(self):
        """Save all current parameters to EEPROM.

        Call this after changing the configuration to make the settings
        persistent across power cycles.
        """
        self.write("SAVEPARA")
