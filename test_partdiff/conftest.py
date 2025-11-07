import pytest
from pathlib import Path
import re
import shlex
from functools import cache
import util


def pytest_addoption(parser):
    parser.addoption("--executable", help="Path to partdiff executable.", required=True)
    parser.addoption(
        "--strictness",
        help="Strictness of the check.",
        type=int,
        default=0,
        choices=range(len(util.OUTPUT_MASKS)),
    )


@pytest.fixture
def partdiff_executable(request):
    value = request.config.getoption("--executable")
    return shlex.split(value)


@pytest.fixture
def strictness(request):
    return request.config.getoption("--strictness")


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


@pytest.fixture
def reference_output_data():
    return get_reference_output_data_map()


def pytest_generate_tests(metafunc):
    if "test_id" in metafunc.fixturenames:
        test_ids = get_reference_output_data_map().keys()
        metafunc.parametrize("test_id", test_ids)
