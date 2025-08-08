from semver.version import Version


def mp_version_to_mpy_abi_version(mp_ver: Version) -> str:
    """
    Convert MicroPython version to mpy-cross ABI version.

    See https://docs.micropython.org/en/latest/reference/mpyfiles.html#versioning-and-compatibility-of-mpy-files

    Parameters:
        mp_ver: MicroPython version

    Returns:
        str: mpy-cross ABI version

    Raises:
        TypeError: If the input is not a valid version string
        NotImplementedError: If the MicroPython version is not supported
    """
    if mp_ver.match(">=1.23.0"):
        return "6.3"

    if mp_ver.match(">=1.22.0"):
        return "6.2"

    if mp_ver.match(">=1.20.0"):
        return "6.1"

    if mp_ver.match(">=1.19.0"):
        return "6"

    if mp_ver.match(">=1.12.0"):
        return "5"

    raise NotImplementedError("MicroPython version must be >=1.12.0")
