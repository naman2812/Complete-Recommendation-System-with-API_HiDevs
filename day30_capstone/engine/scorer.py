class RecommendationScorer:
    def __init__(self):
        """
        Initialize the scorer with an empty list of scoring components.
        """
        self.scorers = []

    def add_scorer(self, name, function, weight):
        """
        Register a scoring function with a specific weight.
        - function: Must take (user_id, item_id, context) and return a float [0.0, 1.0]
        - weight: The importance multiplier for this score
        """
        self.scorers.append({
            "name": name,
            "function": function,
            "weight": weight
        })

    def calculate_score(self, user_id, item_id, context=None):
        """
        Calculates the combined score for a single item.
        Returns a tuple of (final_score, explanation_str, breakdown_dict).
        """
        if not self.scorers:
            return 0.0, "No scorers registered", {}
            
        total_score = 0.0
        total_weight = 0.0
        explanations = []
        breakdown = {}
        
        for scorer in self.scorers:
            try:
                score = scorer["function"](user_id, item_id, context)
            except Exception:
                score = 0.0 # Fail gracefully
                
            weight = scorer["weight"]
            
            # Store in breakdown
            breakdown[scorer["name"]] = round(score, 4)
            
            total_score += score * weight
            total_weight += weight
            
            if score >= 0.5:
                explanations.append(f"high {scorer['name']}")
                
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        if explanations:
            explanation = "Recommended due to: " + ", ".join(explanations)
        else:
            explanation = "General recommendation"
            
        return final_score, explanation, breakdown

    def rank_candidates(self, user_id, candidates, limit=10, context=None):
        """
        Scores a list of candidates and returns the top `limit` results.
        Returns list of dicts with 'item_id', 'score', 'explanation', 'breakdown'.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        for item_id in candidates:
            score, explanation, breakdown = self.calculate_score(user_id, item_id, context)
            scored_candidates.append({
                "item_id": item_id,
                "score": score,
                "explanation": explanation,
                "breakdown": breakdown
            })
            
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:limit]
