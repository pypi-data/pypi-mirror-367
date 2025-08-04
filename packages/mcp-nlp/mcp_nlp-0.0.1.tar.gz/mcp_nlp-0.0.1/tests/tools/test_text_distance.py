import pytest

from src.mcp_nlp.tools.text_distance import list_metrics, measure


@pytest.mark.asyncio
async def test_measure_success() -> None:
    """
    Tests successful execution of the measure tool.
    """
    result = await measure.fn(
        source="hello",
        reference="hallo",
        algorithm="levenshtein",
        metric="distance",
    )
    assert result == 1.0


@pytest.mark.asyncio
async def test_measure_unsupported_algorithm() -> None:
    """
    Tests that measure tool raises ValueError for an unsupported algorithm.
    """
    with pytest.raises(ValueError, match="Unsupported algorithm: 'invalid_algo'"):
        await measure.fn(source="a", reference="b", algorithm="invalid_algo")


@pytest.mark.asyncio
async def test_list_metrics_success() -> None:
    """
    Tests successful execution of the list_metrics tool.
    """
    expected_metrics = [
        "distance",
        "similarity",
        "normalized_distance",
        "normalized_similarity",
        "maximum",
    ]
    result = await list_metrics.fn()
    assert result == expected_metrics
