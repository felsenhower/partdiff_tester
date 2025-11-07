import pytest
import shlex
import util


def shlex_list_str(value: str) -> list[str]:
    return shlex.split(value)


def pytest_addoption(parser):
    parser.addoption(
        "--executable",
        help="Path to partdiff executable.",
        required=True,
        type=shlex_list_str,
    )
    parser.addoption(
        "--strictness",
        help="Strictness of the check.",
        type=int,
        default=0,
        choices=range(len(util.OUTPUT_MASKS)),
    )
    parser.addoption(
        "--valgrind",
        help="Use valgrind to execute the given executable",
        action="store_true",
    )


@pytest.fixture
def reference_output_data():
    return util.get_reference_output_data_map()


def pytest_generate_tests(metafunc):
    if "test_id" in metafunc.fixturenames:
        test_ids = util.get_reference_output_data_map().keys()
        metafunc.parametrize("test_id", test_ids)
