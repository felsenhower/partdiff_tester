import pytest
import shlex
import util
import re
import itertools
import json


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


def partdiff_params_filter_regex(value: str) -> re.Pattern:
    def parse_json_sequence(value: str) -> re.Pattern:
        try:
            j = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise ValueError("Ivalid JSON.")
        if not isinstance(j, list):
            raise ValueError("Not a sequence.")
        if len(j) != 6:
            raise ValueError("Incorrect length.")
        for s in j:
            if not isinstance(s, str):
                raise ValueError("Sequence member not a str.")
        try:
            return re.compile(" ".join(j))
        except re.PatternError:
            raise ValueError("Incorrect regex in sequence.")

    def parse_json_object(value: str) -> re.Pattern:
        try:
            j = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise ValueError("Ivalid JSON.")
        if not isinstance(j, dict):
            raise ValueError("Not an object.")
        if len(j.keys()) != len(set(j.keys())):
            raise ValueError("Keys not unique.")
        for k, v in j.items():
            if not isinstance(k, str):
                raise ValueError("Object key not a str.")
            if not isinstance(v, str):
                raise ValueError("Object value not a str.")
        allowed_params = ("num", "method", "lines", "func", "term", "prec/iter")
        if not set(j.keys()).issubset(allowed_params):
            raise ValueError("Invalid params.")
        try:
            return re.compile(" ".join(j.get(p, r"\w+") for p in allowed_params))
        except re.PatternError:
            raise ValueError("Incorrect regex in object.")

    def parse_regex_str(value: str) -> re.Pattern:
        try:
            return re.compile(value)
        except re.PatternError:
            raise ValueError("Incorrect regex.")

    filter_variant = value[:2]
    value = value[2:]
    match filter_variant:
        case "r:":
            return parse_regex_str(value)
        case "o:":
            return parse_json_object(value)
        case "s:":
            return parse_json_sequence(value)
    raise ValueError(f'The filter "{value}" could not be parsed.')


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
    custom_options.addoption(
        "--filter",
        help=(
            re.sub(
                r"\s+",
                " ",
                r"""
            Filter the test configs with regex.
            You can pass a single regex with "r:"
            (e.g. 'r:\w+ 1 \w+ \w+ \w+ \w+'),
            a JSON-object with "o:"
            (e.g. 'o:{"method": "1"}'),
            or a JSON-sequence with "s:"
            (e.g. 's:["\\w+", "1", "\\w+", "\\w+", "\\w+", "\\w+"]').
            """,
            ).strip()
        ),
        action="append",
        type=partdiff_params_filter_regex,
        default=[],
    )


@pytest.fixture
def reference_output_data():
    return util.get_reference_output_data_map()


def pytest_generate_tests(metafunc):
    if "test_id" in metafunc.fixturenames:
        max_num_tests = metafunc.config.getoption("max_num_tests")
        num_threads_list = metafunc.config.getoption("num_threads")
        filter_regexes = metafunc.config.getoption("filter")
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
        test_ids = [
            test_id
            for test_id in test_ids
            if all(regex.match(test_id) for regex in filter_regexes)
        ]
        metafunc.parametrize("test_id", test_ids)
