import pytest
import shlex
import util
import re
import itertools


def shlex_list_str(value: str) -> list[str]:
    return shlex.split(value)


def reference_source_param(value: str) -> util.ReferenceSource:
    return util.ReferenceSource(value)


REGEX_NUM_LIST = re.compile(r"^(?:\d+(?:-\d+)?)(?:,\d+(?:-\d+)?)*$")


def num_list(value: str) -> list[int]:
    def is_sorted(l) -> bool:
        return all(l[i] <= l[i + 1] for i in range(len(l) - 1))

    def is_unique(l) -> bool:
        return len(set(l)) == len(l)

    if not REGEX_NUM_LIST.match(value):
        raise ValueError(f'Unable to parse number list "{value}"')
    result = []
    l = value.split(",")
    for x in l:
        if "-" in x:
            start, end = [int(s) for s in x.split("-")]
            result += list(range(start, end + 1))
        else:
            result.append(int(x))
    if not is_sorted(result) or not is_unique(result):
        raise ValueError(
            f'Number range "{value}" is not sorted or elements are not unique'
        )

    return result


def pytest_addoption(parser):
    custom_options = parser.getgroup("Custom options for test_partdiff")
    custom_options.addoption(
        "--executable",
        help="Path to partdiff executable.",
        required=True,
        type=shlex_list_str,
    )
    custom_options.addoption(
        "--strictness",
        help="Strictness of the check (default: 1)",
        type=int,
        default=1,
        choices=range(len(util.OUTPUT_MASKS)),
    )
    custom_options.addoption(
        "--valgrind",
        help="Use valgrind to execute the given executable.",
        action="store_true",
    )
    custom_options.addoption(
        "--max-num-tests",
        metavar="n",
        help="Only perform n tests (default: 0 == unlimited).",
        type=int,
        default=0,
    )
    custom_options.addoption(
        "--reference-source",
        help=(
            "Select the source of the reference output "
            "(cache == use only cached output from disk; "
            "impl == always execute reference implementation; "
            "auto (default) == try cache and fall back to impl)."
        ),
        type=reference_source_param,
        default=util.ReferenceSource.auto,
        choices=util.ReferenceSource,
    )
    custom_options.addoption(
        "--num-threads",
        metavar="n",
        help=(
            "Run the tests with n threads (default: 1). "
            'Comma-separated lists and number ranges are supported (e.g. "1-3,5-6").'
        ),
        type=num_list,
        default=[1],
    )


@pytest.fixture
def reference_output_data():
    return util.get_reference_output_data_map()


def pytest_generate_tests(metafunc):
    if "test_id" in metafunc.fixturenames:
        max_num_tests = metafunc.config.getoption("max_num_tests")
        num_threads_list = metafunc.config.getoption("num_threads")
        test_cases = util.get_test_cases()
        if max_num_tests:
            test_cases = test_cases[:max_num_tests]
        test_cases = [
            (str(num), method, lines, func, term, preciter)
            for (
                num,
                (_old_num, method, lines, func, term, preciter),
            ) in itertools.product(num_threads_list, test_cases)
        ]
        test_ids = [" ".join(test_case) for test_case in test_cases]
        metafunc.parametrize("test_id", test_ids)
