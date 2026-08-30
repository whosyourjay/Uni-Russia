"""Render Russia's preferred figure sequence."""

from viz import bvi, coverage, funding, spo


def main():
    bvi.main()
    funding.main()
    coverage.main()
    spo.main()


if __name__ == "__main__":
    main()
