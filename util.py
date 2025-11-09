#!/usr/bin/env python3

import re
from functools import cache
from pathlib import Path

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


def iter_reference_output_data():
    assert REFERENCE_OUTPUT_PATH.is_dir()
    for p in REFERENCE_OUTPUT_PATH.iterdir():
        m = RE_REF_OUTPUT_FILE.match(p.name)
        assert m
        partdiff_params = m.groups()
        assert len(partdiff_params) == 6
        reference_output = p.read_text()
        yield (partdiff_params, reference_output)


def iter_test_cases():
    with TEST_CASES_FILE_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fields = line.split()
            assert len(fields) == 6
            yield tuple(fields)


@cache
def get_test_cases():
    return list(iter_test_cases())


@cache
def get_reference_output_data_map():
    return {
        " ".join(partdiff_params): (partdiff_params, reference_output)
        for (partdiff_params, reference_output) in iter_reference_output_data()
    }
