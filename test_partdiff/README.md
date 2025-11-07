# partdiff-tester

This directory contains a testing script for `partdiff` based on `pytest`.

## Dependencies

- Python
- `pytest`

## Usage

Example usage:

```shell
$ pytest --executable='/path/to/partdiff'
```

Currently, all tests are executed sequentially. On my machine, this takes about 20 seconds. Use `--verbose` if you want to see what's going on.

The test contains some custom options. Here is an excerpt from `pytest --help`:

```
Custom options:
  --executable=EXECUTABLE
                        Path to partdiff executable.
  --strictness={0,1,2,3,4}
                        Strictness of the check.
  --valgrind            Use valgrind to execute the given executable
```

The custom options are explained below.


### `executable`

Path to the partdiff executable.

Use `--executable=/path/to/partdiff` (not `--executable /path/to/partdiff`), because pytest's argparser is a bit dumb.

You can pass a space-separated list to do something like this:

```shell
$ pytest --executable='mpirun /path/to/partdiff'
```

Quoting is supported, so this works:

```shell
$ pytest --executable='mpirun "/path/to/your weird/partdiff"'
```

### `strictness`

| Strictness level | What is checked? |
|-|-|
| 0 | Only the matrix |
| 1 | `(0)` + Matrix and residuum (right-hand-side) |
| 2 | `(1)` + right-hand-side of {calculation method, interlines, pertubation function, number of iterations} |
| 3 | `(2)` + left-hand-side of {calculation time, memory usage, calculation method, interlines, pertubation function, number of iterations, residuum} |
| 4 | Full char-by-char diff (except for calculation time and memory usage) |

## `valgrind`

Start the executable with `valgrind --leak-check=full`.

This takes very long!

### TODO: `filter`

Filter args, e.g. only `termination=1`.

### TODO: `cwd`

Set working directory

### TODO: `threads`

Support more than one thread

### TODO: 'max_num_tests`

Only do `n` tests.
