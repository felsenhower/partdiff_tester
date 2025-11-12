"""Utility functions that are used by both `conftest.py` and `test_partdiff.py`."""

import os
import re
import subprocess
from collections.abc import Iterator
from enum import StrEnum
from functools import cache
from pathlib import Path

REFERENCE_IMPLEMENTATION_DIR = Path.cwd() / "reference_implementation"
REFERENCE_IMPLEMENTATION_EXEC = REFERENCE_IMPLEMENTATION_DIR / "partdiff"


class ReferenceSource(StrEnum):
    AUTO = "auto"
    CACHE = "cache"
    IMPL = "impl"


PartdiffParamsTuple = tuple[str, str, str, str, str, str]


RE_MATRIX_FLOAT = re.compile(r"[01]\.[0-9]{4}")

F = RE_MATRIX_FLOAT.pattern

RE_MATRIX = re.compile(
    rf"""
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_0 = re.compile(
    rf"""
    ^
    .*
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_1 = re.compile(
    rf"""
    ^
    .*
    ([0-9\.e+-]+)
    \s*
    .+:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_2 = re.compile(
    rf"""
    ^
    (.+): \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    (.+): \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    (.+): \s+ .+               \s*\n # Calculation method
    (.+): \s+ ([0-9]+)         \s*\n # Interlines
    (.+): \s+ .+               \s*\n # Pertubation function
    (.+): \s+ .+               \s*\n # Termination
    (.+): \s+ ([0-9]+)         \s*\n # Number of iterations       
    (.+): \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    .+:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_3 = re.compile(
    rf"""
    ^
    Berechnungszeit:     \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time (not captured!)
    Speicherbedarf:      \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage  (not captured!)
    Berechnungsmethode:  \s+ (.+)             \s*\n # Calculation method
    Interlines:          \s+ ([0-9]+)         \s*\n # Interlines
    Stoerfunktion:       \s+ (.+)             \s*\n # Pertubation function
    Terminierung:        \s+ (.+)             \s*\n # Termination
    Anzahl\sIterationen: \s+ ([0-9]+)         \s*\n # Number of iterations       
    Norm\sdes\sFehlers:  \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    Matrix:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_4 = re.compile(
    (
        # fmt: off
        r"^"
        r"Berechnungszeit:    [0-9]+\.[0-9]{6} s\n"
        r"Speicherbedarf:     [0-9]+\.[0-9]{6} MiB\n"
        r"Berechnungsmethode: (.+)\n"
        r"Interlines:         ([0-9]+)\n"
        r"Stoerfunktion:      (.+)\n"
        r"Terminierung:       (.+)\n"
        r"Anzahl Iterationen: ([0-9]+)\n"
        r"Norm des Fehlers:   ([0-9\.e+-]+)\n"
        r"\n"
        r"Matrix:\n"
        r"("
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        r")$"
        # fmt: on
    ),
    re.DOTALL,
)


OUTPUT_MASKS = [
    RE_OUTPUT_MASK_STRICT_0,
    RE_OUTPUT_MASK_STRICT_1,
    RE_OUTPUT_MASK_STRICT_2,
    RE_OUTPUT_MASK_STRICT_3,
    RE_OUTPUT_MASK_STRICT_4,
]

REFERENCE_OUTPUT_PATH = Path.cwd() / "reference_output"
TEST_CASES_FILE_PATH = Path.cwd() / "test_cases.txt"

RE_REF_OUTPUT_FILE = re.compile(
    r"""
    ^
    partdiff
    _(1)        # num (always 1)
    _([12])     # method (1..2)
    _([0-9]+)   # lines  (0..100000)
    _([12])     # func (1..2)
    _([12])     # term (1..2)
    _([0-9e-]+) # prec/iter (1e-4..1e-20 or 1..200000)
    \.txt
    $
""",
    re.VERBOSE | re.DOTALL,
)


def iter_reference_output_data() -> Iterator[tuple[PartdiffParamsTuple, str]]:
    """Iterate over the reference output data.

    Yields:
        Iterator[tuple[PartdiffParamsTuple, str]]: An iterator over the partdiff params and the corresponding output
            of the reference implementation.
    """
    assert REFERENCE_OUTPUT_PATH.is_dir()
    for p in REFERENCE_OUTPUT_PATH.iterdir():
        m = RE_REF_OUTPUT_FILE.match(p.name)
        assert m
        partdiff_params = m.groups()
        assert len(partdiff_params) == 6
        reference_output = p.read_text()
        yield (partdiff_params, reference_output)


def iter_test_cases() -> Iterator[PartdiffParamsTuple]:
    """Iterate over the test cases.

    Yields:
        Iterator[PartdiffParamsTuple]: An iterator over the partdiff params from the test cases.
    """
    with TEST_CASES_FILE_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fields = tuple(line.split())
            assert len(fields) == 6
            yield fields


@cache
def get_test_cases() -> list[PartdiffParamsTuple]:
    """Get the test cases as a list.

    Returns:
        list[PartdiffParamsTuple]: The test cases as a list of parameter tuples.
    """
    return list(iter_test_cases())


@cache
def get_reference_output_data_map() -> dict[PartdiffParamsTuple, str]:
    """Get the reference output as a dict.

    Returns:
        dict[PartdiffParamsTuple, str]: A dict mapping parameter combinations to the corresponding output.
    """
    return dict(iter_reference_output_data())


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
    partdiff_params: PartdiffParamsTuple,
    reference_output_data: dict[PartdiffParamsTuple, str],
    reference_source: ReferenceSource,
) -> str:
    """Acquire the reference output.

    Args:
        partdiff_params (PartdiffParamsTuple): The parameter combination to get the output for.
        reference_output_data (dict[PartdiffParamsTuple, str]): The cached reference output.
        reference_source (ReferenceSource): The source of the reference output (cache, impl, or auto).

    Raises:
        RuntimeError: When reference_source=cache and the output for a parameter combination isn't cached.

    Returns:
        str: The reference output for the params.
    """
    # Force the number of threads to 1:
    _num, method, lines, func, term, preciter = partdiff_params
    partdiff_params = ("1", method, lines, func, term, preciter)

    def get_from_cache():
        return reference_output_data[partdiff_params]

    def get_from_impl():
        command_line = [REFERENCE_IMPLEMENTATION_EXEC] + list(partdiff_params)
        return subprocess.check_output(command_line).decode("utf-8")

    assert reference_source in ReferenceSource

    match reference_source:
        case ReferenceSource.AUTO:
            if partdiff_params in reference_output_data:
                return get_from_cache()
            return get_from_impl()
        case ReferenceSource.CACHE:
            if partdiff_params not in reference_output_data:
                raise RuntimeError(
                    'Parameter combination "{}" was not found in cache'.format(
                        " ".join(partdiff_params)
                    )
                )
            return get_from_cache()
        case ReferenceSource.IMPL:
            return get_from_impl()
        case other:
            raise ValueError(f'Unexpected ReferenceSource "{other}"')


def get_actual_output(
    partdiff_params: PartdiffParamsTuple,
    partdiff_executable: list[str],
    use_valgrind: bool,
    cwd: Path | None,
) -> str:
    """Get the actual output for a parameter combination.

    Args:
        partdiff_params (PartdiffParamsTuple): The parameter combination.
        partdiff_executable (list[str]): The executable to run.
        use_valgrind (bool): Wether valgrind shall be used.
        cwd (Path | None): The working directory of the executable.

    Returns:
        str: The output of the executable.
    """
    command_line = partdiff_executable + list(partdiff_params)
    if use_valgrind:
        command_line = ["valgrind", "--leak-check=full"] + command_line
    return subprocess.check_output(command_line, cwd=cwd).decode("utf-8")


def check_executable_exists(executable: list[str], cwd: Path | None) -> None:
    """Check if the executable exists and can be executed by running it.

    The executable is allowed to return a non-zero exit status.

    Args:
        executable (list[str]): The executable to check
        cwd (Path | None): The working directory of the executable.
    """
    try:
        subprocess.check_output(executable, cwd=cwd)
    except subprocess.CalledProcessError:
        pass


def params_tuple_from_str(value: str) -> PartdiffParamsTuple:
    """Parse a PartdiffParamsTuple from a space-separated str

    Args:
        value (str): The str to parse

    Returns:
        PartdiffParamsTuple: The parsed tuple
    """
    l = value.split()
    assert len(l) == 6
    num, method, lines, func, term, preciter = l
    return (num, method, lines, func, term, preciter)
