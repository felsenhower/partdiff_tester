"""Output masks for partdiff.

These are essentially regexes that (have to) match the output of a partdiff implementation.

There are output masks for different strictness levels (see --strictness).

In most cases OUTPUT_MASKS[strictness] is used.

When --allow-extra-iterations is passed, OUTPUT_MASKS_ALLOW_EXTRA_ITER[strictness]
and OUTPUT_MASKS_WITH_EXTRA_ITER[strictness] may be used instead in some cases.
"""

import re

NUM_OUTPUT_MASKS = 5

RE_MATRIX_FLOAT = re.compile(r"[01]\.[0-9]{4}")

F = RE_MATRIX_FLOAT.pattern

RE_MATRIX = re.compile(
    rf"""
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*\n
    \s*{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s+{F}\s*
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_0 = re.compile(
    rf"""
    ^
    .*
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_1 = re.compile(
    rf"""
    ^
    .*
    ([0-9\.e+-]+)
    \s*
    .+:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_2 = re.compile(
    rf"""
    ^
    (.+): \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    (.+): \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    (.+): \s+ .+               \s*\n # Calculation method
    (.+): \s+ ([0-9]+)         \s*\n # Interlines
    (.+): \s+ .+               \s*\n # Inference function
    (.+): \s+ .+               \s*\n # Termination
    (.+): \s+ ([0-9]+)         \s*\n # Number iterations
    (.+): \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    .+:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_3 = re.compile(
    rf"""
    ^
    Calculation\stime:   \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    Memory\susage:       \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    Calculation\smethod: \s+ (.+)             \s*\n # Calculation method
    Interlines:          \s+ ([0-9]+)         \s*\n # Interlines
    Inference\sfunction: \s+ (.+)             \s*\n # Inference function
    Termination:         \s+ (.+)             \s*\n # Termination
    Number\siterations:  \s+ ([0-9]+)         \s*\n # Number iterations
    Residuum:            \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    Matrix:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_4 = re.compile(
    (
        # fmt: off
        r"^"
        r"Calculation time:   [0-9]+\.[0-9]{6} s\n"
        r"Memory usage:       [0-9]+\.[0-9]{6} MiB\n"
        r"Calculation method: (.+)\n"
        r"Interlines:         ([0-9]+)\n"
        r"Inference function: (.+)\n"
        r"Termination:        (.+)\n"
        r"Number iterations:  ([0-9]+)\n"
        r"Residuum:           ([0-9\.e+-]+)\n"
        r"\n"
        r"Matrix:\n"
        r"("
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        r")$"
        # fmt: on
    ),
    re.DOTALL,
)


RE_OUTPUT_MASK_STRICT_0_ALLOW_EXTRA_ITER = re.compile(
    rf"""
    ^
    .*
    {RE_MATRIX.pattern}
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_1_ALLOW_EXTRA_ITER = re.compile(
    rf"""
    ^
    .*
    [0-9\.e+-]+
    \s*
    .+:
    {RE_MATRIX.pattern}
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_2_ALLOW_EXTRA_ITER = re.compile(
    rf"""
    ^
    (.+): \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    (.+): \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    (.+): \s+ .+               \s*\n # Calculation method
    (.+): \s+ ([0-9]+)         \s*\n # Interlines
    (.+): \s+ .+               \s*\n # Inference function
    (.+): \s+ .+               \s*\n # Termination
    (.+): \s+ [0-9]+           \s*\n # Number iterations
    (.+): \s+ [0-9\.e+-]+      \s*\n # Residuum
    \s*
    .+:
    {RE_MATRIX.pattern}
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_3_ALLOW_EXTRA_ITER = re.compile(
    rf"""
    ^
    Calculation\stime:   \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    Memory\susage:       \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    Calculation\smethod: \s+ (.+)             \s*\n # Calculation method
    Interlines:          \s+ ([0-9]+)         \s*\n # Interlines
    Inference\sfunction: \s+ (.+)             \s*\n # Inference function
    Termination:         \s+ (.+)             \s*\n # Termination
    Number\siterations:  \s+ [0-9]+           \s*\n # Number iterations
    Residuum:            \s+ [0-9\.e+-]+      \s*\n # Residuum
    \s*
    Matrix:
    {RE_MATRIX.pattern}
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_4_ALLOW_EXTRA_ITER = re.compile(
    (
        # fmt: off
        r"^"
        r"Calculation time:   [0-9]+\.[0-9]{6} s\n"
        r"Memory usage:       [0-9]+\.[0-9]{6} MiB\n"
        r"Calculation method: (.+)\n"
        r"Interlines:         ([0-9]+)\n"
        r"Inference function: (.+)\n"
        r"Termination:        (.+)\n"
        r"Number iterations:  [0-9]+\n"
        r"Residuum:           [0-9\.e+-]+\n"
        r"\n"
        r"Matrix:\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        r"$"
        # fmt: on
    ),
    re.DOTALL,
)


RE_OUTPUT_MASK_STRICT_0_WITH_EXTRA_ITER = RE_OUTPUT_MASK_STRICT_0

RE_OUTPUT_MASK_STRICT_1_WITH_EXTRA_ITER = RE_OUTPUT_MASK_STRICT_1

RE_OUTPUT_MASK_STRICT_2_WITH_EXTRA_ITER = RE_OUTPUT_MASK_STRICT_2

RE_OUTPUT_MASK_STRICT_3_WITH_EXTRA_ITER = re.compile(
    rf"""
    ^
    Calculation\stime:   \s+ [0-9\.]+ \s+ s   \s*\n # Calculation time
    Memory\susage:       \s+ [0-9\.]+ \s+ MiB \s*\n # Memory usage
    Calculation\smethod: \s+ (.+)             \s*\n # Calculation method
    Interlines:          \s+ ([0-9]+)         \s*\n # Interlines
    Inference\sfunction: \s+ (.+)             \s*\n # Inference function
    Termination:         \s+ .+               \s*\n # Termination
    Number\siterations:  \s+ ([0-9]+)         \s*\n # Number iterations
    Residuum:            \s+ ([0-9\.e+-]+)    \s*\n # Residuum
    \s*
    Matrix:
    ({RE_MATRIX.pattern})
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

RE_OUTPUT_MASK_STRICT_4_WITH_EXTRA_ITER = re.compile(
    (
        # fmt: off
        r"^"
        r"Calculation time:   [0-9]+\.[0-9]{6} s\n"
        r"Memory usage:       [0-9]+\.[0-9]{6} MiB\n"
        r"Calculation method: (.+)\n"
        r"Interlines:         ([0-9]+)\n"
        r"Inference function: (.+)\n"
        r"Termination:        .+\n"
        r"Number iterations:  ([0-9]+)\n"
        r"Residuum:           ([0-9\.e+-]+)\n"
        r"\n"
        r"Matrix:\n"
        r"("
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        rf" {F} {F} {F} {F} {F} {F} {F} {F} {F}\n"
        r")$"
        # fmt: on
    ),
    re.DOTALL,
)


RE_OUTPUT_MASK_FOR_ITERATIONS = re.compile(
    rf"""
    ^
    .*
    .+: \s+ ([0-9]+)    \s*\n # Number of iterations
    .+: \s+ [0-9\.e+-]+ \s*\n # Residuum
    \s*
    .+:
    {RE_MATRIX.pattern}
    .*
    $
""",
    re.VERBOSE | re.DOTALL,
)

OUTPUT_MASKS = [
    RE_OUTPUT_MASK_STRICT_0,
    RE_OUTPUT_MASK_STRICT_1,
    RE_OUTPUT_MASK_STRICT_2,
    RE_OUTPUT_MASK_STRICT_3,
    RE_OUTPUT_MASK_STRICT_4,
]

OUTPUT_MASKS_ALLOW_EXTRA_ITER = [
    RE_OUTPUT_MASK_STRICT_0_ALLOW_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_1_ALLOW_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_2_ALLOW_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_3_ALLOW_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_4_ALLOW_EXTRA_ITER,
]

OUTPUT_MASKS_WITH_EXTRA_ITER = [
    RE_OUTPUT_MASK_STRICT_0_WITH_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_1_WITH_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_2_WITH_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_3_WITH_EXTRA_ITER,
    RE_OUTPUT_MASK_STRICT_4_WITH_EXTRA_ITER,
]

assert len(OUTPUT_MASKS) == NUM_OUTPUT_MASKS
assert len(OUTPUT_MASKS_ALLOW_EXTRA_ITER) == NUM_OUTPUT_MASKS
assert len(OUTPUT_MASKS_WITH_EXTRA_ITER) == NUM_OUTPUT_MASKS
