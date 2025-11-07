#/usr/bin/env bash

set -euo pipefail

PARTDIFF_EXEC=( "$@" )

param_num_range=(1)
param_method_range=(1 2)
param_lines_range=(0 1 10 100 1000)
param_func_range=(1 2)

function run_partdiff {
    num="$1"
    method="$2"
    lines="$3"
    func="$4"
    term="$5"
    preciter="$6"
    echo ${PARTDIFF_EXEC[@]} "$num" "$method" "$lines" "$func" "$term" "$preciter"
    set +e
    output="$(timeout 2 ${PARTDIFF_EXEC[@]} "$num" "$method" "$lines" "$func" "$term" "$preciter")"
    exit_code="$?"
    set -e
    success="$((exit_code == 0))"
    if (( success )) ; then
        output_filename="$(printf 'partdiff_%s_%s_%s_%s_%s_%s.txt\n' "$num" "$method" "$lines" "$func" "$term" "$preciter")"
        echo "$output" > "$output_filename"
    fi
    timed_out="$((exit_code == 125))"
    if ! (( timed_out )) ; then
        echo "$output"
        exit "$exit_code"
    fi
}

(
    param_term_range=(2)
    param_preciter_range=(1 10 100 1000 10000 100000)
    for num in ${param_num_range[@]} ; do
        for method in ${param_method_range[@]} ; do
            for lines in ${param_lines_range[@]} ; do
                for func in ${param_func_range[@]} ; do
                    for term in ${param_term_range[@]} ; do
                        for preciter in ${param_preciter_range[@]} ; do
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
    for num in ${param_num_range[@]} ; do
        for method in ${param_method_range[@]} ; do
            for lines in ${param_lines_range[@]} ; do
                for func in ${param_func_range[@]} ; do
                    for term in ${param_term_range[@]} ; do
                        for preciter in ${param_preciter_range[@]} ; do
                            run_partdiff "$num" "$method" "$lines" "$func" "$term" "$preciter"
                        done
                    done
                done
            done
        done
    done
)
