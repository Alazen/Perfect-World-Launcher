import sys


def main() -> None:
    try:
        from launcher.app import run
    except ImportError as exc:
        print(exc)
        sys.exit(1)
    run()


if __name__ == "__main__":
    main()
