"""This file contains the actual test case (see `test_partdiff_parametrized`).

The test is parametrized by `pytest_generate_tests` in `conftest.py` via its `test_id` argument.
"""

import os
import subprocess
from pathlib import Path

import pytest

import util
from util import ReferenceSource, partdiff_params_tuple

REFERENCE_IMPLEMENTATION_DIR = Path.cwd() / "reference_implementation"
REFERENCE_IMPLEMENTATION_EXEC = REFERENCE_IMPLEMENTATION_DIR / "partdiff"


def ensure_reference_implementation_exists() -> None:
    """Ensure that the reference implementation exists.

    If it doesn't exist, `make` is used to automatically compile it.
    """

    def is_executable():
        executable = REFERENCE_IMPLEMENTATION_EXEC
        return executable.exists() and os.access(executable, os.X_OK)

    if is_executable():
        return
    subprocess.check_output(["make", "-C", REFERENCE_IMPLEMENTATION_DIR])
    assert is_executable()


def get_reference_output(
    partdiff_params: partdiff_params_tuple,
    reference_output_data: dict[partdiff_params_tuple, str],
    reference_source: ReferenceSource,
) -> str:
    """Acquire the reference output.

    Args:
        partdiff_params (partdiff_params_tuple): The parameter combination to get the output for.
        reference_output_data (dict[partdiff_params_tuple, str]): The cached reference output.
        reference_source (ReferenceSource): The source of the reference output (cache, impl, or auto).

    Raises:
        RuntimeError: When reference_source=cache and the output for a parameter combination isn't cached.

    Returns:
        str: The reference output for the params.
    """
    # Force the number of threads to 1:
    partdiff_params = ("1",) + partdiff_params[1:6]

    def get_from_cache():
        return reference_output_data[partdiff_params]

    def get_from_impl():
        ensure_reference_implementation_exists()
        command_line = [REFERENCE_IMPLEMENTATION_EXEC] + list(partdiff_params)
        return subprocess.check_output(command_line).decode("utf-8")

    assert reference_source in ReferenceSource

    match reference_source:
        case ReferenceSource.auto:
            if partdiff_params in reference_output_data:
                return get_from_cache()
            return get_from_impl()
        case ReferenceSource.cache:
            if partdiff_params not in reference_output_data:
                raise RuntimeError(
                    'Parameter combination "{}" was not found in cache'.format(
                        " ".join(partdiff_params)
                    )
                )
            return get_from_cache()
        case ReferenceSource.impl:
            return get_from_impl()


def get_actual_output(
    partdiff_params: partdiff_params_tuple,
    partdiff_executable: list[str],
    use_valgrind: bool,
) -> str:
    """Get the actual output for a parameter combination.

    Args:
        partdiff_params (partdiff_params_tuple): The parameter combination.
        partdiff_executable (list[str]): The executable to run.
        use_valgrind (bool): Wether valgrind shall be used.

    Returns:
        str: The output of the executable.
    """
    command_line = partdiff_executable + list(partdiff_params)
    if use_valgrind:
        command_line = ["valgrind", "--leak-check=full"] + command_line
    return subprocess.check_output(command_line).decode("utf-8")


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

    actual_output = get_actual_output(
        partdiff_params, partdiff_executable, use_valgrind
    )
    reference_output = get_reference_output(
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
