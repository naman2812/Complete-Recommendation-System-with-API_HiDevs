import math

class SimilarityCalculator:
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Calculates cosine similarity between two vectors.
        Handles both dictionary (sparse) and list (dense) representations.
        """
        if not vec1 or not vec2:
            return 0.0
        
        if isinstance(vec1, dict) and isinstance(vec2, dict):
            intersection = set(vec1.keys()) & set(vec2.keys())
            dot_product = sum(vec1[k] * vec2[k] for k in intersection)
            mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
            mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
        else: # lists or tuples
            if len(vec1) != len(vec2):
                raise ValueError("Vectors must be of same length for list inputs")
            dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
            mag1 = math.sqrt(sum(v**2 for v in vec1))
            mag2 = math.sqrt(sum(v**2 for v in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    @staticmethod
    def jaccard_similarity(set1, set2):
        """
        Calculates Jaccard similarity between two sets.
        Good for comparing tags or skill sets.
        """
        if not set1 and not set2:
            return 1.0 # Both empty means they are identical
        if not set1 or not set2:
            return 0.0
            
        s1, s2 = set(set1), set(set2)
        intersection = len(s1.intersection(s2))
        union = len(s1.union(s2))
        
        if union == 0:
            return 0.0
            
        return intersection / union

    @staticmethod
    def pearson_correlation(ratings1, ratings2):
        """
        Calculates Pearson correlation between two rating patterns.
        Handles both dictionaries of ratings or lists of ratings.
        """
        if not ratings1 or not ratings2:
            return 0.0
            
        if isinstance(ratings1, dict) and isinstance(ratings2, dict):
            common_items = set(ratings1.keys()) & set(ratings2.keys())
            if not common_items:
                return 0.0
                
            n = len(common_items)
            
            sum1 = sum(ratings1[i] for i in common_items)
            sum2 = sum(ratings2[i] for i in common_items)
            
            sum1_sq = sum(ratings1[i]**2 for i in common_items)
            sum2_sq = sum(ratings2[i]**2 for i in common_items)
            
            p_sum = sum(ratings1[i] * ratings2[i] for i in common_items)
        else:
            if len(ratings1) != len(ratings2):
                raise ValueError("Ratings lists must be of same length")
            n = len(ratings1)
            if n == 0:
                return 0.0
                
            sum1 = sum(ratings1)
            sum2 = sum(ratings2)
            
            sum1_sq = sum(r**2 for r in ratings1)
            sum2_sq = sum(r**2 for r in ratings2)
            
            p_sum = sum(r1 * r2 for r1, r2 in zip(ratings1, ratings2))
            
        num = p_sum - (sum1 * sum2 / n)
        den = math.sqrt((sum1_sq - sum1**2 / n) * (sum2_sq - sum2**2 / n))
        
        if den == 0:
            return 0.0
            
        # Ensure result is between -1 and 1 (avoiding float precision issues)
        return max(min(num / den, 1.0), -1.0)
