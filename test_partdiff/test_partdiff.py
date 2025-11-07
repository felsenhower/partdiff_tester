import pytest
import subprocess
import re
import util


def test_partdiff_parametrized(
    partdiff_executable, reference_output_data, test_id, strictness
):
    partdiff_params, reference_output = reference_output_data[test_id]
    command_line = partdiff_executable + list(partdiff_params)
    actual_output = subprocess.check_output(command_line).decode("utf-8")
    re_output_mask = util.OUTPUT_MASKS[strictness]
    m_expected = re_output_mask.match(reference_output)
    assert m_expected is not None, (reference_output,)
    m_actual = re_output_mask.match(actual_output)
    assert m_actual is not None, (actual_output,)
    assert len(m_expected.groups()) == len(m_actual.groups())
    assert len(m_expected.groups()) > 0
    for capture_expected, capture_actual in zip(m_expected.groups(), m_actual.groups()):
        assert capture_expected == capture_actual
