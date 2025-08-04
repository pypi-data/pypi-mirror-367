import pytest

from src.mcp_nlp.services.text_distance import Metric, TextDistanceEvaluator


def test_text_distance_evaluator_init_success() -> None:
    """
    Tests successful initialization of TextDistanceEvaluator.
    """
    evaluator = TextDistanceEvaluator(algorithm="levenshtein")
    assert evaluator.algorithm is not None
    assert evaluator.metric == "normalized_similarity"


def test_text_distance_evaluator_init_unsupported_algorithm() -> None:
    """
    Tests that TextDistanceEvaluator raises ValueError for an unsupported algorithm.
    """
    with pytest.raises(ValueError, match="Unsupported algorithm: 'invalid_algo'"):
        TextDistanceEvaluator(algorithm="invalid_algo")


@pytest.mark.parametrize(
    "algorithm,metric,source,reference,expected",
    [
        ("levenshtein", "distance", "hello", "hallo", 1.0),
        ("levenshtein", "similarity", "hello", "hallo", 4.0),
        (
            "levenshtein",
            "normalized_similarity",
            "saturday",
            "sunday",
            0.625,
        ),
        ("jaro_winkler", "normalized_similarity", "martha", "marhta", 0.9611111111111111),
    ],
)
def test_text_distance_evaluator_compute(
    algorithm: str,
    metric: Metric,
    source: str,
    reference: str,
    expected: float,
) -> None:
    """
    Tests the compute method with various algorithms and metrics.
    """
    evaluator = TextDistanceEvaluator(algorithm=algorithm, metric=metric)
    assert evaluator.compute(source, reference) == pytest.approx(expected)


def test_text_distance_evaluator_compute_unsupported_metric() -> None:
    """
    Tests that compute raises ValueError for an unsupported metric.
    """
    evaluator = TextDistanceEvaluator(
        algorithm="levenshtein",
        metric="invalid_metric",  # type: ignore
    )
    with pytest.raises(ValueError, match="Unsupported metric: 'invalid_metric'"):
        evaluator.compute("a", "b")


def test_list_metrics() -> None:
    """
    Tests the list_metrics class method.
    """
    expected_metrics = [
        "distance",
        "similarity",
        "normalized_distance",
        "normalized_similarity",
        "maximum",
    ]
    assert TextDistanceEvaluator.list_metrics() == expected_metrics
