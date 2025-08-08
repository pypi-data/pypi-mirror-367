# Python packaging for multi-target mpy-cross

This repository contains Python packaging to distribute the `mpy-cross` tool
from [MicroPython](https://github.com/micropython/micropython) via PyPI.

This package includes multiple versions of `mpy-cross` to support different
MicroPython runtime versions.

## Installation

To install the latest version of `mpy-cross-multi`:

    pip install mpy-cross-multi

## Usage

This package can be used programmatically or as a command line script.

### Script

This can be used just like the original `mpy-cross` tool: by substituting
the name `mpy-cross` with `mpy-cross-multi` in the command line.

    mpy-cross-multi --version

It has an optional extra command line option to target older MicroPython
runtimes. The oldest support MicroPython runtime is v1.12.

    mpy-cross-multi --micropython 1.22 ...
