import math


class RecommendationEvaluator:
    @staticmethod
    def precision_at_k(recommendations, relevant_items, k):
        """
        Measures the fraction of top-k recommendations that are actually relevant.
        """
        if not recommendations or not relevant_items or k <= 0:
            return 0.0

        top_k = recommendations[:k]
        relevant_set = set(relevant_items)

        hits = sum(1 for item in top_k if item in relevant_set)
        return hits / len(top_k)

    @staticmethod
    def recall_at_k(recommendations, relevant_items, k):
        """
        Measures the fraction of relevant items that are captured in the top-k recommendations.
        """
        if not recommendations or not relevant_items or k <= 0:
            return 0.0

        top_k = recommendations[:k]
        relevant_set = set(relevant_items)

        hits = sum(1 for item in top_k if item in relevant_set)
        return hits / len(relevant_set)

    @staticmethod
    def ndcg_at_k(recommendations, relevant_items, k):
        """
        Normalized Discounted Cumulative Gain at K.
        Accounts for position in ranking (hits at index 0 are worth more than hits at index k).
        """
        if not recommendations or not relevant_items or k <= 0:
            return 0.0

        top_k = recommendations[:k]
        relevant_set = set(relevant_items)

        dcg = 0.0
        for i, item in enumerate(top_k):
            if item in relevant_set:
                # Rank starts at 1, so index + 1
                # The discount factor is log2(rank + 1)
                dcg += 1.0 / math.log2((i + 1) + 1)

        idcg = 0.0
        # Ideal order would have all relevant items at the top
        for i in range(min(k, len(relevant_set))):
            idcg += 1.0 / math.log2((i + 1) + 1)

        if idcg == 0.0:
            return 0.0

        return dcg / idcg

    @classmethod
    def evaluate_all(cls, recommendations_dict, ground_truth_dict, k=10):
        """
        Calculates average metrics across all users.
        """
        metrics = {"precision": [], "recall": [], "ndcg": []}

        for user_id, recs in recommendations_dict.items():
            if user_id not in ground_truth_dict:
                continue

            truth = ground_truth_dict[user_id]
            if not truth:
                continue  # Skip users with no ground truth data

            metrics["precision"].append(cls.precision_at_k(recs, truth, k))
            metrics["recall"].append(cls.recall_at_k(recs, truth, k))
            metrics["ndcg"].append(cls.ndcg_at_k(recs, truth, k))

        result = {}
        for metric_name, values in metrics.items():
            if values:
                result[f"{metric_name}@{k}"] = sum(values) / len(values)
            else:
                result[f"{metric_name}@{k}"] = 0.0

        return result
