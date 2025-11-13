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

OUTPUT_DIRECTORY='./reference_output'
TEST_CASES_FILE='./test_cases.txt'

mkdir -p "$OUTPUT_DIRECTORY"

cat "$TEST_CASES_FILE" | while read -r line ; do
    IFS=' ' read -r -a partdiff_params <<< "$line"
    echo "$PARTDIFF_EXEC" "${partdiff_params[@]}"
    output_filename="$(printf '%s/partdiff_%s_%s_%s_%s_%s_%s.txt\n' "$OUTPUT_DIRECTORY" "${partdiff_params[@]}")"
    "$PARTDIFF_EXEC" "${partdiff_params[@]}" > "$output_filename"
done
