#!/usr/bin/env python3

from pathlib import Path
import re

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
    .txt
    $
""",
    re.VERBOSE | re.DOTALL,
)


def iter_reference_output():
    assert REFERENCE_OUTPUT_PATH.is_dir()
    for p in REFERENCE_OUTPUT_PATH.iterdir():
        m = RE_REF_OUTPUT_FILE.match(p.name)
        assert m
        partdiff_params = m.groups()
        assert len(partdiff_params) == 6
        content = p.read_text()
        yield (partdiff_params, content)


def main() -> None:
    x = list(read_reference_output())
    print(x)


if __name__ == "__main__":
    main()
