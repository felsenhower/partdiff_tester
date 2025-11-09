import pytest
import subprocess
import re
import util


def get_reference_output(partdiff_params, reference_output_data):
    return reference_output_data[partdiff_params]


def get_actual_output(partdiff_params, partdiff_executable, use_valgrind):
    command_line = partdiff_executable + list(partdiff_params)
    if use_valgrind:
        command_line = ["valgrind", "--leak-check=full"] + command_line
    actual_output = subprocess.check_output(command_line).decode("utf-8")
    return actual_output


def test_partdiff_parametrized(pytestconfig, reference_output_data, test_id):
    partdiff_params = tuple(test_id.split())

    partdiff_executable = pytestconfig.getoption("executable")
    strictness = pytestconfig.getoption("strictness")
    use_valgrind = pytestconfig.getoption("valgrind")

    actual_output = get_actual_output(
        partdiff_params, partdiff_executable, use_valgrind
    )
    reference_output = get_reference_output(partdiff_params, reference_output_data)

    re_output_mask = util.OUTPUT_MASKS[strictness]

    m_expected = re_output_mask.match(reference_output)
    assert m_expected is not None, (reference_output,)

    m_actual = re_output_mask.match(actual_output)
    assert m_actual is not None, (actual_output,)

    assert len(m_expected.groups()) == len(m_actual.groups())
    assert len(m_expected.groups()) > 0

    for capture_expected, capture_actual in zip(m_expected.groups(), m_actual.groups()):
        assert capture_expected == capture_actual
