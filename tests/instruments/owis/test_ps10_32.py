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

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.owis import PS10_32


# ── Initialisation ──────────────────────────────────────────────────────────

def test_init():
    with expected_protocol(PS10_32, []):
        pass


def test_init_with_slave_id():
    with expected_protocol(PS10_32, [], slave_id=5):
        pass


# ── Instrument-level: General Status ────────────────────────────────────────

def test_version():
    with expected_protocol(PS10_32,
                           [("?VERSION", "PS10-V3.0-181010")]) as instr:
        assert instr.version == "PS10-V3.0-181010"


def test_serial_number():
    with expected_protocol(PS10_32,
                           [("?SERNUM", "09080145")]) as instr:
        assert instr.serial_number == "09080145"


def test_axis_state():
    with expected_protocol(PS10_32,
                           [("?ASTAT", "R")]) as instr:
        assert instr.axis_state == "R"


def test_error_message():
    with expected_protocol(PS10_32,
                           [("?MSG", "00 NO MESSAGE AVAILABLE")]) as instr:
        assert instr.error_message == "00 NO MESSAGE AVAILABLE"


def test_error_code():
    with expected_protocol(PS10_32,
                           [("?ERR", "1211")]) as instr:
        assert instr.error_code == 1211


def test_error_code_no_error():
    with expected_protocol(PS10_32,
                           [("?ERR", "0")]) as instr:
        assert instr.error_code == 0


def test_emergency_stop_state():
    with expected_protocol(PS10_32,
                           [("?EMERGINP", "1")]) as instr:
        assert instr.emergency_stop_state == 1


# ── Instrument-level: Base Configuration ────────────────────────────────────

@pytest.mark.parametrize("mode", [0, 1, 2])
def test_terminal_mode_getter(mode):
    with expected_protocol(PS10_32,
                           [("?TERM", str(mode))]) as instr:
        assert instr.terminal_mode == mode


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_terminal_mode_setter(mode):
    with expected_protocol(PS10_32,
                           [("TERM=%d" % mode, None)]) as instr:
        instr.terminal_mode = mode


# ── Instrument-level: I/O ────────────────────────────────────────────────────

def test_inputs():
    with expected_protocol(PS10_32,
                           [("?INPUTS", "0010")]) as instr:
        assert instr.inputs == "0010"


def test_outputs():
    with expected_protocol(PS10_32,
                           [("?OUTPUTS", "00101")]) as instr:
        assert instr.outputs == "00101"


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_output_mode_getter(mode):
    with expected_protocol(PS10_32,
                           [("?OUTMODE", str(mode))]) as instr:
        assert instr.output_mode == mode


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_output_mode_setter(mode):
    with expected_protocol(PS10_32,
                           [("OUTMODE=%d" % mode, None)]) as instr:
        instr.output_mode = mode


def test_slave_id_register_getter():
    with expected_protocol(PS10_32,
                           [("?SLAVEID", "64")]) as instr:
        assert instr.slave_id_register == 64


def test_slave_id_register_setter():
    with expected_protocol(PS10_32,
                           [("SLAVEID=64", None)]) as instr:
        instr.slave_id_register = 64


# ── Instrument-level: I/O methods ────────────────────────────────────────────

@pytest.mark.parametrize("port,value", [(1, 0), (1, 1), (2, 0)])
def test_set_output(port, value):
    with expected_protocol(PS10_32,
                           [("OUTPUT%d=%d" % (port, value), None)]) as instr:
        instr.set_output(port, value)


@pytest.mark.parametrize("port", [1, 2, 3, 4])
def test_get_analog_input(port):
    with expected_protocol(PS10_32,
                           [("?ANIN%d" % port, "512")]) as instr:
        assert instr.get_analog_input(port) == 512


@pytest.mark.parametrize("port,value", [(1, 55), (2, 0), (1, 100)])
def test_set_pwm_output(port, value):
    with expected_protocol(PS10_32,
                           [("OPWM%d=%d" % (port, value), None)]) as instr:
        instr.set_pwm_output(port, value)


@pytest.mark.parametrize("port", [1, 2])
def test_get_pwm_output(port):
    with expected_protocol(PS10_32,
                           [("?OPWM%d" % port, "55")]) as instr:
        assert instr.get_pwm_output(port) == 55


# ── Instrument-level: Action methods ─────────────────────────────────────────

def test_clear_errors():
    with expected_protocol(PS10_32,
                           [("ERRCLEAR", None)]) as instr:
        instr.clear_errors()


def test_reset_board():
    with expected_protocol(PS10_32,
                           [("RESETMB", None)]) as instr:
        instr.reset_board()


def test_save_parameters():
    with expected_protocol(PS10_32,
                           [("SAVEPARA", None)]) as instr:
        instr.save_parameters()


# ── Axis 1: Status ────────────────────────────────────────────────────────────

def test_limit_switch_state():
    with expected_protocol(PS10_32,
                           [("?ESTAT1", "10101")]) as instr:
        assert instr.axis1.limit_switch_state == "10101"


def test_position_error():
    with expected_protocol(PS10_32,
                           [("?POSERR1", "-15")]) as instr:
        assert instr.axis1.position_error == -15


def test_actual_velocity():
    with expected_protocol(PS10_32,
                           [("?VACT1", "10000")]) as instr:
        assert instr.axis1.actual_velocity == 10000


def test_encoder_position():
    with expected_protocol(PS10_32,
                           [("?ENCPOS1", "34567")]) as instr:
        assert instr.axis1.encoder_position == 34567


def test_reference_valid():
    with expected_protocol(PS10_32,
                           [("?REFST1", "1")]) as instr:
        assert instr.axis1.reference_valid == 1


# ── Axis 1: Base Configuration ───────────────────────────────────────────────

@pytest.mark.parametrize("value", [0, 1])
def test_motor_type_getter(value):
    with expected_protocol(PS10_32,
                           [("?MOTYPE1", str(value))]) as instr:
        assert instr.axis1.motor_type == value


@pytest.mark.parametrize("value", [0, 1])
def test_motor_type_setter(value):
    with expected_protocol(PS10_32,
                           [("MOTYPE1=%d" % value, None)]) as instr:
        instr.axis1.motor_type = value


@pytest.mark.parametrize("value", [0, 1])
def test_current_range_getter(value):
    with expected_protocol(PS10_32,
                           [("?AMPSHNT1", str(value))]) as instr:
        assert instr.axis1.current_range == value


@pytest.mark.parametrize("value", [0, 1])
def test_current_range_setter(value):
    with expected_protocol(PS10_32,
                           [("AMPSHNT1=%d" % value, None)]) as instr:
        instr.axis1.current_range = value


# ── Axis 1: Positioning Operation ────────────────────────────────────────────

def test_target_position_getter():
    with expected_protocol(PS10_32,
                           [("?PSET1", "100000")]) as instr:
        assert instr.axis1.target_position == 100000


def test_target_position_setter():
    with expected_protocol(PS10_32,
                           [("PSET1=100000", None)]) as instr:
        instr.axis1.target_position = 100000


def test_target_position_setter_negative():
    with expected_protocol(PS10_32,
                           [("PSET1=-50000", None)]) as instr:
        instr.axis1.target_position = -50000


def test_velocity_setpoint_getter():
    with expected_protocol(PS10_32,
                           [("?VVEL1", "-20000")]) as instr:
        assert instr.axis1.velocity_setpoint == -20000


def test_velocity_setpoint_setter():
    with expected_protocol(PS10_32,
                           [("VVEL1=-20000", None)]) as instr:
        instr.axis1.velocity_setpoint = -20000


def test_position_counter_getter():
    with expected_protocol(PS10_32,
                           [("?CNT1", "5000")]) as instr:
        assert instr.axis1.position_counter == 5000


def test_position_counter_setter():
    with expected_protocol(PS10_32,
                           [("CNT1=5000", None)]) as instr:
        instr.axis1.position_counter = 5000


@pytest.mark.parametrize("mode", ["ABSOL", "RELAT"])
def test_positioning_mode_getter(mode):
    with expected_protocol(PS10_32,
                           [("?MODE1", mode)]) as instr:
        assert instr.axis1.positioning_mode == mode


@pytest.mark.parametrize("mode", ["ABSOL", "RELAT"])
def test_positioning_mode_setter(mode):
    with expected_protocol(PS10_32,
                           [("%s1" % mode, None)]) as instr:
        instr.axis1.positioning_mode = mode


# ── Axis 1: Positioning Parameters ───────────────────────────────────────────

def test_max_velocity_getter():
    with expected_protocol(PS10_32,
                           [("?PVEL1", "10000")]) as instr:
        assert instr.axis1.max_velocity == 10000


def test_max_velocity_setter():
    with expected_protocol(PS10_32,
                           [("PVEL1=10000", None)]) as instr:
        instr.axis1.max_velocity = 10000


def test_acceleration_getter():
    with expected_protocol(PS10_32,
                           [("?ACC1", "300000")]) as instr:
        assert instr.axis1.acceleration == 300000


def test_acceleration_setter():
    with expected_protocol(PS10_32,
                           [("ACC1=300000", None)]) as instr:
        instr.axis1.acceleration = 300000


def test_drive_current_getter():
    with expected_protocol(PS10_32,
                           [("?DRICUR1", "50")]) as instr:
        assert instr.axis1.drive_current == 50


def test_drive_current_setter():
    with expected_protocol(PS10_32,
                           [("DRICUR1=50", None)]) as instr:
        instr.axis1.drive_current = 50


def test_holding_current_getter():
    with expected_protocol(PS10_32,
                           [("?HOLCUR1", "30")]) as instr:
        assert instr.axis1.holding_current == 30


def test_holding_current_setter():
    with expected_protocol(PS10_32,
                           [("HOLCUR1=30", None)]) as instr:
        instr.axis1.holding_current = 30


def test_timeout_getter():
    with expected_protocol(PS10_32,
                           [("?ATOT1", "20000")]) as instr:
        assert instr.axis1.timeout == 20000


def test_timeout_disable():
    with expected_protocol(PS10_32,
                           [("ATOT1=0", None)]) as instr:
        instr.axis1.timeout = 0


def test_pid_kp_getter():
    with expected_protocol(PS10_32,
                           [("?FKP1", "25")]) as instr:
        assert instr.axis1.pid_kp == 25


def test_pid_kp_setter():
    with expected_protocol(PS10_32,
                           [("FKP1=25", None)]) as instr:
        instr.axis1.pid_kp = 25


def test_pid_kd_setter():
    with expected_protocol(PS10_32,
                           [("FKD1=5", None)]) as instr:
        instr.axis1.pid_kd = 5


def test_pid_ki_setter():
    with expected_protocol(PS10_32,
                           [("FKI1=10", None)]) as instr:
        instr.axis1.pid_ki = 10


def test_max_output_getter():
    with expected_protocol(PS10_32,
                           [("?MAXOUT1", "95")]) as instr:
        assert instr.axis1.max_output == 95


def test_max_output_setter():
    with expected_protocol(PS10_32,
                           [("MAXOUT1=95", None)]) as instr:
        instr.axis1.max_output = 95


@pytest.mark.parametrize("freq", [20000, 80000])
def test_pwm_frequency_setter(freq):
    with expected_protocol(PS10_32,
                           [("AMPPWMF1=%d" % freq, None)]) as instr:
        instr.axis1.pwm_frequency = freq


# ── Axis 1: Reference Travel & Limit-Switch ───────────────────────────────────

def test_reference_slow_speed_setter():
    with expected_protocol(PS10_32,
                           [("RVELS1=2000", None)]) as instr:
        instr.axis1.reference_slow_speed = 2000


def test_reference_fast_speed_setter():
    with expected_protocol(PS10_32,
                           [("RVELF1=-20000", None)]) as instr:
        instr.axis1.reference_fast_speed = -20000


def test_limit_switch_mask_getter():
    with expected_protocol(PS10_32,
                           [("?SMK1", "0110")]) as instr:
        assert instr.axis1.limit_switch_mask == "0110"


def test_limit_switch_mask_setter():
    with expected_protocol(PS10_32,
                           [("SMK1=0110", None)]) as instr:
        instr.axis1.limit_switch_mask = "0110"


def test_limit_switch_polarity_setter():
    with expected_protocol(PS10_32,
                           [("SPL1=1111", None)]) as instr:
        instr.axis1.limit_switch_polarity = "1111"


def test_reference_switch_mask_getter():
    with expected_protocol(PS10_32,
                           [("?RMK1", "0001")]) as instr:
        assert instr.axis1.reference_switch_mask == "0001"


def test_reference_switch_mask_setter():
    with expected_protocol(PS10_32,
                           [("RMK1=0001", None)]) as instr:
        instr.axis1.reference_switch_mask = "0001"


def test_soft_limit_min_getter():
    with expected_protocol(PS10_32,
                           [("?SLMIN1", "100")]) as instr:
        assert instr.axis1.soft_limit_min == 100


def test_soft_limit_max_setter():
    with expected_protocol(PS10_32,
                           [("SLMAX1=100000", None)]) as instr:
        instr.axis1.soft_limit_max = 100000


# ── Axis 1: PS 10-32-specific (amp_mode, amp_state) ─────────────────────────

def test_amp_mode_getter():
    with expected_protocol(PS10_32,
                           [("?AMPMODE1", "3")]) as instr:
        assert instr.axis1.amp_mode == 3


def test_amp_mode_setter():
    with expected_protocol(PS10_32,
                           [("AMPMODE1=3", None)]) as instr:
        instr.axis1.amp_mode = 3


def test_amp_state():
    with expected_protocol(PS10_32,
                           [("?AMPST1", "0000")]) as instr:
        assert instr.axis1.amp_state == "0000"


# ── Axis 1: Action methods ────────────────────────────────────────────────────

def test_initialize():
    with expected_protocol(PS10_32,
                           [("INIT1", None)]) as instr:
        instr.axis1.initialize()


def test_start_positioning():
    with expected_protocol(PS10_32,
                           [("PGO1", None)]) as instr:
        instr.axis1.start_positioning()


def test_start_velocity_mode():
    with expected_protocol(PS10_32,
                           [("VGO1", None)]) as instr:
        instr.axis1.start_velocity_mode()


def test_stop():
    with expected_protocol(PS10_32,
                           [("STOP1", None)]) as instr:
        instr.axis1.stop()


def test_stop_velocity_mode():
    with expected_protocol(PS10_32,
                           [("VSTP1", None)]) as instr:
        instr.axis1.stop_velocity_mode()


def test_free_limit_switch():
    with expected_protocol(PS10_32,
                           [("EFREE1", None)]) as instr:
        instr.axis1.free_limit_switch()


def test_enable_motor():
    with expected_protocol(PS10_32,
                           [("MON1", None)]) as instr:
        instr.axis1.enable_motor()


def test_disable_motor():
    with expected_protocol(PS10_32,
                           [("MOFF1", None)]) as instr:
        instr.axis1.disable_motor()


def test_reset_position_counter():
    with expected_protocol(PS10_32,
                           [("CRES1", None)]) as instr:
        instr.axis1.reset_position_counter()


@pytest.mark.parametrize("mode", [0, 1, 2, 3, 4, 5, 6, 7])
def test_reference_move(mode):
    with expected_protocol(PS10_32,
                           [("REF1=%d" % mode, None)]) as instr:
        instr.axis1.reference_move(mode)


def test_reference_move_default():
    with expected_protocol(PS10_32,
                           [("REF1=4", None)]) as instr:
        instr.axis1.reference_move()


# ── is_moving ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("state,expected", [
    ("T", True),   # trapezoidal positioning
    ("V", True),   # velocity mode
    ("P", True),   # reference motion
    ("F", True),   # freeing limit switch
    ("H", True),   # phase initialisation
    ("S", True),   # S-curve positioning (PS 35 state, safe to check)
    ("R", False),  # ready (idle)
    ("O", False),  # disabled
    ("I", False),  # not initialised
    ("L", False),  # disabled after HW limit
    ("Z", False),  # disabled after timeout
])
def test_axis_is_moving(state, expected):
    with expected_protocol(PS10_32,
                           [("?ASTAT", state)]) as instr:
        assert instr.axis1.is_moving() is expected


def test_instrument_is_moving_true():
    with expected_protocol(PS10_32,
                           [("?ASTAT", "T")]) as instr:
        assert instr.is_moving() is True


def test_instrument_is_moving_false():
    with expected_protocol(PS10_32,
                           [("?ASTAT", "R")]) as instr:
        assert instr.is_moving() is False


# ── CANopen slave-ID prefix ────────────────────────────────────────────────────

def test_slave_id_prefixes_axis_command():
    """With slave_id=5, axis commands must be prefixed with '05'."""
    with expected_protocol(PS10_32,
                           [("05INIT1", None)],
                           slave_id=5) as instr:
        instr.axis1.initialize()


def test_slave_id_prefixes_instrument_command():
    with expected_protocol(PS10_32,
                           [("05ERRCLEAR", None)],
                           slave_id=5) as instr:
        instr.clear_errors()


def test_slave_id_prefixes_query():
    with expected_protocol(PS10_32,
                           [("05?PVEL1", "10000")],
                           slave_id=5) as instr:
        assert instr.axis1.max_velocity == 10000


def test_slave_id_two_digit_padding():
    with expected_protocol(PS10_32,
                           [("01STOP1", None)],
                           slave_id=1) as instr:
        instr.axis1.stop()
