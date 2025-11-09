# partdiff_tester

This repository contains a testing script for `partdiff` based on `pytest`.

## Dependencies

- Python
- `pytest`

## Usage

Example usage:

```shell
$ uv run pytest --executable='/path/to/partdiff'
```

Or if you have `pytest` installed:

```shell
$ pytest --executable='/path/to/partdiff'
```

The following perform a soundness check by essentially testing the reference reference implementation against itself. 

```shell
$ uv run pytest --verbose --executable='reference_implementation/partdiff' --strictness=4 --valgrind
```

If this fails, the tests are not correct or do not match the reference implementation.

Currently, all tests are executed sequentially. On my machine, this takes about 20 seconds (without `--valgrind`). Use `--verbose` if you want to see what's going on.

The test contains some custom options:

```shell
$ uv run pytest --help | awk '/^Custom options for test_partdiff/{y=1}/^\[pytest\]/{y=0}y'
Custom options for test_partdiff:
  --executable=EXECUTABLE
                        Path to partdiff executable.
  --strictness={0,1,2,3,4}
                        Strictness of the check (default: 1)
  --valgrind            Use valgrind to execute the given executable.
  --max-num-tests=n     Only perform n tests (default: 0 == unlimited).
  --reference-source={auto,cache,impl}
                        Select the source of the reference output (cache == use
                        only cached output from disk; impl == always execute
                        reference implementation; auto (default) == try cache
                        and fall back to impl).
  --num-threads=n       Run the tests with n threads (default: 1). Comma-
                        separated lists and number ranges are supported (e.g.
                        "1-3,5-6").


```

The custom options are explained below.

### `executable`

Path to the partdiff executable.

Use `--executable=/path/to/partdiff` (not `--executable /path/to/partdiff`), because pytest's argparser is a bit dumb.

You can pass a space-separated list to do something like this:

```shell
$ uv run pytest --executable='mpirun /path/to/partdiff'
```

Quoting is supported, so this works:

```shell
$ uv run pytest --executable='"/path/to/your weird/partdiff"'
```

### `strictness`

Use `--strictness` to control which parts of the output are checked:

| Strictness level | What is checked? |
|-|-|
| 0 | Only the matrix |
| 1 | Matrix and residuum (right-hand-side) |
| 2 | Matrix, right-hand-side of {interlines, number of iterations, residuum} |
| 3 | Matrix, right-hand-side of {calculation method, interlines, pertubation function, number of iterations, residuum}, left-hand-side of {calculation time, memory usage, calculation method, interlines, pertubation function, number of iterations, residuum} |
| 4 | Full char-by-char diff (except for calculation time and memory usage) |

## `valgrind`

Start the executable with `valgrind --leak-check=full`.

This takes very long!

### `max-num-tests`

Limit the total number of tests to `n` (default: 0).

If `n=0`, all tests are performed.

### `reference_source`

Control which data source is used to obtain the reference output:

- `cache` ==> Load from `reference_output` only
- `impl` ==> Start partdiff in `reference_implementation` only
- `auto` (default) ==> Try to read from `reference_output` and fall back to reference impl, if data is not available

### `num-threads`

Run the tests with `n` threads (default: 1).

You can pass a comma-separated list that may also contain ranges, so this works: `1-4,8-16`.

The tests are repeated for all selected number of threads.

The test duplication happens after `max-num-tests` is applied, so `--max-num-tests=10 --num-threads=1-8` will run 80 tests.

Only the partdiff implementation given by `--executable=EXECUTABLE` is affected by this setting; for the reference output, a thread number of 1 is used.
So for example, when `--num-threads=8` is used, the console might show a test like
```
test_partdiff.py::test_partdiff_parametrized[8 1 0 2 2 1000]
```
Here, `EXECUTABLE` will be started with the parameters `8 1 0 2 2 1000`, but the reference output will be obtained by reading from `reference_output/partdiff_1_1_0_2_2_1000.txt` or by running `reference_implementation/partdiff 1 1 0 2 2 1000` (depending on the value of `--reference-source`).

> [!TIP]
> If you want to test a partdiff that was parallelized with MPI, you can do that by modifying `--executable`.
> This should work:
> ```shell
> for nprocs in {1..8} ; do
>   uv run pytest --executable="$(printf 'mpirun -n%d /path/to/partdiff' "$nprocs")"
> done
>  ```

### TODO: `filter`

Filter args, e.g. only `termination=1`.

### TODO: `cwd`

Set working directory
