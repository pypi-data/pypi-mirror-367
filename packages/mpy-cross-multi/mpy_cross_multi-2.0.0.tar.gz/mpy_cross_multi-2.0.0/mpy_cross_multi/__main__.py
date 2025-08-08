import sys
import subprocess
import importlib
import itertools

from semver.version import Version

from mpy_cross_multi import mp_version_to_mpy_abi_version


def _run():
    """
    Run mpy-cross directly with extra arg for getting the right version.
    """

    # remove the first argument (the script name)
    # if there is --micropython=X.Y, split it into two arguments
    args = list(
        itertools.chain(
            *(
                arg.split("=") if arg.startswith("--micropython") else (arg,)
                for arg in sys.argv[1:]
            )
        )
    )

    try:
        idx = args.index("--micropython")
    except ValueError:
        # default if argument is not given
        mp_ver = "1.23"
    else:
        # argument is given
        mp_ver = args.pop(idx + 1)
        # also remove the --micropython flag
        del args[idx]

    # validate the version argument
    try:
        mp_semver = Version.parse(mp_ver, optional_minor_and_patch=True)
    except ValueError:
        print(
            f"Error: invalid version format for --micropython: '{mp_ver}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        abi = mp_version_to_mpy_abi_version(mp_semver)
    except NotImplementedError:
        print(
            f"Error: targeting MicroPython v{mp_semver} is not supported",
            file=sys.stderr,
        )
        sys.exit(1)

    # get the right mpy-cross version for the target ABI
    mpy_cross = importlib.import_module(f"mpy_cross_v{abi.replace('.', '_')}")

    # run mpy-cross with the remaining arguments
    proc = subprocess.run([mpy_cross.MPY_CROSS_PATH] + args)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    _run()
