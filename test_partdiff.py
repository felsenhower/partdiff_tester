"""This file contains the actual test case (see `test_partdiff_parametrized`).

The test is parametrized by `pytest_generate_tests` in `conftest.py` via its `test_id` argument.
"""

from pathlib import Path

import pytest

import util
from util import PartdiffParamsTuple, ReferenceSource, TermParam


def _test_partdiff_term_iter(
    reference_output_data: dict[PartdiffParamsTuple, str],
    partdiff_params: PartdiffParamsTuple,
    partdiff_executable: list[str],
    strictness: int,
    use_valgrind: bool,
    reference_source: ReferenceSource,
    cwd: Path | None,
):
    actual_output = util.get_actual_output(
        partdiff_params, partdiff_executable, use_valgrind, cwd
    )
    reference_output = util.get_reference_output(
        partdiff_params, reference_output_data, reference_source
    )
    re_output_mask = util.OUTPUT_MASKS[strictness]
    m_actual = re_output_mask.match(actual_output)
    assert m_actual is not None, (actual_output,)
    m_expected = re_output_mask.match(reference_output)
    assert m_expected is not None, (reference_output,)
    assert len(m_expected.groups()) == len(m_actual.groups())
    assert len(m_expected.groups()) > 0
    for capture_expected, capture_actual in zip(m_expected.groups(), m_actual.groups()):
        assert capture_expected == capture_actual


def _test_partdiff_term_prec(
    reference_output_data: dict[PartdiffParamsTuple, str],
    partdiff_params: PartdiffParamsTuple,
    partdiff_executable: list[str],
    strictness: int,
    use_valgrind: bool,
    reference_source: ReferenceSource,
    cwd: Path | None,
):
    actual_output = util.get_actual_output(
        partdiff_params, partdiff_executable, use_valgrind, cwd
    )
    reference_output = util.get_reference_output(
        partdiff_params, reference_output_data, reference_source
    )
    re_output_mask = util.OUTPUT_MASKS[strictness]
    m_actual = re_output_mask.match(actual_output)
    assert m_actual is not None, (actual_output,)
    m_expected = re_output_mask.match(reference_output)
    assert m_expected is not None, (reference_output,)
    assert len(m_expected.groups()) == len(m_actual.groups())
    assert len(m_expected.groups()) > 0
    for capture_expected, capture_actual in zip(m_expected.groups(), m_actual.groups()):
        assert capture_expected == capture_actual


def test_partdiff_parametrized(
    pytestconfig: pytest.Config,
    reference_output_data: dict[PartdiffParamsTuple, str],
    test_id: str,
) -> None:
    """Test if the output of a partdiff implementation matches the output of the reference implementation.

    Args:
        pytestconfig (pytest.Config): See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytestconfig
        reference_output_data (dict[PartdiffParamsTuple, str]): The cached reference output data
        test_id (str): The parameters to test as a space-separated string (not a tuple because a str prints better).
    """
    partdiff_params = util.params_tuple_from_str(test_id)
    partdiff_executable = pytestconfig.getoption("executable")
    strictness = pytestconfig.getoption("strictness")
    use_valgrind = pytestconfig.getoption("valgrind")
    reference_source = pytestconfig.getoption("reference_source")
    cwd = pytestconfig.getoption("cwd")
    match util.PartdiffParamsClass.from_tuple(partdiff_params).term:
        case TermParam.PREC:
            _test_partdiff_term_prec(
                reference_output_data,
                partdiff_params,
                partdiff_executable,
                strictness,
                use_valgrind,
                reference_source,
                cwd,
            )
        case TermParam.ITER:
            _test_partdiff_term_iter(
                reference_output_data,
                partdiff_params,
                partdiff_executable,
                strictness,
                use_valgrind,
                reference_source,
                cwd,
            )
        case other:
            raise ValueError(f'Unexpected termination condition "{other}"')
