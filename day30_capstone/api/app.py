import time
import uuid
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import engine, Base, get_db
from engine.orchestrator import RecommendationOrchestrator
from database.repositories import UserRepository

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recommendation System API (Enterprise Edition)", version="2.0.0")

# Security
API_KEY = "capstone-auth-key-2026"
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=401, detail="Unauthorized - invalid or missing API key"
    )

# Request/Response Models
class FeedbackRequest(BaseModel):
    user_id: int
    content_id: int
    interaction_type: str
    rating: Optional[float] = None

class RecommendationResponse(BaseModel):
    id: int
    title: str
    category: str
    score: float
    explanation: str
    breakdown: dict
    strategy: str

# Metrics state
app.state.metrics = {
    "total_requests": 0,
    "total_recommendations": 0,
    "total_feedback": 0,
    "errors": 0,
    "average_latency_ms": 0.0
}

@app.middleware("http")
async def add_process_time_and_tracing(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    duration_ms = round(process_time * 1000, 2)
    
    # Update metrics safely
    app.state.metrics["total_requests"] += 1
    n = app.state.metrics["total_requests"]
    current_avg = app.state.metrics["average_latency_ms"]
    app.state.metrics["average_latency_ms"] = ((current_avg * (n - 1)) + duration_ms) / n
    
    response.headers["X-Process-Time-ms"] = str(duration_ms)
    response.headers["X-Request-ID"] = request_id
    
    logger.info(f"[{request_id}] -> {response.status_code} in {duration_ms}ms")
    return response

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/metrics", dependencies=[Depends(get_api_key)])
def get_metrics():
    return app.state.metrics

@app.get("/recommend/{user_id}", response_model=List[RecommendationResponse], dependencies=[Depends(get_api_key)])
def get_recommendations(
    user_id: int, 
    limit: int = 5, 
    strategy: str = "hybrid",
    refresh: bool = False,
    db: Session = Depends(get_db)
):
    valid_strategies = {"collaborative", "content", "popular", "hybrid"}
    if strategy not in valid_strategies:
        raise HTTPException(status_code=400, detail=f"'strategy' must be one of {sorted(valid_strategies)}")

    user_repo = UserRepository(db)
    user = user_repo.get_user(user_id)
    if not user:
        app.state.metrics["errors"] += 1
        raise HTTPException(status_code=404, detail="User not found")

    try:
        orchestrator = RecommendationOrchestrator(db)
        recs = orchestrator.get_recommendations(user_id, limit=limit, strategy=strategy, refresh=refresh)
        app.state.metrics["total_recommendations"] += 1
        return recs
    except Exception as e:
        logger.exception(f"Error generating recommendations for user {user_id}: {e}")
        app.state.metrics["errors"] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", dependencies=[Depends(get_api_key)])
def record_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        orchestrator = RecommendationOrchestrator(db)
        orchestrator.record_feedback(
            user_id=feedback.user_id,
            content_id=feedback.content_id,
            interaction_type=feedback.interaction_type,
            rating=feedback.rating
        )
        app.state.metrics["total_feedback"] += 1
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.exception(f"Error recording feedback: {e}")
        app.state.metrics["errors"] += 1
        raise HTTPException(status_code=400, detail=str(e))
