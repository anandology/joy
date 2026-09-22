## Version 0.4.1 - 2026-09-21

* Moved packaging to pyproject.toml, managed with uv
* Included the README as the project description on PyPI

## Version 0.4.0 - 2024-12-24

* Added setup.py to release a pypi package
* Improved the docs

## Version 0.3.1 - 2021-12-29
* Fixed inconsistencies in rendering caused due to a bug in cloning the node (#34)

## Version 0.3.0 - 2021-10-11

* Improved the repeat tranformation and fixed a couple of bugs that were introduced due to these improvements
* Added new functions `combine`, `color` and `random`
* Added `polyline` shape (tx @abhinavxd)
* Added `polygon` shape
* Added `as_dict` method to Shape to be able to serialize the shapes to JSON
* Added lowercase function names for transformations.
* Fixed the issues with `line` function

## Version 0.2.3 - 2021-06-19

* Fixed a typo that causing the y coordinate to be initialized to the value of argument `x` instead of `y`.

## Version 0.2.2 - 2021-06-17

* Added lowercase functions for shapes with simpler API

## Version 0.2.1 - 2021-06-11

* Made the y value grow upwards, just like the classical cartisian
coordinate system learn in the high school

## Version 0.2.0 - 2021-06-10

* Refactored the entire API of the library, not backword-compatible

## Version 0.1 - 2021-06-04

* First release!

