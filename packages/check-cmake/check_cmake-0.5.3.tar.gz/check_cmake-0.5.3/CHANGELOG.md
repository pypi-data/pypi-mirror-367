# Changelog

## v0.5.3

- Fixed `# nocheck` not working in some rare circumstances

## v0.5.2

- Fixed internal `Path.relative_to()` error when used inside a virtual environment

## v0.5.1

- Fixed false positive for incorrect use of `SYSTEM` in `target_include_directories()` in some cases

## v0.5.0

- Added check for `add_library()` with implicit type (`STATIC`, `SHARED`, et cetera)

## v0.4.0

- Fixed line numbers sometimes being wrong in context snippets
- Added check for incorrectly-placed `SYSTEM` in `target_include_directories()`
- Added check for extraneous space in `ExternalProject_Add()` `CMAKE_ARGS`

## v0.3.0

- Fixed `#nocheck`

## v0.2.0

- Added pragmas for ignoring checks on a line
- Added check for `cmake_minimum_required()` when `project()` is present
- Fixed minor formatting issues

## v0.1.0

- First public release 🎉&#xFE0F;
