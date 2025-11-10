import pytest
import subprocess
import re
import util
from pathlib import Path
import os
from util import ReferenceSource, partdiff_params_tuple

REFERENCE_IMPLEMENTATION_DIR = Path.cwd() / "reference_implementation"
REFERENCE_IMPLEMENTATION_EXEC = REFERENCE_IMPLEMENTATION_DIR / "partdiff"


def ensure_reference_implementation_exists() -> None:
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
    # Force the number of threads to 1:
    partdiff_params = ("1",) + partdiff_params[1:6]

    def get_from_cache():
        return reference_output_data[partdiff_params]

    def get_from_impl():
        ensure_reference_implementation_exists()
        command_line = [REFERENCE_IMPLEMENTATION_EXEC] + list(partdiff_params)
        return subprocess.check_output(command_line).decode("utf-8")

    match reference_source:
        case ReferenceSource.auto:
            if partdiff_params in reference_output_data:
                return get_from_cache()
            return get_from_impl()
        case ReferenceSource.cache:
            if not partdiff_params in reference_output_data:
                raise RuntimeError(
                    'Parameter combination "{}" was not found in cache'.format(
                        " ".join(partdiff_params)
                    )
                )
            return get_from_cache()
        case ReferenceSource.impl:
            return get_from_impl()
        case _:
            raise ValueError(
                f'Encountered unexepected reference source "{reference_source}"'
            )


def get_actual_output(
    partdiff_params: partdiff_params_tuple,
    partdiff_executable: list[str],
    use_valgrind: bool,
) -> str:
    command_line = partdiff_executable + list(partdiff_params)
    if use_valgrind:
        command_line = ["valgrind", "--leak-check=full"] + command_line
    return subprocess.check_output(command_line).decode("utf-8")


def test_partdiff_parametrized(
    pytestconfig: pytest.Config,
    reference_output_data: dict[partdiff_params_tuple, str],
    test_id: str,
) -> None:
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
