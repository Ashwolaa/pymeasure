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
from pymeasure.instruments.owis import PS90Plus


# ── Initialisation ──────────────────────────────────────────────────────────

def test_init():
    with expected_protocol(PS90Plus, []):
        pass


# ── Instrument-level: shared commands (OWISBase) ─────────────────────────────

def test_version():
    with expected_protocol(PS90Plus,
                           [("?VERSION", "PS90-V8.0-20231001")]) as instr:
        assert instr.version == "PS90-V8.0-20231001"


def test_serial_number():
    with expected_protocol(PS90Plus,
                           [("?SERNUM", "09080145")]) as instr:
        assert instr.serial_number == "09080145"


def test_axis_state_nine_axes():
    with expected_protocol(PS90Plus,
                           [("?ASTAT", "IIOURTTJV")]) as instr:
        assert instr.axis_state == "IIOURTTJV"


def test_error_code():
    with expected_protocol(PS90Plus,
                           [("?ERR", "1211")]) as instr:
        assert instr.error_code == 1211


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_terminal_mode_setter(mode):
    with expected_protocol(PS90Plus,
                           [("TERM=%d" % mode, None)]) as instr:
        instr.terminal_mode = mode


def test_clear_errors():
    with expected_protocol(PS90Plus,
                           [("ERRCLEAR", None)]) as instr:
        instr.clear_errors()


def test_reset_board():
    with expected_protocol(PS90Plus,
                           [("RESETMB", None)]) as instr:
        instr.reset_board()


def test_set_output():
    with expected_protocol(PS90Plus,
                           [("OUTPUT3=1", None)]) as instr:
        instr.set_output(3, 1)


def test_get_analog_input():
    with expected_protocol(PS90Plus,
                           [("?ANIN5", "512")]) as instr:
        assert instr.get_analog_input(5) == 512


def test_set_pwm_output():
    with expected_protocol(PS90Plus,
                           [("OPWM2=75", None)]) as instr:
        instr.set_pwm_output(2, 75)


def test_get_pwm_output():
    with expected_protocol(PS90Plus,
                           [("?OPWM2", "75")]) as instr:
        assert instr.get_pwm_output(2) == 75


# ── PS 90+ specific: configuration ───────────────────────────────────────────

@pytest.mark.parametrize("baud", [9600, 19200, 57600, 115200])
def test_baudrate_setter(baud):
    with expected_protocol(PS90Plus,
                           [("BAUDRATE=%d" % baud, None)]) as instr:
        instr.baudrate = baud


def test_baudrate_getter():
    with expected_protocol(PS90Plus,
                           [("?BAUDRATE", "9600")]) as instr:
        assert instr.baudrate == 9600


@pytest.mark.parametrize("end", [0, 1, 2])
def test_command_end_setter(end):
    with expected_protocol(PS90Plus,
                           [("COMEND=%d" % end, None)]) as instr:
        instr.command_end = end


def test_program_checksum():
    with expected_protocol(PS90Plus,
                           [("?PCHECK", "12227")]) as instr:
        assert instr.program_checksum == 12227


# ── PS 90+ specific: joystick instrument-level ───────────────────────────────

def test_joystick_zone_setter():
    with expected_protocol(PS90Plus,
                           [("JZONE=25", None)]) as instr:
        instr.joystick_zone = 25


def test_joystick_center_x_setter():
    with expected_protocol(PS90Plus,
                           [("JZEROX=505", None)]) as instr:
        instr.joystick_center_x = 505


def test_joystick_center_y_setter():
    with expected_protocol(PS90Plus,
                           [("JZEROY=515", None)]) as instr:
        instr.joystick_center_y = 515


def test_joystick_center_z_setter():
    with expected_protocol(PS90Plus,
                           [("JZEROZ=508", None)]) as instr:
        instr.joystick_center_z = 508


def test_joystick_button_setter():
    with expected_protocol(PS90Plus,
                           [("JBUTTON=1", None)]) as instr:
        instr.joystick_button = 1


def test_joystick_plane_x_setter():
    with expected_protocol(PS90Plus,
                           [("JPLAX=2", None)]) as instr:
        instr.joystick_plane_x = 2


def test_joystick_plane_y_setter():
    with expected_protocol(PS90Plus,
                           [("JPLAY=3", None)]) as instr:
        instr.joystick_plane_y = 3


def test_joystick_plane_z_setter():
    with expected_protocol(PS90Plus,
                           [("JPLAZ=1", None)]) as instr:
        instr.joystick_plane_z = 1


def test_joystick_on():
    with expected_protocol(PS90Plus,
                           [("JOYON", None)]) as instr:
        instr.joystick_on()


def test_joystick_off():
    with expected_protocol(PS90Plus,
                           [("JOYOFF", None)]) as instr:
        instr.joystick_off()


# ── PS 90+ specific: I/O ─────────────────────────────────────────────────────

def test_ttl_inputs():
    with expected_protocol(PS90Plus,
                           [("?INPTTL", "10100100")]) as instr:
        assert instr.ttl_inputs == "10100100"


def test_sps_inputs():
    with expected_protocol(PS90Plus,
                           [("?INPSPS", "00110011")]) as instr:
        assert instr.sps_inputs == "00110011"


def test_ttl_outputs():
    with expected_protocol(PS90Plus,
                           [("?OUTTTL", "00101001")]) as instr:
        assert instr.ttl_outputs == "00101001"


def test_sps_outputs():
    with expected_protocol(PS90Plus,
                           [("?OUTSPS", "00101001")]) as instr:
        assert instr.sps_outputs == "00101001"


@pytest.mark.parametrize("mode", [0, 1])
def test_input_mode_setter(mode):
    with expected_protocol(PS90Plus,
                           [("INMODE=%d" % mode, None)]) as instr:
        instr.input_mode = mode


def test_io_config():
    with expected_protocol(PS90Plus,
                           [("?IOCONFIG", "15")]) as instr:
        assert instr.io_config == 15


def test_set_ttl_output():
    with expected_protocol(PS90Plus,
                           [("OUTTTL3=1", None)]) as instr:
        instr.set_ttl_output(3, 1)


def test_set_sps_output():
    with expected_protocol(PS90Plus,
                           [("OUTSPS2=0", None)]) as instr:
        instr.set_sps_output(2, 0)


def test_get_analog_output():
    with expected_protocol(PS90Plus,
                           [("?DAOUT2", "250")]) as instr:
        assert instr.get_analog_output(2) == 250


def test_set_analog_output():
    with expected_protocol(PS90Plus,
                           [("DAOUT2=250", None)]) as instr:
        instr.set_analog_output(2, 250)


# ── PS 90+ specific: save/load parameters ────────────────────────────────────

def test_save_parameters_all_axes():
    with expected_protocol(PS90Plus,
                           [("SAVEGLOB", None),
                            ("SAVEAXPA1", None),
                            ("SAVEAXPA2", None),
                            ("SAVEAXPA3", None),
                            ("SAVEAXPA4", None),
                            ("SAVEAXPA5", None),
                            ("SAVEAXPA6", None),
                            ("SAVEAXPA7", None),
                            ("SAVEAXPA8", None),
                            ("SAVEAXPA9", None)]) as instr:
        instr.save_parameters()


def test_save_parameters_selected_axes():
    with expected_protocol(PS90Plus,
                           [("SAVEGLOB", None),
                            ("SAVEAXPA3", None),
                            ("SAVEAXPA5", None)]) as instr:
        instr.save_parameters(axes=[3, 5])


def test_save_parameters_global_only():
    with expected_protocol(PS90Plus,
                           [("SAVEGLOB", None)]) as instr:
        instr.save_parameters(axes=[])


def test_load_parameters_all_axes():
    with expected_protocol(PS90Plus,
                           [("LOADGLOB", None),
                            ("LOADAXPA1", None),
                            ("LOADAXPA2", None),
                            ("LOADAXPA3", None),
                            ("LOADAXPA4", None),
                            ("LOADAXPA5", None),
                            ("LOADAXPA6", None),
                            ("LOADAXPA7", None),
                            ("LOADAXPA8", None),
                            ("LOADAXPA9", None)]) as instr:
        instr.load_parameters()


# ── PS 90+ specific: linear interpolation and multi-axis commands ─────────────

def test_start_linear_interpolation():
    with expected_protocol(PS90Plus,
                           [("LIGO=000000111", None)]) as instr:
        instr.start_linear_interpolation("000000111")


def test_multi_axis_start_positioning():
    with expected_protocol(PS90Plus,
                           [("MPGO=000000011", None)]) as instr:
        instr.multi_axis_start_positioning("000000011")


def test_multi_axis_start_velocity():
    with expected_protocol(PS90Plus,
                           [("MVGO=000000011", None)]) as instr:
        instr.multi_axis_start_velocity("000000011")


def test_multi_axis_stop():
    with expected_protocol(PS90Plus,
                           [("MSTOP=000000111", None)]) as instr:
        instr.multi_axis_stop("000000111")


# ── Axis channels: shared commands on all nine axes ───────────────────────────

@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis5", 5), ("axis9", 9)
])
def test_initialize_axes(axis_name, n):
    with expected_protocol(PS90Plus,
                           [("INIT%d" % n, None)]) as instr:
        getattr(instr, axis_name).initialize()


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis5", 5), ("axis9", 9)
])
def test_target_position_setter(axis_name, n):
    with expected_protocol(PS90Plus,
                           [("PSET%d=100000" % n, None)]) as instr:
        getattr(instr, axis_name).target_position = 100000


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis5", 5), ("axis9", 9)
])
def test_max_velocity_setter(axis_name, n):
    with expected_protocol(PS90Plus,
                           [("PVEL%d=10000" % n, None)]) as instr:
        getattr(instr, axis_name).max_velocity = 10000


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis5", 5), ("axis9", 9)
])
def test_stop_axes(axis_name, n):
    with expected_protocol(PS90Plus,
                           [("STOP%d" % n, None)]) as instr:
        getattr(instr, axis_name).stop()


@pytest.mark.parametrize("axis_name,mode", [
    ("axis1", "ABSOL"), ("axis3", "RELAT"), ("axis9", "ABSOL")
])
def test_positioning_mode_setter(axis_name, mode):
    n = int(axis_name[-1])
    with expected_protocol(PS90Plus,
                           [("%s%d" % (mode, n), None)]) as instr:
        getattr(instr, axis_name).positioning_mode = mode


def test_limit_switch_mask_axis5():
    with expected_protocol(PS90Plus,
                           [("?SMK5", "1001")]) as instr:
        assert instr.axis5.limit_switch_mask == "1001"


def test_reference_move_axis9():
    with expected_protocol(PS90Plus,
                           [("REF9=4", None)]) as instr:
        instr.axis9.reference_move()


# ── PS 90+ specific axis commands ────────────────────────────────────────────

@pytest.mark.parametrize("motor_type", [0, 2, 3, 4])
def test_motor_type_setter(motor_type):
    with expected_protocol(PS90Plus,
                           [("MOTYPE1=%d" % motor_type, None)]) as instr:
        instr.axis1.motor_type = motor_type


def test_deceleration_getter():
    with expected_protocol(PS90Plus,
                           [("?DACC3", "68")]) as instr:
        assert instr.axis3.deceleration == 68


def test_deceleration_setter():
    with expected_protocol(PS90Plus,
                           [("DACC3=68", None)]) as instr:
        instr.axis3.deceleration = 68


def test_jerk_setter():
    with expected_protocol(PS90Plus,
                           [("JACC9=5", None)]) as instr:
        instr.axis9.jerk = 5


def test_emergency_deceleration_setter():
    with expected_protocol(PS90Plus,
                           [("EDACC1=1000", None)]) as instr:
        instr.axis1.emergency_deceleration = 1000


@pytest.mark.parametrize("profile", [0, 1])
def test_positioning_profile_setter(profile):
    with expected_protocol(PS90Plus,
                           [("PMOD2=%d" % profile, None)]) as instr:
        instr.axis2.positioning_profile = profile


def test_inpos_mode_setter():
    with expected_protocol(PS90Plus,
                           [("INPOSMOD5=1", None)]) as instr:
        instr.axis5.inpos_mode = 1


def test_inpos_window_setter():
    with expected_protocol(PS90Plus,
                           [("INPOSWND5=50", None)]) as instr:
        instr.axis5.inpos_window = 50


def test_enabled_getter():
    with expected_protocol(PS90Plus,
                           [("?AXIS7", "1")]) as instr:
        assert instr.axis7.enabled == 1


def test_encoder_lines_setter():
    with expected_protocol(PS90Plus,
                           [("ENCLINES1=500", None)]) as instr:
        instr.axis1.encoder_lines = 500


@pytest.mark.parametrize("mode", [0, 1])
def test_bldc_commutation_setter(mode):
    with expected_protocol(PS90Plus,
                           [("BLDCCT4=%d" % mode, None)]) as instr:
        instr.axis4.bldc_commutation = mode


def test_joystick_velocity_setter():
    with expected_protocol(PS90Plus,
                           [("JVEL3=1000", None)]) as instr:
        instr.axis3.joystick_velocity = 1000


def test_joystick_acceleration_getter():
    with expected_protocol(PS90Plus,
                           [("?JOYACC3", "100")]) as instr:
        assert instr.axis3.joystick_acceleration == 100


def test_joystick_auto_off_setter():
    with expected_protocol(PS90Plus,
                           [("JAUTOMOFF1=0", None)]) as instr:
        instr.axis1.joystick_auto_off = 0


def test_interpolation_velocity_setter():
    with expected_protocol(PS90Plus,
                           [("IVEL1=50000", None)]) as instr:
        instr.axis1.interpolation_velocity = 50000


def test_interpolation_acceleration_setter():
    with expected_protocol(PS90Plus,
                           [("IACC3=2000", None)]) as instr:
        instr.axis3.interpolation_acceleration = 2000


def test_change_target():
    with expected_protocol(PS90Plus,
                           [("PCHANGE6=75000", None)]) as instr:
        instr.axis6.change_target(75000)


def test_set_ttl_outputs_axis():
    with expected_protocol(PS90Plus,
                           [("ETTLOUTS2=10", None)]) as instr:
        instr.axis2.set_ttl_outputs("10")


def test_clear_ttl_outputs_axis():
    with expected_protocol(PS90Plus,
                           [("ETTLOUTC2=01", None)]) as instr:
        instr.axis2.clear_ttl_outputs("01")


def test_set_axis_output():
    with expected_protocol(PS90Plus,
                           [("AXOUTPUT5=1", None)]) as instr:
        instr.axis5.set_axis_output(1)


# ── is_moving (per-axis and instrument-level) ─────────────────────────────────

@pytest.mark.parametrize("full_state,axis_name,expected", [
    # Base states
    ("TRRRRRRRI", "axis1", True),   # axis1 trapezoidal
    ("TRRRRRRRI", "axis2", False),  # axis2 ready
    ("RRVRRRRRI", "axis3", True),   # axis3 velocity mode
    ("RRRRRPRRR", "axis6", True),   # axis6 reference motion
    # PS 90+-specific states
    ("RJRRRRRRR", "axis2", True),   # axis2 joystick mode
    ("WWWWWWWWW", "axis5", True),   # axis5 trapezoidal+WMS
    ("RRRXRRRRR", "axis4", True),   # axis4 S-curve+WMS
    ("RRRRYRRRR", "axis5", True),   # axis5 velocity+WMS
    ("RRRRRCRRRR"[:9], "axis6", True),  # axis6 CNC velocity
    ("RNRRRRRRR", "axis2", True),   # axis2 piezo follow-up
    # Non-moving states
    ("RLRRRRRRR", "axis2", False),  # axis2 limit-switch disabled
    ("BRRRRRRR", "axis1", False),   # axis1 brake-switch stopped - only 8 chars
    ("RRRRRRRRR", "axis9", False),  # axis9 ready
])
def test_axis_is_moving(full_state, axis_name, expected):
    with expected_protocol(PS90Plus,
                           [("?ASTAT", full_state)]) as instr:
        assert getattr(instr, axis_name).is_moving() is expected


def test_instrument_is_moving_joystick():
    """is_moving() recognises joystick mode (PS 90+-specific state 'J')."""
    with expected_protocol(PS90Plus,
                           [("?ASTAT", "RJRRRRRRR")]) as instr:
        assert instr.is_moving() is True


def test_instrument_is_moving_wms():
    """is_moving() recognises WMS-assisted modes (W, X, Y, C, N)."""
    with expected_protocol(PS90Plus,
                           [("?ASTAT", "RRRRWRRRR")]) as instr:
        assert instr.is_moving() is True


def test_instrument_is_moving_all_ready():
    with expected_protocol(PS90Plus,
                           [("?ASTAT", "RRRRRRRRR")]) as instr:
        assert instr.is_moving() is False


def test_instrument_is_moving_all_idle():
    with expected_protocol(PS90Plus,
                           [("?ASTAT", "IIIIIIIII")]) as instr:
        assert instr.is_moving() is False
