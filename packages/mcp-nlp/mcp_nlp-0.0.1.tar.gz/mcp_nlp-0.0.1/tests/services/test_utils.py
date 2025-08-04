import sys

import pytest
from textdistance.algorithms.base import Base, BaseSimilarity

from src.mcp_nlp.services.utils import _import_string


def test_import_string() -> None:
    algorithms = ("levenshtein", "jaro_winkler", "cosine")
    for algorithm in algorithms:
        algorithm = _import_string(f"textdistance.{algorithm}")
        assert issubclass(type(algorithm), Base | BaseSimilarity)


def test_import_string_w_non_existing_path() -> None:
    algorithm_name = "non_existing_algorithm"
    with pytest.raises(ImportError):
        _import_string(f"textdistance.{algorithm_name}")


def test_import_string_w_badly_formatted_path() -> None:
    with pytest.raises(ImportError):
        _import_string("textdistance-levenshtein")


def test_import_string_forces_module_import() -> None:
    if "math" in sys.modules:
        del sys.modules["math"]
    sqrt = _import_string("math.sqrt")
    assert sqrt(4) == 2
