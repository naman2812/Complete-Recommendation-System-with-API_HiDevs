import pytest
from engine.evaluator import RecommendationEvaluator


def test_precision_at_k():
    evaluator = RecommendationEvaluator()
    # recommended: [1, 2, 3], relevant: {2, 3, 4} -> 2/3 precision
    p = evaluator.precision_at_k([1, 2, 3], {2, 3, 4}, k=3)
    assert p == pytest.approx(0.666, abs=0.01)


def test_recall_at_k():
    evaluator = RecommendationEvaluator()
    # recommended: [1, 2, 3], relevant: {2, 3, 4, 5} -> 2 relevant retrieved out of 4 total -> 0.5
    r = evaluator.recall_at_k([1, 2, 3], {2, 3, 4, 5}, k=3)
    assert r == 0.5


def test_ndcg_at_k():
    evaluator = RecommendationEvaluator()
    # Perfect ranking
    n1 = evaluator.ndcg_at_k([1, 2, 3], {1, 2, 3}, k=3)
    assert n1 == 1.0

    # Worst ranking
    n2 = evaluator.ndcg_at_k([4, 5, 6], {1, 2, 3}, k=3)
    assert n2 == 0.0


def test_evaluate_system():
    evaluator = RecommendationEvaluator()
    ground_truth = {1: {10, 20}, 2: {30}}
    recommendations = {1: [10, 99, 88], 2: [99, 88, 77]}
    metrics = evaluator.evaluate_all(recommendations, ground_truth, k=3)
    # User 1: precision = 1/3, recall = 1/2.
    # User 2: precision = 0, recall = 0.
    # Avg precision = 1/6 = 0.166...
    assert metrics["precision@3"] == pytest.approx(0.166, abs=0.01)
    # Avg recall = (0.5 + 0) / 2 = 0.25
    assert metrics["recall@3"] == 0.25
