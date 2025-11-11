"""This file contains the actual test case (see `test_partdiff_parametrized`).

The test is parametrized by `pytest_generate_tests` in `conftest.py` via its `test_id` argument.
"""

import pytest

import util
from util import ReferenceSource, partdiff_params_tuple


def test_partdiff_parametrized(
    pytestconfig: pytest.Config,
    reference_output_data: dict[partdiff_params_tuple, str],
    test_id: str,
) -> None:
    """Test if the output of a partdiff implementation matches the output of the reference implementation.

    Args:
        pytestconfig (pytest.Config): See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytestconfig
        reference_output_data (dict[partdiff_params_tuple, str]): The cached reference output data
        test_id (str): The parameters to test as a space-separated string (not a tuple because a str prints better).
    """
    partdiff_params = tuple(test_id.split())
    assert len(partdiff_params) == 6

    partdiff_executable = pytestconfig.getoption("executable")
    strictness = pytestconfig.getoption("strictness")
    use_valgrind = pytestconfig.getoption("valgrind")
    reference_source = pytestconfig.getoption("reference_source")
    cwd = pytestconfig.getoption("cwd")

    actual_output = util.get_actual_output(
        partdiff_params, partdiff_executable, use_valgrind, cwd
    )
    reference_output = util.get_reference_output(
        partdiff_params, reference_output_data, reference_source
    )

    re_output_mask = util.OUTPUT_MASKS[strictness]

    m_expected = re_output_mask.match(reference_output)
    assert m_expected is not None, (reference_output,)

    m_actual = re_output_mask.match(actual_output)
    assert m_actual is not None, (actual_output,)

    assert len(m_expected.groups()) == len(m_actual.groups())
    assert len(m_expected.groups()) > 0

    for capture_expected, capture_actual in zip(m_expected.groups(), m_actual.groups()):
        assert capture_expected == capture_actual
