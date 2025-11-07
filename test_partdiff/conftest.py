import pytest
import shlex
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


@pytest.fixture
def reference_output_data():
    return util.get_reference_output_data_map()


def pytest_generate_tests(metafunc):
    if "test_id" in metafunc.fixturenames:
        test_ids = util.get_reference_output_data_map().keys()
        metafunc.parametrize("test_id", test_ids)
