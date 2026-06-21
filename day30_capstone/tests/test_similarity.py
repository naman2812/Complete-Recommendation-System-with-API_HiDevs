import pytest
from engine.similarity import SimilarityCalculator

def test_jaccard_similarity():
    set1 = {1, 2, 3}
    set2 = {2, 3, 4}
    sim = SimilarityCalculator.jaccard_similarity(set1, set2)
    assert sim == 0.5  # Intersection(2,3) / Union(1,2,3,4) = 2/4 = 0.5

def test_jaccard_empty():
    assert SimilarityCalculator.jaccard_similarity(set(), set()) == 1.0
    assert SimilarityCalculator.jaccard_similarity({1}, set()) == 0.0

def test_cosine_similarity():
    v1 = {"math": 1.0, "science": 1.0}
    v2 = {"math": 1.0, "history": 1.0}
    sim = SimilarityCalculator.cosine_similarity(v1, v2)
    # math intersection = 1. magnitudes = sqrt(2). 1 / 2 = 0.5
    assert sim == pytest.approx(0.5)

def test_cosine_empty():
    assert SimilarityCalculator.cosine_similarity({}, {}) == 0.0

def test_pearson_correlation():
    r1 = {1: 5, 2: 4, 3: 3}
    r2 = {1: 5, 2: 4, 3: 3}
    sim = SimilarityCalculator.pearson_correlation(r1, r2)
    assert sim > 0.99  # perfectly correlated

    # Uncorrelated/negative
    r3 = {1: 1, 2: 2, 3: 3}
    r4 = {1: 5, 2: 4, 3: 3}
    sim_neg = SimilarityCalculator.pearson_correlation(r3, r4)
    assert sim_neg < 0

def test_pearson_low_overlap():
    assert SimilarityCalculator.pearson_correlation({1: 5}, {2: 5}) == 0.0
