#!/usr/bin/env python3

import re
from functools import cache
from pathlib import Path

# Sample output for reference
"""
Berechnungszeit:    0.000004 s
Speicherbedarf:     0.000618 MiB
Berechnungsmethode: Gauß-Seidel
Interlines:         0
Stoerfunktion:      f(x,y) = 0
Terminierung:       Anzahl der Iterationen
Anzahl Iterationen: 47
Norm des Fehlers:   8.677282e-05

Matrix:
 1.0000 0.8750 0.7500 0.6250 0.5000 0.3750 0.2500 0.1250 0.0000
 0.8750 0.7811 0.6873 0.5935 0.4998 0.4060 0.3124 0.2187 0.1250
 0.7500 0.6873 0.6247 0.5621 0.4996 0.4371 0.3747 0.3124 0.2500
 0.6250 0.5935 0.5621 0.5307 0.4995 0.4683 0.4372 0.4061 0.3750
 0.5000 0.4998 0.4996 0.4995 0.4995 0.4996 0.4997 0.4998 0.5000
 0.3750 0.4060 0.4371 0.4683 0.4996 0.5309 0.5622 0.5936 0.6250
 0.2500 0.3124 0.3747 0.4372 0.4997 0.5622 0.6248 0.6874 0.7500
 0.1250 0.2187 0.3124 0.4061 0.4998 0.5936 0.6874 0.7812 0.8750
 0.0000 0.1250 0.2500 0.3750 0.5000 0.6250 0.7500 0.8750 1.0000
"""

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
    Matrix:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_2 = re.compile(
    rf"""
    ^
    (.+): \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time (not captured!)
    (.+): \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage  (not captured!)
    (.+): \s+ (.+)             \s*\n # Calculation method
    (.+): \s+ ([0-9]+)         \s*\n # Interlines
    (.+): \s+ (.+)             \s*\n # Pertubation function
    (.+): \s+ (.+)             \s*\n # Termination
    (.+): \s+ ([0-9]+)         \s*\n # Number of iterations       
    (.+): \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    Matrix:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

OUTPUT_MASKS = [
    RE_OUTPUT_MASK_STRICT_0,
    RE_OUTPUT_MASK_STRICT_1,
    RE_OUTPUT_MASK_STRICT_2,
]

REFERENCE_OUTPUT_PATH = Path.cwd() / ".." / "reference_output"

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


@cache
def get_reference_output_data_map():
    return {
        " ".join(partdiff_params): (partdiff_params, reference_output)
        for (partdiff_params, reference_output) in iter_reference_output_data()
    }
