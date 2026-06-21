import pytest
from engine.candidate_gen import CandidateGenerator

@pytest.fixture
def generator():
    user_history = {
        1: {101, 102},
        2: {102, 103},
        3: {101, 103}
    }
    user_similarities = {
        1: [(2, 0.8), (3, 0.4)],
        2: [(1, 0.8), (3, 0.5)],
        3: [(1, 0.4), (2, 0.5)]
    }
    item_similarities = {
        101: [(102, 0.5), (103, 0.1)],
        102: [(101, 0.5), (103, 0.9)],
        103: [(102, 0.9), (101, 0.1)]
    }
    all_items = [101, 102, 103, 104]
    
    return CandidateGenerator(user_history, user_similarities, item_similarities, all_items)

def test_collaborative_candidates(generator):
    # User 1 has seen 101, 102. Similar users (2,3) have seen 103. 
    # Therefore, 103 should be recommended to User 1.
    candidates = generator.collaborative_candidates(1, limit=5)
    assert 103 in candidates
    assert 101 not in candidates # Already seen

def test_content_based_candidates(generator):
    # User 1 has seen 101, 102. 102 is similar to 103.
    candidates = generator.content_based_candidates(1, limit=5)
    assert 103 in candidates
    assert 101 not in candidates

def test_popularity_candidates(generator):
    # Popularity falls back to all items sorted randomly or by a popularity metric.
    # In CandidateGenerator, it returns most frequent items across all histories.
    # 101: 2, 102: 2, 103: 2, 104: 0
    candidates = generator.popularity_candidates(limit=2)
    assert len(candidates) == 2

def test_hybrid_candidates(generator):
    candidates = generator.hybrid_candidates(1, limit=5)
    assert isinstance(candidates, list)
    assert 103 in candidates
