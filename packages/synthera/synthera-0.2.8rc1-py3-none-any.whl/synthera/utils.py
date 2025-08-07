from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "synthera"


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        raise
