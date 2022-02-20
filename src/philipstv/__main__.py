import sys


def wrapped_cli() -> None:
    try:
        from ._cli import cli
    except ModuleNotFoundError:
        print("CLI dependencies missing!", file=sys.stderr, flush=True)
        print("Please install the package as 'philipstv[cli]'.", file=sys.stderr, flush=True)
        sys.exit(1)
    else:
        cli()


if __name__ == "__main__":
    wrapped_cli()
