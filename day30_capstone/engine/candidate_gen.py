class CandidateGenerator:
    def __init__(self, user_history, user_similarities, item_similarities, all_items):
        """
        Initialize with data sources. In a real system, these would likely be
        database queries or caching layer lookups.
        """
        self.user_history = user_history
        self.user_similarities = user_similarities
        self.item_similarities = item_similarities
        self.all_items = set(all_items)

    def collaborative_candidates(self, user_id, limit=20):
        """
        Generates candidates based on what similar users liked.
        """
        candidates = set()
        if user_id not in self.user_similarities:
            return []

        history = self.user_history.get(user_id, set())
        for sim_user, _ in self.user_similarities.get(user_id, []):
            sim_user_history = self.user_history.get(sim_user, set())
            for item in sim_user_history:
                if item not in history:
                    candidates.add(item)
                    if len(candidates) >= limit * 2:  # Gather slightly larger pool
                        break
            if len(candidates) >= limit * 2:
                break

        return list(candidates)[:limit]

    def content_based_candidates(self, user_id, limit=20):
        """
        Generates candidates based on items similar to the user's past history.
        """
        candidates = set()
        history = self.user_history.get(user_id, set())

        if not history:
            return []

        for item in history:
            for sim_item, _ in self.item_similarities.get(item, []):
                if sim_item not in history:
                    candidates.add(sim_item)
                    if len(candidates) >= limit * 2:
                        break
            if len(candidates) >= limit * 2:
                break

        return list(candidates)[:limit]

    def popularity_candidates(self, limit=20):
        """
        Generates candidates based on overall popularity.
        Useful for cold-start problems (new users with no history).
        """
        item_counts = {}
        for history in self.user_history.values():
            for item in history:
                item_counts[item] = item_counts.get(item, 0) + 1

        sorted_items = sorted(
            item_counts.keys(), key=lambda x: item_counts[x], reverse=True
        )
        return sorted_items[:limit]

    def hybrid_candidates(self, user_id, limit=20):
        """
        Combines multiple generation strategies to ensure a robust candidate pool.
        """
        candidates = set()
        history = self.user_history.get(user_id, set())

        # 1. Try collaborative first
        collab = self.collaborative_candidates(user_id, limit=limit)
        candidates.update(collab)

        # 2. Add content-based if we need more candidates
        if len(candidates) < limit:
            content = self.content_based_candidates(user_id, limit=limit)
            for item in content:
                if item not in candidates:
                    candidates.add(item)
                    if len(candidates) >= limit:
                        break

        # 3. Fallback to popularity (e.g., for cold-start users)
        if len(candidates) < limit:
            pop = self.popularity_candidates(limit=limit)
            for item in pop:
                if item not in history and item not in candidates:
                    candidates.add(item)
                    if len(candidates) >= limit:
                        break

        return list(candidates)[:limit]
