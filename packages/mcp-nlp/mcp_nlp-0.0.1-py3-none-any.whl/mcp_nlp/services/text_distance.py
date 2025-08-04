from typing import Literal, get_args

from .utils import _import_string

__all__ = ["TextDistanceEvaluator", "Metric"]

Metric = Literal[
    "distance",
    "similarity",
    "normalized_distance",
    "normalized_similarity",
    "maximum",
]


class TextDistanceEvaluator:
    """
    Measures text distance between two strings using various algorithms.
    """

    def __init__(
        self,
        algorithm: str,
        metric: Metric = "normalized_similarity",
    ) -> None:
        try:
            # Use import_module for importing "textdistance" package and target algorithm
            self.algorithm = _import_string(f"textdistance.{algorithm}")
        except ImportError as e:
            msg = f"Unsupported algorithm: '{algorithm}'"
            raise ValueError(msg) from e
        self.metric = metric

    def compute(self, source: str, reference: str) -> float:
        """
        Calculates text distance between source and reference segments.
        """
        try:
            return getattr(self.algorithm, self.metric)(source, reference)
        except AttributeError as e:
            msg = f"Unsupported metric: '{self.metric}'"
            raise ValueError(msg) from e

    @classmethod
    def list_metrics(cls) -> list[str]:
        """
        Lists supported textdistance metrics.
        """
        return list(get_args(Metric))
