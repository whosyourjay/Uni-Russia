"""Stable locations for repository resources and derived tables."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(*parts):
    """Absolute path to a repository resource, e.g.
    ``path("assessment-pool.tsv")``."""
    return os.path.join(ROOT, *parts)


def data_path(*parts):
    """Absolute path to parsed or published input data."""
    return path("data", *parts)


def source_path(*parts):
    """Absolute path to a downloaded source document."""
    return path("sources", *parts)


def ranking_path(*parts):
    """Absolute path to generated ranking tables."""
    return path("rankings", *parts)
