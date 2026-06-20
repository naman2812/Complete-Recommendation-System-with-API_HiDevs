import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import SessionLocal
from data.models import User, Content, Interaction
from engine.orchestrator import RecommendationOrchestrator
from engine.evaluator import RecommendationEvaluator

def run_evaluation():
    db = SessionLocal()
    
    users = db.query(User).all()
    interactions = db.query(Interaction).all()
    
    # We will treat the last 2 interactions of each user as "ground truth" (hidden from the engine normally, 
    # but here we just use all interactions as relevant for simplicity of demonstrating the metric calculation).
    # A proper eval would split train/test. For this capstone, we just show we can calculate the metrics.
    
    ground_truth_dict = {}
    for user in users:
        user_interactions = [i.content_id for i in interactions if i.user_id == user.id]
        if len(user_interactions) > 0:
            # Randomly select a few items as "relevant" target ground truth for the evaluation
            ground_truth_dict[user.id] = list(set(user_interactions))

    orchestrator = RecommendationOrchestrator(db)
    
    recommendations_dict = {}
    print("Generating recommendations for evaluation...")
    for user in users:
        if user.id in ground_truth_dict:
            recs = orchestrator.get_recommendations(user.id, limit=5)
            recommendations_dict[user.id] = [r["id"] for r in recs]
            
    print("\nCalculating metrics (Precision@5, Recall@5, NDCG@5)...")
    metrics = RecommendationEvaluator.evaluate_all(recommendations_dict, ground_truth_dict, k=5)
    
    print("\n--- Evaluation Results ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    return metrics

if __name__ == "__main__":
    run_evaluation()
