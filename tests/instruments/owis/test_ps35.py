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
from pymeasure.instruments.owis import PS35


# ── Initialisation ──────────────────────────────────────────────────────────

def test_init():
    with expected_protocol(PS35, []):
        pass


# ── Instrument-level: shared commands ────────────────────────────────────────

def test_version():
    with expected_protocol(PS35,
                           [("?VERSION", "PS35-V5.3-240512")]) as instr:
        assert instr.version == "PS35-V5.3-240512"


def test_serial_number():
    with expected_protocol(PS35,
                           [("?SERNUM", "09080145")]) as instr:
        assert instr.serial_number == "09080145"


def test_axis_state_three_axes():
    with expected_protocol(PS35,
                           [("?ASTAT", "RIT")]) as instr:
        assert instr.axis_state == "RIT"


def test_error_code():
    with expected_protocol(PS35,
                           [("?ERR", "1211")]) as instr:
        assert instr.error_code == 1211


@pytest.mark.parametrize("mode", [0, 1, 2])
def test_terminal_mode_setter(mode):
    with expected_protocol(PS35,
                           [("TERM=%d" % mode, None)]) as instr:
        instr.terminal_mode = mode


def test_clear_errors():
    with expected_protocol(PS35,
                           [("ERRCLEAR", None)]) as instr:
        instr.clear_errors()


def test_reset_board():
    with expected_protocol(PS35,
                           [("RESETMB", None)]) as instr:
        instr.reset_board()


def test_set_output():
    with expected_protocol(PS35,
                           [("OUTPUT2=1", None)]) as instr:
        instr.set_output(2, 1)


def test_get_analog_input():
    with expected_protocol(PS35,
                           [("?ANIN3", "234")]) as instr:
        assert instr.get_analog_input(3) == 234


# ── PS 35 specific: save/load parameters ─────────────────────────────────────

def test_save_parameters_all_axes():
    with expected_protocol(PS35,
                           [("SAVEGLOB", None),
                            ("SAVEAXPA1", None),
                            ("SAVEAXPA2", None),
                            ("SAVEAXPA3", None)]) as instr:
        instr.save_parameters()


def test_save_parameters_selected_axes():
    with expected_protocol(PS35,
                           [("SAVEGLOB", None),
                            ("SAVEAXPA2", None)]) as instr:
        instr.save_parameters(axes=[2])


def test_save_parameters_global_only():
    with expected_protocol(PS35,
                           [("SAVEGLOB", None)]) as instr:
        instr.save_parameters(axes=[])


def test_load_parameters_all_axes():
    with expected_protocol(PS35,
                           [("LOADGLOB", None),
                            ("LOADAXPA1", None),
                            ("LOADAXPA2", None),
                            ("LOADAXPA3", None)]) as instr:
        instr.load_parameters()


# ── PS 35 specific: joystick ─────────────────────────────────────────────────

def test_joystick_on():
    with expected_protocol(PS35,
                           [("JOYON", None)]) as instr:
        instr.joystick_on()


def test_joystick_off():
    with expected_protocol(PS35,
                           [("JOYOFF", None)]) as instr:
        instr.joystick_off()


# ── PS 35 specific: linear interpolation / output stage reset ────────────────

def test_start_linear_interpolation():
    with expected_protocol(PS35,
                           [("LIGO=011", None)]) as instr:
        instr.start_linear_interpolation("011")


def test_reset_output_stage():
    with expected_protocol(PS35,
                           [("RESETAC", None)]) as instr:
        instr.reset_output_stage()


# ── Axis channels: shared commands on all three axes ─────────────────────────

@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis2", 2), ("axis3", 3)
])
def test_initialize_all_axes(axis_name, n):
    with expected_protocol(PS35,
                           [("INIT%d" % n, None)]) as instr:
        getattr(instr, axis_name).initialize()


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis2", 2), ("axis3", 3)
])
def test_target_position_setter(axis_name, n):
    with expected_protocol(PS35,
                           [("PSET%d=100000" % n, None)]) as instr:
        getattr(instr, axis_name).target_position = 100000


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis2", 2), ("axis3", 3)
])
def test_max_velocity_setter(axis_name, n):
    with expected_protocol(PS35,
                           [("PVEL%d=10000" % n, None)]) as instr:
        getattr(instr, axis_name).max_velocity = 10000


@pytest.mark.parametrize("axis_name,n", [
    ("axis1", 1), ("axis2", 2), ("axis3", 3)
])
def test_stop_all_axes(axis_name, n):
    with expected_protocol(PS35,
                           [("STOP%d" % n, None)]) as instr:
        getattr(instr, axis_name).stop()


@pytest.mark.parametrize("axis_name,mode", [
    ("axis1", "ABSOL"), ("axis2", "RELAT"), ("axis3", "ABSOL")
])
def test_positioning_mode_setter(axis_name, mode):
    n = int(axis_name[-1])
    with expected_protocol(PS35,
                           [("%s%d" % (mode, n), None)]) as instr:
        getattr(instr, axis_name).positioning_mode = mode


def test_limit_switch_mask_axis2():
    with expected_protocol(PS35,
                           [("?SMK2", "1001")]) as instr:
        assert instr.axis2.limit_switch_mask == "1001"


def test_reference_move_axis3():
    with expected_protocol(PS35,
                           [("REF3=4", None)]) as instr:
        instr.axis3.reference_move()


# ── PS 35 specific axis commands ─────────────────────────────────────────────

def test_deceleration_getter():
    with expected_protocol(PS35,
                           [("?DACC2", "68")]) as instr:
        assert instr.axis2.deceleration == 68


def test_deceleration_setter():
    with expected_protocol(PS35,
                           [("DACC2=68", None)]) as instr:
        instr.axis2.deceleration = 68


def test_jerk_setter():
    with expected_protocol(PS35,
                           [("JACC3=5", None)]) as instr:
        instr.axis3.jerk = 5


def test_emergency_deceleration_setter():
    with expected_protocol(PS35,
                           [("EDACC1=1000", None)]) as instr:
        instr.axis1.emergency_deceleration = 1000


@pytest.mark.parametrize("profile", [0, 1])
def test_positioning_profile_setter(profile):
    with expected_protocol(PS35,
                           [("PMOD1=%d" % profile, None)]) as instr:
        instr.axis1.positioning_profile = profile


def test_inpos_mode_setter():
    with expected_protocol(PS35,
                           [("INPOSMOD1=1", None)]) as instr:
        instr.axis1.inpos_mode = 1


def test_inpos_window_setter():
    with expected_protocol(PS35,
                           [("INPOSWND1=50", None)]) as instr:
        instr.axis1.inpos_window = 50


def test_enabled_getter():
    with expected_protocol(PS35,
                           [("?AXIS3", "1")]) as instr:
        assert instr.axis3.enabled == 1


def test_encoder_lines_setter():
    with expected_protocol(PS35,
                           [("ENCLINES1=500", None)]) as instr:
        instr.axis1.encoder_lines = 500


def test_change_target():
    with expected_protocol(PS35,
                           [("PCHANGE2=50000", None)]) as instr:
        instr.axis2.change_target(50000)


# ── Commands inherited from OWISBase (common to all OWIS devices) ─────────────

@pytest.mark.parametrize("baud", [9600, 19200, 115200])
def test_baudrate_setter(baud):
    with expected_protocol(PS35,
                           [("BAUDRATE=%d" % baud, None)]) as instr:
        instr.baudrate = baud


def test_baudrate_getter():
    with expected_protocol(PS35,
                           [("?BAUDRATE", "9600")]) as instr:
        assert instr.baudrate == 9600


@pytest.mark.parametrize("end", [0, 1, 2])
def test_command_end_setter(end):
    with expected_protocol(PS35,
                           [("COMEND=%d" % end, None)]) as instr:
        instr.command_end = end


# ── Commands inherited from OWISAdvancedBase (PS 35 + PS 90+) ─────────────────

def test_motion_controller_version():
    with expected_protocol(PS35,
                           [("?MCTRVER", "MC1.0")]) as instr:
        assert instr.motion_controller_version == "MC1.0"


def test_program_checksum():
    with expected_protocol(PS35,
                           [("?PCHECK", "12227")]) as instr:
        assert instr.program_checksum == 12227


def test_joystick_zone_setter():
    with expected_protocol(PS35,
                           [("JZONE=25", None)]) as instr:
        instr.joystick_zone = 25


def test_joystick_center_x_setter():
    with expected_protocol(PS35,
                           [("JZEROX=505", None)]) as instr:
        instr.joystick_center_x = 505


def test_joystick_center_y_setter():
    with expected_protocol(PS35,
                           [("JZEROY=515", None)]) as instr:
        instr.joystick_center_y = 515


def test_joystick_center_z_setter():
    with expected_protocol(PS35,
                           [("JZEROZ=508", None)]) as instr:
        instr.joystick_center_z = 508


def test_joystick_button_setter():
    with expected_protocol(PS35,
                           [("JBUTTON=1", None)]) as instr:
        instr.joystick_button = 1


def test_joystick_plane_x_setter():
    with expected_protocol(PS35,
                           [("JPLAX=2", None)]) as instr:
        instr.joystick_plane_x = 2


def test_joystick_plane_y_setter():
    with expected_protocol(PS35,
                           [("JPLAY=3", None)]) as instr:
        instr.joystick_plane_y = 3


def test_joystick_plane_z_setter():
    with expected_protocol(PS35,
                           [("JPLAZ=1", None)]) as instr:
        instr.joystick_plane_z = 1


def test_ttl_inputs():
    with expected_protocol(PS35,
                           [("?INPTTL", "10100100")]) as instr:
        assert instr.ttl_inputs == "10100100"


def test_ttl_outputs():
    with expected_protocol(PS35,
                           [("?OUTTTL", "00101001")]) as instr:
        assert instr.ttl_outputs == "00101001"


def test_set_ttl_output():
    with expected_protocol(PS35,
                           [("OUTTTL2=1", None)]) as instr:
        instr.set_ttl_output(2, 1)


# ── Commands inherited from OWISAdvancedAxis (PS 35 + PS 90+) ─────────────────

def test_joystick_velocity_axis2():
    with expected_protocol(PS35,
                           [("JVEL2=1000", None)]) as instr:
        instr.axis2.joystick_velocity = 1000


def test_joystick_acceleration_getter():
    with expected_protocol(PS35,
                           [("?JOYACC3", "100")]) as instr:
        assert instr.axis3.joystick_acceleration == 100


def test_interpolation_velocity_setter():
    with expected_protocol(PS35,
                           [("IVEL1=50000", None)]) as instr:
        instr.axis1.interpolation_velocity = 50000


def test_interpolation_acceleration_setter():
    with expected_protocol(PS35,
                           [("IACC3=2000", None)]) as instr:
        instr.axis3.interpolation_acceleration = 2000


def test_measured_travel_axis1():
    with expected_protocol(PS35,
                           [("?MXSTROKE1", "340000")]) as instr:
        assert instr.axis1.measured_travel == 340000


def test_set_ttl_outputs_axis():
    with expected_protocol(PS35,
                           [("ETTLOUTS1=10", None)]) as instr:
        instr.axis1.set_ttl_outputs("10")


def test_clear_ttl_outputs_axis():
    with expected_protocol(PS35,
                           [("ETTLOUTC1=01", None)]) as instr:
        instr.axis1.clear_ttl_outputs("01")


def test_set_axis_output():
    with expected_protocol(PS35,
                           [("AXOUTPUT3=1", None)]) as instr:
        instr.axis3.set_axis_output(1)


# ── is_moving (per-axis) ──────────────────────────────────────────────────────

@pytest.mark.parametrize("full_state,axis_name,expected", [
    ("TIR", "axis1", True),   # axis1 moving
    ("TIR", "axis2", False),  # axis2 idle
    ("TIR", "axis3", False),  # axis3 ready
    ("RTV", "axis2", True),   # axis2 moving
    ("RRS", "axis3", True),   # axis3 S-curve
    ("RRR", "axis1", False),  # all ready
])
def test_axis_is_moving(full_state, axis_name, expected):
    with expected_protocol(PS35,
                           [("?ASTAT", full_state)]) as instr:
        assert getattr(instr, axis_name).is_moving() is expected


def test_instrument_is_moving_any_axis():
    """is_moving() returns True when any axis is moving."""
    with expected_protocol(PS35,
                           [("?ASTAT", "RTR")]) as instr:
        assert instr.is_moving() is True


def test_instrument_is_moving_all_idle():
    with expected_protocol(PS35,
                           [("?ASTAT", "RRR")]) as instr:
        assert instr.is_moving() is False
