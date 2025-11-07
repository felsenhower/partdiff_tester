# partdiff-tester


### Executable

Path to executable as a string (can contain quotes if necessary).

### Strictness

| Strictness level | What is checked? |
|-|-|
| 0 | Only the matrix |
| 1 | `(0)` + Matrix and residuum (right-hand-side) |
| 2 | `(1)` + right-hand-side of {calculation method, interlines, pertubation function, number of iterations} |
| 3 | `(2)` + left-hand-side of {calculation time, memory usage, calculation method, interlines, pertubation function, number of iterations, residuum} |
| 4 | Full char-by-char diff (except for calculation time and memory usage) |

### Filter

TODO: Filter args, e.g. only `termination=1`.


