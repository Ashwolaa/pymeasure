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

"""Shared base classes for OWIS PS-series motion controllers."""

import logging
from time import sleep

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class OWISAxis(Channel):
    """Per-axis properties and methods shared by all OWIS PS-series controllers.

    The axis number is the channel id (``{ch}``).  Do not instantiate
    directly; access through the parent instrument::

        stage.axis1.target_position = 10000
        stage.axis1.start_positioning()
        stage.axis1.wait_for_stop()
    """

    #: Axis-state characters that indicate active motion.
    MOVING_STATES = frozenset("TVPFHS")

    # ── Status ──────────────────────────────────────────────────────────────

    limit_switch_state = Channel.measurement(
        "?ESTAT{ch}",
        """Get the logical state of the limit switches and power-stage feedback
        as a 5-character binary string.

        Bit order (left = MSB):
        ``<power-stage error, MAXSTOP, MAXDEC, MINDEC, MINSTOP>``.
        """,
        cast=str,
    )

    position_error = Channel.measurement(
        "?POSERR{ch}",
        """Get the current position error (encoder position − target position)
        in counts (int).""",
        cast=int,
    )

    actual_velocity = Channel.measurement(
        "?VACT{ch}",
        """Get the current speed in counts/cycle (int).""",
        cast=int,
    )

    encoder_position = Channel.measurement(
        "?ENCPOS{ch}",
        """Get the encoder position counter in counts (int).
        Also valid for open-loop stepper motors fitted with an encoder.
        """,
        cast=int,
    )

    reference_valid = Channel.measurement(
        "?REFST{ch}",
        """Get whether the reference position is valid (int).
        ``1`` = valid (reference run completed successfully), ``0`` = not valid.
        """,
        cast=int,
    )

    reference_hysteresis = Channel.measurement(
        "?HYST{ch}",
        """Get the measured hysteresis of the reference switch in counts (int).
        Only meaningful after a successful reference run when no switch is active.
        """,
        cast=int,
    )

    soft_limit_state = Channel.measurement(
        "?LSTAT{ch}",
        """Get the software position-limit state as a 2-character binary string.
        Bit 0 = MINDEC (lower limit exceeded), Bit 1 = MAXDEC (upper exceeded).
        """,
        cast=str,
    )

    # ── Base Configuration ───────────────────────────────────────────────────

    motor_type = Channel.control(
        "?MOTYPE{ch}", "MOTYPE{ch}=%d",
        """Control the motor type (int).

        * ``0`` – DC brush motor (closed-loop)
        * ``1`` – 2-phase stepper motor (open-loop)

        An :meth:`initialize` call is required afterwards.
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    current_range = Channel.control(
        "?AMPSHNT{ch}", "AMPSHNT{ch}=%d",
        """Control the current range of the motor power stage (int).

        * ``0`` – range 1 (low)
        * ``1`` – range 2 (high)

        An :meth:`initialize` call is required afterwards.
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    # ── Positioning Operation ────────────────────────────────────────────────

    target_position = Channel.control(
        "?PSET{ch}", "PSET{ch}=%d",
        """Control the target position (absolute mode) or travel distance
        (relative mode) in counts (int).
        Range: −2 147 483 648 … +2 147 483 647.
        """,
        cast=int,
    )

    velocity_setpoint = Channel.control(
        "?VVEL{ch}", "VVEL{ch}=%d",
        """Control the target speed for velocity mode (counts/cycle, int).
        Positive → positive direction; negative → negative direction.
        """,
        cast=int,
    )

    position_counter = Channel.control(
        "?CNT{ch}", "CNT{ch}=%d",
        """Control the current position counter in counts (int).""",
        cast=int,
    )

    positioning_mode = Channel.control(
        "?MODE{ch}", "%s{ch}",
        """Control the coordinate-entry mode (str).

        * ``'ABSOL'`` – absolute position
        * ``'RELAT'`` – relative position (travel distance)
        """,
        validator=strict_discrete_set,
        values={"ABSOL", "RELAT"},
    )

    # ── Positioning Parameters ───────────────────────────────────────────────

    max_velocity = Channel.control(
        "?PVEL{ch}", "PVEL{ch}=%d",
        """Control the maximum positioning velocity (counts/cycle, int).
        Range: 1–2 147 483 647.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    release_velocity = Channel.control(
        "?FVEL{ch}", "FVEL{ch}=%d",
        """Control the limit-switch release speed (counts/cycle, int).
        Range: 1–2 147 483 647.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    acceleration = Channel.control(
        "?ACC{ch}", "ACC{ch}=%d",
        """Control the acceleration ramp (counts/cycle², int).
        Applied in all motion modes.  Range: 1–2 147 483 647.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    microstep_resolution = Channel.control(
        "?MCSTP{ch}", "MCSTP{ch}=%d",
        """Control the micro-step resolution for stepper axes (int).""",
        cast=int,
    )

    drive_current = Channel.control(
        "?DRICUR{ch}", "DRICUR{ch}=%d",
        """Control the drive current as a percentage of the maximum for the
        selected current range (int, 0–100 %).
        Stepper: run current; DC servo: current limit.
        """,
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    holding_current = Channel.control(
        "?HOLCUR{ch}", "HOLCUR{ch}=%d",
        """Control the holding current for stepper axes as a percentage of the
        maximum for the selected current range (int, 0–100 %).
        """,
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    timeout = Channel.control(
        "?ATOT{ch}", "ATOT{ch}=%d",
        """Control the motion timeout in milliseconds (int).
        Setting to ``0`` disables timeout monitoring.
        """,
        validator=truncated_range,
        values=[0, 2 ** 32 - 1],
        cast=int,
    )

    pid_kp = Channel.control(
        "?FKP{ch}", "FKP{ch}=%d",
        """Control the proportional gain (Kp) of the PID servo loop
        (int, 0–32 767).
        """,
        validator=strict_range,
        values=[0, 32767],
        cast=int,
    )

    pid_kd = Channel.control(
        "?FKD{ch}", "FKD{ch}=%d",
        """Control the derivative gain (Kd) of the PID servo loop
        (int, 0–32 767).
        """,
        validator=strict_range,
        values=[0, 32767],
        cast=int,
    )

    pid_ki = Channel.control(
        "?FKI{ch}", "FKI{ch}=%d",
        """Control the integral gain (Ki) of the PID servo loop
        (int, 0–32 767).
        """,
        validator=strict_range,
        values=[0, 32767],
        cast=int,
    )

    pid_integration_limit = Channel.control(
        "?FIL{ch}", "FIL{ch}=%d",
        """Control the integration limit of the PID servo loop
        (int, 0–2 124 483 647).
        """,
        validator=strict_range,
        values=[0, 2124483647],
        cast=int,
    )

    sample_time = Channel.control(
        "?FST{ch}", "FST{ch}=%d",
        """Control the servo-loop sample time in microseconds (int, 204–20 000 µs).
        """,
        validator=strict_range,
        values=[204, 20000],
        cast=int,
    )

    derivative_delay = Channel.control(
        "?FDT{ch}", "FDT{ch}=%d",
        """Control the delay of the derivative (Kd) term in sample-time
        cycles (int).
        """,
        cast=int,
    )

    max_position_error = Channel.control(
        "?MXPOSERR{ch}", "MXPOSERR{ch}=%d",
        """Control the maximum allowable position error in counts (int).
        When exceeded, the DC-servo axis is switched off.
        """,
        cast=int,
    )

    max_output = Channel.control(
        "?MAXOUT{ch}", "MAXOUT{ch}=%d",
        """Control the maximum servo-amplifier output as a percentage
        (int, 0–99 %).
        """,
        validator=strict_range,
        values=[0, 99],
        cast=int,
    )

    pwm_frequency = Channel.control(
        "?AMPPWMF{ch}", "AMPPWMF{ch}=%d",
        """Control the PWM switching frequency of the drive board in Hz (int).
        Allowed values: ``20000`` or ``80000``.
        """,
        validator=strict_discrete_set,
        values={20000, 80000},
        cast=int,
    )

    phase_init_time = Channel.control(
        "?PHINTIM{ch}", "PHINTIM{ch}=%d",
        """Control the phase-initialisation time for stepper axes in multiples
        of the cycle time (int).
        """,
        cast=int,
    )

    # ── Reference Travel & Limit-Switch Configuration ────────────────────────

    reference_slow_speed = Channel.control(
        "?RVELS{ch}", "RVELS{ch}=%d",
        """Control the slow reference speed (counts/cycle, signed int).
        Used when searching for the index pulse or releasing the reference
        switch.
        """,
        cast=int,
    )

    reference_fast_speed = Channel.control(
        "?RVELF{ch}", "RVELF{ch}=%d",
        """Control the fast reference speed (counts/cycle, signed int).
        The axis approaches the limit/reference switch at this speed.
        """,
        cast=int,
    )

    reference_deceleration = Channel.control(
        "?RDACC{ch}", "RDACC{ch}=%d",
        """Control the deceleration used when approaching the reference point
        (counts/cycle², int).  Range: 1–2 147 483 647.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    limit_switch_mask = Channel.control(
        "?SMK{ch}", "SMK{ch}=%s",
        """Control the limit/brake-switch mask as a 4-character binary string
        (bit order: MAXSTOP, MAXDEC, MINDEC, MINSTOP).
        Set a bit to ``'1'`` to activate the corresponding switch.
        """,
        cast=str,
    )

    limit_switch_polarity = Channel.control(
        "?SPL{ch}", "SPL{ch}=%s",
        """Control the active level of the limit/brake switches as a 4-character
        binary string (bit order: MAXSTOP, MAXDEC, MINDEC, MINSTOP).
        ``'0'`` = low-active, ``'1'`` = high-active.
        """,
        cast=str,
    )

    reference_switch_mask = Channel.control(
        "?RMK{ch}", "RMK{ch}=%s",
        """Control the reference-switch mask as a 4-character binary string
        (bit order: MAXSTOP, MAXDEC, MINDEC, MINSTOP).
        Exactly one bit must be set.
        """,
        cast=str,
    )

    reference_switch_polarity = Channel.control(
        "?RPL{ch}", "RPL{ch}=%s",
        """Control the active level of the reference switch as a 4-character
        binary string (bit order: MAXSTOP, MAXDEC, MINDEC, MINSTOP).
        """,
        cast=str,
    )

    soft_limit_mask = Channel.control(
        "?LMK{ch}", "LMK{ch}=%s",
        """Control the software position-limit monitoring mask as a 2-character
        binary string (bit order: MAXDEC, MINDEC).
        Set a bit to ``'1'`` to activate the corresponding software limit.
        """,
        cast=str,
    )

    soft_limit_min = Channel.control(
        "?SLMIN{ch}", "SLMIN{ch}=%d",
        """Control the negative (lower) software limit position (counts, int).""",
        cast=int,
    )

    soft_limit_max = Channel.control(
        "?SLMAX{ch}", "SLMAX{ch}=%d",
        """Control the positive (upper) software limit position (counts, int).""",
        cast=int,
    )

    # ── Holding Brake ────────────────────────────────────────────────────────

    holding_brake_channel = Channel.control(
        "?HBCH{ch}", "HBCH{ch}=%d",
        """Control the PWM port assigned to the holding brake (int).
        ``0`` disables the holding-brake function; ``1`` or ``2`` selects a
        PWM port.
        """,
        validator=strict_discrete_set,
        values={0, 1, 2},
        cast=int,
    )

    holding_brake_first_pwm = Channel.control(
        "?HBFV{ch}", "HBFV{ch}=%d",
        """Control the first (activation) PWM duty cycle for the holding brake
        in percent (int, 0–100).  Applied for :attr:`holding_brake_settle_time`
        milliseconds to pull the brake in fully.
        """,
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    holding_brake_second_pwm = Channel.control(
        "?HBSV{ch}", "HBSV{ch}=%d",
        """Control the second (hold) PWM duty cycle for the holding brake in
        percent (int, 0–100).  Applied after the settling time.
        """,
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    holding_brake_settle_time = Channel.control(
        "?HBTI{ch}", "HBTI{ch}=%d",
        """Control the settling time for the holding brake in milliseconds
        (int).  The first PWM value is applied for this duration before
        switching to the hold value.
        """,
        cast=int,
    )

    # ── Action Methods ────────────────────────────────────────────────────────

    def initialize(self):
        """Enable the motor power stage and activate the position-control loop.

        Must be called after power-on—and after any motor type or current-range
        change—before issuing motion commands.
        """
        self.write("INIT{ch}")

    def start_positioning(self):
        """Start trapezoidal point-to-point positioning.

        Moves to :attr:`target_position` using :attr:`max_velocity` and
        :attr:`acceleration`.
        """
        self.write("PGO{ch}")

    def start_velocity_mode(self):
        """Start velocity mode.

        Accelerates to :attr:`velocity_setpoint` using :attr:`acceleration`
        and runs until :meth:`stop_velocity_mode` or :meth:`stop` is called.
        """
        self.write("VGO{ch}")

    def stop(self):
        """Stop any active motion using the preset deceleration ramp."""
        self.write("STOP{ch}")

    def stop_velocity_mode(self):
        """Terminate velocity mode and stop using the deceleration ramp."""
        self.write("VSTP{ch}")

    def free_limit_switch(self):
        """Release the axis from an active limit switch or brake switch.

        Call after tripping MINSTOP, MAXSTOP, MINDEC, or MAXDEC.  The
        controller selects the release direction automatically.
        """
        self.write("EFREE{ch}")

    def enable_motor(self):
        """Enable the motor power stage and position-control loop."""
        self.write("MON{ch}")

    def disable_motor(self):
        """Disable the motor power stage and position-control loop."""
        self.write("MOFF{ch}")

    def reset_position_counter(self):
        """Reset the position counter to zero."""
        self.write("CRES{ch}")

    def reference_move(self, mode=4):
        """Start a reference travel.

        :param mode: Reference mode integer (0–7):

            * ``0`` – search for next index pulse and stop
            * ``1`` – approach reference switch and stop
            * ``2`` – approach reference switch, then search index pulse, stop
            * ``3`` – mode 0 + set current position to 0
            * ``4`` – mode 1 + set current position to 0 (default)
            * ``5`` – mode 2 + set current position to 0
            * ``6`` – approach max reference switch, then min, set position 0
            * ``7`` – approach min reference switch, then max, set position 0
        """
        mode = strict_discrete_set(mode, [0, 1, 2, 3, 4, 5, 6, 7])
        self.write("REF{ch}=%d" % mode)

    def is_moving(self):
        """Return ``True`` if this axis is currently executing a motion command.

        The state for this axis is taken from the parent's :attr:`axis_state`
        string (one character per axis, 1-based).

        :returns: bool
        """
        state = self.parent.axis_state
        idx = self.id - 1
        return idx < len(state) and state[idx] in self.MOVING_STATES

    def wait_for_stop(self, interval=0.1):
        """Block until this axis has finished its current motion.

        :param interval: Polling interval in seconds (default 0.1 s).
        """
        while self.is_moving():
            sleep(interval)


class OWISBase(Instrument):
    """Base class for OWIS PS-series motion controllers.

    Provides instrument-level properties and methods that are common across
    the PS product family.  Subclasses add the appropriate
    :class:`OWISAxis` channel(s) and any device-specific commands.
    """

    def __init__(self, adapter, name, **kwargs):
        kwargs.setdefault("write_termination", "\r")
        kwargs.setdefault("read_termination", "\r")
        kwargs.setdefault("timeout", 2000)
        super().__init__(adapter, name, includeSCPI=False,
                         asrl={"baud_rate": 9600}, **kwargs)

    # ── General Status ───────────────────────────────────────────────────────

    version = Instrument.measurement(
        "?VERSION",
        """Get the firmware version string.""",
    )

    serial_number = Instrument.measurement(
        "?SERNUM",
        """Get the serial number.""",
        cast=str,
    )

    axis_state = Instrument.measurement(
        "?ASTAT",
        """Get the current state of all axes as a string (one character per axis).

        Common characters (see device manual for full list):

        * ``'I'`` – not initialised
        * ``'O'`` – disabled
        * ``'R'`` – ready
        * ``'T'`` – trapezoidal positioning
        * ``'S'`` – S-curve positioning (PS 35 only)
        * ``'V'`` – velocity mode
        * ``'P'`` – reference motion
        * ``'F'`` – freeing a limit switch
        * ``'H'`` – phase initialisation (stepper)
        * ``'L'`` – disabled after hardware limit switch
        * ``'Z'`` – disabled after timeout
        """,
    )

    error_message = Instrument.measurement(
        "?MSG",
        """Get the last entry in the command-error message buffer.
        Returns ``'00 NO MESSAGE AVAILABLE'`` when the buffer is empty.
        """,
    )

    error_code = Instrument.measurement(
        "?ERR",
        """Get the next error code from the error memory (depth 20).
        Returns ``0`` when no further errors are stored.
        """,
        cast=int,
    )

    emergency_stop_state = Instrument.measurement(
        "?EMERGINP",
        """Get the current state of the emergency-stop input (``1`` = active).""",
        cast=int,
    )

    # ── Base Configuration ───────────────────────────────────────────────────

    baudrate = Instrument.control(
        "?BAUDRATE", "BAUDRATE=%d",
        """Control the serial interface baud rate (int).
        Allowed values: 9600, 19200, 38400, 57600, 115200.
        The new rate takes effect only after the next reset or power-on.
        """,
        validator=strict_discrete_set,
        values={9600, 19200, 38400, 57600, 115200},
        cast=int,
    )

    command_end = Instrument.control(
        "?COMEND", "COMEND=%d",
        """Control the command termination character (int).

        * ``0`` – CR (default)
        * ``1`` – CR + LF
        * ``2`` – LF
        """,
        validator=strict_discrete_set,
        values={0, 1, 2},
        cast=int,
    )

    terminal_mode = Instrument.control(
        "?TERM", "TERM=%d",
        """Control the terminal response mode (int).

        * ``0`` – short: error code only (fastest throughput)
        * ``1`` – error code + plain-text explanation
        * ``2`` – same as 1, plus ``'OK'`` acknowledgement after every
          write-only command
        """,
        validator=strict_discrete_set,
        values={0, 1, 2},
        cast=int,
    )

    # ── I/O ──────────────────────────────────────────────────────────────────

    inputs = Instrument.measurement(
        "?INPUTS",
        """Get the state of the TTL inputs as a binary string.""",
        cast=str,
    )

    outputs = Instrument.measurement(
        "?OUTPUTS",
        """Get the current state of all digital outputs as a binary string.""",
        cast=str,
    )

    # ── Action Methods ────────────────────────────────────────────────────────

    def set_output(self, port, value):
        """Set a digital output.

        :param port: Output port number (integer, 1-based).
        :param value: Output state (``0`` = low, ``1`` = high).
        """
        port = int(port)
        value = strict_discrete_set(int(value), [0, 1])
        self.write("OUTPUT%d=%d" % (port, value))

    def get_analog_input(self, port):
        """Read the 10-bit value of an analog input.

        :param port: Analog input port number.
        :returns: Integer 0–1023 (maps to 0–5 V).
        """
        return int(self.ask("?ANIN%d" % int(port)))

    def set_pwm_output(self, port, value):
        """Set a PWM output level.

        :param port: PWM output port number.
        :param value: Duty cycle as a percentage (0–100 %).
        """
        value = strict_range(int(value), [0, 100])
        self.write("OPWM%d=%d" % (int(port), value))

    def get_pwm_output(self, port):
        """Read the current PWM output level.

        :param port: PWM output port number.
        :returns: Integer duty cycle 0–100 (%).
        """
        return int(self.ask("?OPWM%d" % int(port)))

    def clear_errors(self):
        """Clear the error memory."""
        self.write("ERRCLEAR")

    def reset_board(self):
        """Issue a main-board reset."""
        self.write("RESETMB")

    def is_moving(self):
        """Return ``True`` if any axis is currently executing a motion command.

        Queries :attr:`axis_state` once and checks all axis characters,
        avoiding one round-trip per axis.
        """
        return any(c in OWISAxis.MOVING_STATES for c in self.axis_state)

    def wait_for_stop(self, interval=0.1):
        """Block until all axes have finished their current motion.

        :param interval: Polling interval in seconds (default 0.1 s).
        """
        while self.is_moving():
            sleep(interval)


# ── Intermediate classes shared by PS 35 and PS 90+ ──────────────────────────

class OWISAdvancedAxis(OWISAxis):
    """Axis channel shared by the PS 35 and PS 90+, extending
    :class:`OWISAxis` with commands present on both devices but absent from
    the PS 10-32.
    """

    # ── Motor type (PS 35 / PS 90+ codes) ────────────────────────────────────

    motor_type = Channel.control(
        "?MOTYPE{ch}", "MOTYPE{ch}=%d",
        """Control the motor type for this axis (int).

        * ``0`` – DC brush motor (closed-loop)
        * ``2`` – 2-phase stepper motor (open-loop)
        * ``3`` – 2-phase stepper motor (closed-loop)
        * ``4`` – BLDC motor

        An :meth:`~OWISAxis.initialize` call is required after changing.
        """,
        validator=strict_discrete_set,
        values={0, 2, 3, 4},
        cast=int,
    )

    # ── Additional positioning parameters ────────────────────────────────────

    deceleration = Channel.control(
        "?DACC{ch}", "DACC{ch}=%d",
        """Control the deceleration ramp (counts/cycle², int).
        Used for all modes except S-curve (where
        :attr:`~OWISAxis.acceleration` is used for both ramps).
        Range: 1–2 147 483 647.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    jerk = Channel.control(
        "?JACC{ch}", "JACC{ch}=%d",
        """Control the maximum jerk for S-curve profiling (counts/cycle³, int).
        Only used when :attr:`positioning_profile` is ``1`` (S-curve).
        """,
        cast=int,
    )

    emergency_deceleration = Channel.control(
        "?EDACC{ch}", "EDACC{ch}=%d",
        """Control the emergency-stop deceleration (counts/cycle², int).
        Applied when a brake switch (MINDEC/MAXDEC) responds.
        """,
        validator=strict_range,
        values=[1, 2147483647],
        cast=int,
    )

    positioning_profile = Channel.control(
        "?PMOD{ch}", "PMOD{ch}=%d",
        """Control the positioning profile mode (int).

        * ``0`` – trapezoidal (default)
        * ``1`` – S-curve (requires :attr:`jerk` to be set)
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    # ── In-position reporting ─────────────────────────────────────────────────

    inpos_mode = Channel.control(
        "?INPOSMOD{ch}", "INPOSMOD{ch}=%d",
        """Control the end-of-motion reporting mode (int).

        * ``0`` – target position reached
        * ``1`` – actual position within settling window for
          :attr:`inpos_time`
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    inpos_time = Channel.control(
        "?INPOSTIM{ch}", "INPOSTIM{ch}=%d",
        """Control the end-of-motion reporting time in multiples of the cycle
        time (int).  Used when :attr:`inpos_mode` is ``1``.
        """,
        cast=int,
    )

    inpos_window = Channel.control(
        "?INPOSWND{ch}", "INPOSWND{ch}=%d",
        """Control the end-of-motion settling window in encoder counts (int).
        Used when :attr:`inpos_mode` is ``1``.
        """,
        cast=int,
    )

    # ── Axis enable ───────────────────────────────────────────────────────────

    enabled = Channel.control(
        "?AXIS{ch}", "AXIS{ch}=%d",
        """Control whether this axis is released/enabled (bool-like int).
        ``1`` = released, ``0`` = not released.
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    # ── Axis signals ──────────────────────────────────────────────────────────

    axis_signals = Channel.measurement(
        "?AXSIGNALS{ch}",
        """Get the raw hardware axis signals as a binary string.

        Bit layout varies by model — see the device manual for the full
        bit assignment.  Common bits:

        * Bit 0 – encoder CHA
        * Bit 1 – encoder CHB
        * Bit 2 – encoder Index
        * Bit 3 – encoder Home
        * Bit 4 – MAXSTOP
        * Bit 5 – MINSTOP
        """,
        cast=str,
    )

    # ── Encoder / motor configuration ────────────────────────────────────────

    encoder_lines = Channel.control(
        "?ENCLINES{ch}", "ENCLINES{ch}=%d",
        """Control the encoder line number (int).""",
        cast=int,
    )

    motor_poles = Channel.control(
        "?MOTPOLES{ch}", "MOTPOLES{ch}=%d",
        """Control the motor pole number for brushless DC axes (int).""",
        cast=int,
    )

    encoder_counts_per_cycle = Channel.control(
        "?ELCYCNT{ch}", "ELCYCNT{ch}=%d",
        """Control the encoder counts per electrical commutation cycle (int).
        """,
        cast=int,
    )

    phase_init_amplitude = Channel.control(
        "?PHINAMP{ch}", "PHINAMP{ch}=%d",
        """Control the phase-initialisation amplitude in percent (int, 0–100).
        """,
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    # ── Joystick per-axis settings ────────────────────────────────────────────

    joystick_velocity = Channel.control(
        "?JVEL{ch}", "JVEL{ch}=%d",
        """Control the maximum axis velocity at full joystick deflection
        (counts/cycle, signed int).
        """,
        cast=int,
    )

    joystick_acceleration = Channel.control(
        "?JOYACC{ch}", "JOYACC{ch}=%d",
        """Control the axis acceleration and deceleration for joystick travel
        (counts/cycle², int).
        """,
        cast=int,
    )

    # ── Interpolation ─────────────────────────────────────────────────────────

    interpolation_velocity = Channel.control(
        "?IVEL{ch}", "IVEL{ch}=%d",
        """Control the maximum velocity for this axis during linear
        interpolation (counts/cycle, signed int).
        """,
        cast=int,
    )

    interpolation_acceleration = Channel.control(
        "?IACC{ch}", "IACC{ch}=%d",
        """Control the maximum acceleration for this axis during linear
        interpolation (counts/cycle², signed int).
        """,
        cast=int,
    )

    # ── Measured travel ───────────────────────────────────────────────────────

    measured_travel = Channel.measurement(
        "?MXSTROKE{ch}",
        """Get the travel measured during reference mode 6 or 7
        (counts, int).
        """,
        cast=int,
    )

    # ── Methods ───────────────────────────────────────────────────────────────

    def change_target(self, position):
        """Change the target position while the axis is moving
        (trapezoidal profile only).

        :param position: New signed target position (or distance in relative
            mode) in counts (int).
        """
        self.write("PCHANGE{ch}=%d" % int(position))

    @property
    def command_position(self):
        """Get the current target position of the PID regulator
        (counts, int).
        """
        return int(self.ask("?CMDPOS{ch}"))

    def set_ttl_outputs(self, mask):
        """Assert (set) TTL output bits for the motor power stage of this
        axis.

        :param mask: Binary string mask of bits to set (e.g. ``'10'``).
        """
        self.write("ETTLOUTS{ch}=%s" % str(mask))

    def clear_ttl_outputs(self, mask):
        """De-assert (clear) TTL output bits for the motor power stage of
        this axis.

        :param mask: Binary string mask of bits to clear (e.g. ``'01'``).
        """
        self.write("ETTLOUTC{ch}=%s" % str(mask))

    def set_axis_output(self, value):
        """Set the axis out-pin high or low.

        :param value: ``1`` = high, ``0`` = low.
        """
        value = strict_discrete_set(int(value), [0, 1])
        self.write("AXOUTPUT{ch}=%d" % value)


class OWISAdvancedBase(OWISBase):
    """Instrument base class shared by the PS 35 and PS 90+, extending
    :class:`OWISBase` with commands present on both devices but absent from
    the PS 10-32.

    Subclasses must set :attr:`_axis_ids` to define the default axes for
    :meth:`save_parameters` and :meth:`load_parameters`.
    """

    #: Axis IDs included in save/load by default.  Override in subclasses.
    _axis_ids = ()

    # ── Firmware / diagnostics ────────────────────────────────────────────────

    motion_controller_version = Instrument.measurement(
        "?MCTRVER",
        """Get the version data for the motion controller chips.""",
    )

    program_checksum = Instrument.measurement(
        "?PCHECK",
        """Get the checksum of the programme memory (int).""",
        cast=int,
    )

    # ── Joystick instrument-level settings ────────────────────────────────────

    joystick_zone = Instrument.control(
        "?JZONE", "JZONE=%d",
        """Control the inactive (dead) zone of the joystick (int, 0–256).""",
        validator=strict_range,
        values=[0, 256],
        cast=int,
    )

    joystick_center_x = Instrument.control(
        "?JZEROX", "JZEROX=%d",
        """Control the centre-point calibration value for the X joystick
        axis (int).
        """,
        cast=int,
    )

    joystick_center_y = Instrument.control(
        "?JZEROY", "JZEROY=%d",
        """Control the centre-point calibration value for the Y joystick
        axis (int).
        """,
        cast=int,
    )

    joystick_center_z = Instrument.control(
        "?JZEROZ", "JZEROZ=%d",
        """Control the centre-point calibration value for the Z joystick
        axis (int).
        """,
        cast=int,
    )

    joystick_button = Instrument.control(
        "?JBUTTON", "JBUTTON=%d",
        """Control whether the joystick button is evaluated (int).
        ``1`` = evaluation enabled, ``0`` = disabled.
        """,
        validator=strict_discrete_set,
        values={0, 1},
        cast=int,
    )

    joystick_plane_x = Instrument.control(
        "?JPLAX", "JPLAX=%d",
        """Control which axis number is assigned to the joystick X plane
        (int, 0 = disabled).
        """,
        cast=int,
    )

    joystick_plane_y = Instrument.control(
        "?JPLAY", "JPLAY=%d",
        """Control which axis number is assigned to the joystick Y plane
        (int, 0 = disabled).
        """,
        cast=int,
    )

    joystick_plane_z = Instrument.control(
        "?JPLAZ", "JPLAZ=%d",
        """Control which axis number is assigned to the joystick Z plane
        (int, 0 = disabled).
        """,
        cast=int,
    )

    # ── TTL I/O ───────────────────────────────────────────────────────────────

    ttl_inputs = Instrument.measurement(
        "?INPTTL",
        """Get the current state of all TTL inputs as a binary string.""",
        cast=str,
    )

    ttl_outputs = Instrument.measurement(
        "?OUTTTL",
        """Get the current state of all TTL outputs as a binary string.""",
        cast=str,
    )

    # ── Action Methods ────────────────────────────────────────────────────────

    def set_ttl_output(self, port, value):
        """Set a TTL digital output.

        :param port: Output port number (integer, 1-based).
        :param value: Output state (``0`` = low, ``1`` = high).
        """
        value = strict_discrete_set(int(value), [0, 1])
        self.write("OUTTTL%d=%d" % (int(port), value))

    def joystick_on(self):
        """Activate joystick mode for the configured joystick axes."""
        self.write("JOYON")

    def joystick_off(self):
        """Terminate joystick mode."""
        self.write("JOYOFF")

    def start_linear_interpolation(self, axis_mask):
        """Start positioning with linear interpolation for a group of axes.

        :param axis_mask: Binary axis mask string, bit order
            ``<axis_n, …, axis_1>``.  E.g. ``'011'`` moves axes 1 and 2.
        """
        self.write("LIGO=%s" % str(axis_mask))

    def save_parameters(self, axes=None):
        """Save parameters to non-volatile FRAM.

        :param axes: Iterable of axis numbers whose axis parameters should be
            saved.  Defaults to all axes declared for this device
            (:attr:`_axis_ids`).  Pass an empty iterable to save only the
            global parameters.
        """
        if axes is None:
            axes = list(self._axis_ids)
        self.write("SAVEGLOB")
        for n in axes:
            self.write("SAVEAXPA%d" % n)

    def load_parameters(self, axes=None):
        """Reload parameters from non-volatile FRAM.

        :param axes: Iterable of axis numbers to reload.  Defaults to all
            axes declared for this device (:attr:`_axis_ids`).
        """
        if axes is None:
            axes = list(self._axis_ids)
        self.write("LOADGLOB")
        for n in axes:
            self.write("LOADAXPA%d" % n)
