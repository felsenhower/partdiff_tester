#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

[ "${SHELLCHECK:-0}" == "1" ] && shellcheck "$0"

PARTDIFF_EXEC='reference_implementation/partdiff'

if ! [[ -x "$PARTDIFF_EXEC" ]] ; then
    printf 'Error: partdiff executable "%s" does not exist or is not executable.\n' "$PARTDIFF_EXEC"
    echo 'Maybe you need to build it first?'
    echo '$ make -C reference_implementation'
    exit 1
fi

TIMEOUT_DURATION=2
OUTPUT_DIRECTORY='./reference_output'
TEST_CASES_FILE='./test_cases.txt'

PARAM_NUM_RANGE=(1)
PARAM_METHOD_RANGE=(1 2)
PARAM_LINES_RANGE=(0 1 10 100 1000)
PARAM_FUNC_RANGE=(1 2)

function run_partdiff {
    num="$1"
    method="$2"
    lines="$3"
    func="$4"
    term="$5"
    preciter="$6"
    echo -n "$PARTDIFF_EXEC" "$num" "$method" "$lines" "$func" "$term" "$preciter"
    set +e
    output="$(timeout "$TIMEOUT_DURATION" "$PARTDIFF_EXEC" "$num" "$method" "$lines" "$func" "$term" "$preciter")"
    exit_code="$?"
    set -e
    success="$((exit_code == 0))"
    if (( success )) ; then
        output_filename="$(printf '%s/partdiff_%s_%s_%s_%s_%s_%s.txt\n' "$OUTPUT_DIRECTORY" "$num" "$method" "$lines" "$func" "$term" "$preciter")"
        echo "$output" > "$output_filename"
        echo '  (OK)'
        echo "$num" "$method" "$lines" "$func" "$term" "$preciter" >> "$TEST_CASES_FILE"
        return
    fi
    timed_out="$((exit_code == 124))"
    if (( timed_out )) ; then
        echo '  (TIMED OUT)'
        return
    fi
    echo "$output"
    exit "$exit_code"
}

mkdir -p "$OUTPUT_DIRECTORY"
true > "$TEST_CASES_FILE"

(
    param_term_range=(2)
    param_preciter_range=(1 10 100 1000 10000 100000)
    for num in "${PARAM_NUM_RANGE[@]}" ; do
        for method in "${PARAM_METHOD_RANGE[@]}" ; do
            for lines in "${PARAM_LINES_RANGE[@]}" ; do
                for func in "${PARAM_FUNC_RANGE[@]}" ; do
                    for term in "${param_term_range[@]}" ; do
                        for preciter in "${param_preciter_range[@]}" ; do
                            run_partdiff "$num" "$method" "$lines" "$func" "$term" "$preciter"
                        done
                    done
                done
            done
        done
    done
)

(
    param_term_range=(1)
    param_preciter_range=('1e-4' '1e-8' '1e-12' '1e-16' '1e-20')
    for num in "${PARAM_NUM_RANGE[@]}" ; do
        for method in "${PARAM_METHOD_RANGE[@]}" ; do
            for lines in "${PARAM_LINES_RANGE[@]}" ; do
                for func in "${PARAM_FUNC_RANGE[@]}" ; do
                    for term in "${param_term_range[@]}" ; do
                        for preciter in "${param_preciter_range[@]}" ; do
                            run_partdiff "$num" "$method" "$lines" "$func" "$term" "$preciter"
                        done
                    done
                done
            done
        done
    done
)
