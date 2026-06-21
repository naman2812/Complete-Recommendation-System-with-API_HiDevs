# Capstone Project: Complete Recommendation System

This project is a production-ready recommendation system microservice. It wraps the Day 29 recommendation components in a FastAPI application, backed by a SQLite database with SQLAlchemy ORM.

## Features
- **REST API** built with FastAPI
- **Data Layer** using SQLite and SQLAlchemy
- **Recommendation Engine** integrating Candidate Generation, Scoring, and Similarity Calculation
- **Caching Layer** to handle repeat queries efficiently
- **Cold Start Handling** for new users
- **Comprehensive Testing** with pytest (Data, Engine, API layers)
- **Evaluation Scripts** for generating Precision, Recall, and NDCG metrics
- **Load Testing Scripts** to ensure performance < 200ms

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Seed the Database**
   This will create sample users, content, and simulated interaction history.
   ```bash
   python scripts/seed_data.py
   ```

3. **Run the API Server**
   ```bash
   uvicorn api.app:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`. You can access the interactive Swagger UI at `http://127.0.0.1:8000/docs`.
   🚨 IMPORTANT: HOW TO VIEW THE PROJECT 🚨 The API will start running at http://127.0.0.1:8000, but this root URL will return a "Not Found" error because APIs don't have homepages.

  To view and interact with the project:

  Open the interactive UI at http://127.0.0.1:8000/docs
  Click the green Authorize button at the top right.
  Enter the security key: capstone-auth-key-2026
  You can now test the endpoints!

## Evaluation & Load Testing

- **Evaluate Metrics**: Calculate Precision@5, Recall@5, and NDCG@5.
  ```bash
  python scripts/evaluate.py
  ```

- **Load Testing**: Simulate concurrent users. Make sure the API is running first!
  ```bash
  python scripts/load_test.py
  ```

- **Run Unit Tests**:
  ```bash
  python -m pytest tests/
  ```

## API Endpoints

- `GET /health` : Health check.
- `GET /metrics` : System performance metrics.
- `GET /recommend/{user_id}?limit=5` : Get top `limit` recommendations for a user.
- `POST /feedback` : Record user interaction with an item.

## Project Structure
- `api/` : FastAPI routes and application.
- `data/` : SQLAlchemy models and repository classes.
- `engine/` : Recommendation logic (candidate generation, similarity, scoring, orchestrator).
- `scripts/` : Utility scripts for seeding, load testing, and evaluating.
- `tests/` : Pytest test suite.
