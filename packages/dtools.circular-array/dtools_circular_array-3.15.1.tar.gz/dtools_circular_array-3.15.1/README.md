# Developer Tools - Circular Array **DEPRICATED**

Please use PyPI project
[pythonic-fp-circularray](https://pypi.org/project/pythonic-fp-circulararray/)
instead.

Python package containing a module implementing a circular array data
structure, This project is part of the [Developer Tools for Python][4]
**dtools** namespace projects.

- **Repositories**
  - [dtools.circular-array][1] project on *PyPI*
  - [Source code][2] on *GitHub*
- **Detailed documentation**
  - [Detailed API documentation][3] on *GH-Pages*

## Overview

A full featured auto resizing circular array data structure. Double
sided, indexable, sliceable, and iterable. When iterated, uses cached
copies of its present state so that the circular array itself can safely
be mutated.

- O(1) amortized pushes and pops either end.
- O(1) indexing
- fully supports slicing
- safely mutates over previous state

Useful either if used directly like a Python list, or in a "has-a"
relationship when implementing other data structures.

- *module* dtools.circular_array
  - *class* `CA:` circular array data structure
    - initializer takes 1 or 0 iterators
      - like `list` or `set` does
  - *function* `ca`: produces a `CA` from the function's arguments
    - similar use case as syntactic constructs `[]` or `{}`

Above nomenclature modeled after builtin data types like `list`, where
`CA` and `ca` correspond respectfully to `list` and  `[]` in their use
cases.

#### Usage

```python
    from dtools.circular_array import CA, ca
    
    ca1 = ca(1, 2, 3)
    assert ca1.popl() == 1
    assert ca1.popr() == 3
    ca1.pushr(42, 0)
    ca1.pushl(0, 1)
    assert repr(ca1) == 'ca(1, 0, 2, 42, 0)'
    assert str(ca1) == '(|1, 0, 2, 42, 0|)'
    
    ca2 = CA(range(1,11))
    assert repr(ca2) == 'ca(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)'
    assert str(ca2) == '(|1, 2, 3, 4, 5, 6, 7, 8, 9, 10|)'
    assert len(ca2) == 10
    tup3 = ca2.poplt(3)
    tup4 = ca2.poprt(4)
    assert tup3 == (1, 2, 3)
    assert tup4 == (10, 9, 8, 7)
    assert ca2 == ca(4, 5, 6)
    four, *rest = ca2.poplt(1000)
    assert four == 4
    assert rest == [5, 6]
    assert len(ca2) == 0
    
    ca3 = CA([1, 2, 3])
    assert ca3.popld(42) == 1
    assert ca3.poprd(42) == 3
    assert ca3.popld(42) == 2
    assert ca3.poprd(42) == 42
    assert ca3.popld(42) == 42
    assert len(ca2) == 0
```

[1]: https://pypi.org/project/dtools.circular-array
[2]: https://github.com/grscheller/dtools-circular-array
[3]: https://grscheller.github.io/dtools-namespace-projects/circular-array
[4]: https://github.com/grscheller/dtools-namespace-projects/blob/main/README.md
