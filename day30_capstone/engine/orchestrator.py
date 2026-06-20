import time
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from data.repositories import UserRepository, ContentRepository, InteractionRepository
from engine.candidate_gen import CandidateGenerator
from engine.scorer import RecommendationScorer
from engine.similarity import SimilarityCalculator

class RecommendationOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.content_repo = ContentRepository(db)
        self.interaction_repo = InteractionRepository(db)
        
        # Caching layer
        self.cache = {}
        self.cache_ttl = 300 # 5 minutes

        self.scorer = RecommendationScorer()
        self._configure_scorers()

    def _configure_scorers(self):
        def popularity_score(user_id, item_id, context):
            content = self.content_repo.get_content(item_id)
            if not content: return 0.0
            # Normalize popularity
            return min(content.popularity / 100.0, 1.0)

        def skill_match_score(user_id, item_id, context):
            user = self.user_repo.get_user(user_id)
            content = self.content_repo.get_content(item_id)
            if not user or not content: return 0.0
            
            user_skill_ids = {us.skill_id for us in user.skills}
            content_skill_ids = {cs.skill_id for cs in content.skills}
            
            if not user_skill_ids or not content_skill_ids: return 0.0
            
            intersection = len(user_skill_ids.intersection(content_skill_ids))
            union = len(user_skill_ids.union(content_skill_ids))
            return intersection / union if union > 0 else 0.0

        def difficulty_match_score(user_id, item_id, context):
            return 0.5 

        self.scorer.add_scorer("popularity", popularity_score, weight=0.3)
        self.scorer.add_scorer("skill_match", skill_match_score, weight=0.5)
        self.scorer.add_scorer("difficulty", difficulty_match_score, weight=0.2)

    def _build_data_structures(self):
        interactions = self.interaction_repo.get_all_interactions()
        all_content = [c.id for c in self.content_repo.get_all_content()]
        all_users = [u.id for u in self.user_repo.get_all_users()]

        user_history = {}
        user_ratings = {}
        
        for interaction in interactions:
            u_id = interaction.user_id
            i_id = interaction.content_id
            
            if u_id not in user_history:
                user_history[u_id] = set()
            user_history[u_id].add(i_id)
            
            if interaction.rating is not None:
                if u_id not in user_ratings:
                    user_ratings[u_id] = {}
                user_ratings[u_id][i_id] = interaction.rating

        user_similarities = {}
        for u1 in all_users:
            sims = []
            for u2 in all_users:
                if u1 != u2:
                    r1 = user_ratings.get(u1, {})
                    r2 = user_ratings.get(u2, {})
                    sim = SimilarityCalculator.pearson_correlation(r1, r2)
                    if sim > 0:
                        sims.append((u2, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            user_similarities[u1] = sims[:5]

        item_similarities = {}
        for i1 in all_content:
            sims = []
            for i2 in all_content:
                if i1 != i2:
                    users_i1 = {u for u, hist in user_history.items() if i1 in hist}
                    users_i2 = {u for u, hist in user_history.items() if i2 in hist}
                    sim = SimilarityCalculator.jaccard_similarity(users_i1, users_i2)
                    if sim > 0:
                        sims.append((i2, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            item_similarities[i1] = sims[:5]

        return user_history, user_similarities, item_similarities, all_content

    def get_recommendations(self, user_id: int, limit: int = 5, strategy: str = "hybrid", refresh: bool = False):
        cache_key = f"recs_{user_id}_{limit}_{strategy}"
        
        # Check Cache
        if not refresh and cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry['timestamp'] < self.cache_ttl:
                return entry['data']

        # Not in cache, generate
        user_history, user_similarities, item_similarities, all_content = self._build_data_structures()
        
        generator = CandidateGenerator(
            user_history=user_history,
            user_similarities=user_similarities,
            item_similarities=item_similarities,
            all_items=all_content
        )

        # Cold Start Detection
        user_hist = user_history.get(user_id, set())
        is_cold_start = len(user_hist) < 3

        applied_strategy = strategy
        
        if is_cold_start:
            candidates = generator.popularity_candidates(limit=limit*3)
            applied_strategy = "cold_start_popular"
        else:
            # Route strategy
            if strategy == "collaborative":
                candidates = generator.collaborative_candidates(user_id, limit=limit*3)
            elif strategy == "content":
                candidates = generator.content_based_candidates(user_id, limit=limit*3)
            elif strategy == "popular":
                candidates = generator.popularity_candidates(limit=limit*3)
            else: # hybrid
                candidates = generator.hybrid_candidates(user_id, limit=limit*3)
                
            # Absolute fallback
            if not candidates:
                candidates = generator.popularity_candidates(limit=limit*3)
                applied_strategy = "cold_start_popular"
            
        # Score and Rank
        ranked = self.scorer.rank_candidates(user_id, candidates, limit=limit)
        
        # Format output
        results = []
        for rec in ranked:
            content = self.content_repo.get_content(rec['item_id'])
            if content:
                results.append({
                    "id": content.id,
                    "title": content.title,
                    "category": content.category,
                    "score": round(rec['score'], 3),
                    "explanation": rec['explanation'],
                    "breakdown": rec['breakdown'],
                    "strategy": applied_strategy
                })
                
        # Save to cache
        self.cache[cache_key] = {
            "timestamp": time.time(),
            "data": results
        }
        
        return results

    def record_feedback(self, user_id: int, content_id: int, interaction_type: str, rating: float = None):
        self.interaction_repo.record_interaction(user_id, content_id, interaction_type, rating)
        
        # Invalidate cache for this user
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"recs_{user_id}_")]
        for k in keys_to_delete:
            del self.cache[k]
        
        return True
