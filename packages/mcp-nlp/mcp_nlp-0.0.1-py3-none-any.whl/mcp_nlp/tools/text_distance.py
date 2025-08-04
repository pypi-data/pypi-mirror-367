from fastmcp import FastMCP

from ..services.text_distance import Metric, TextDistanceEvaluator

textdistance_mcp: FastMCP = FastMCP("MCP: Text Distance Calculator")


@textdistance_mcp.tool()
async def measure(
    source: str,
    reference: str,
    algorithm: str = "levenshtein",
    metric: Metric = "normalized_similarity",
) -> float:
    """Measures text distance between two sequences of strings using various algorithms."""

    evaluator = TextDistanceEvaluator(algorithm=algorithm, metric=metric)
    return evaluator.compute(source, reference)


@textdistance_mcp.tool()
async def list_metrics() -> list[str]:
    """List supported metrics for text distance algorithms."""

    return TextDistanceEvaluator.list_metrics()
