from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from src.database.connection import get_db_session
import pandas as pd

app = FastAPI(title="Medical Data API")

@app.get("/api/v1/products/top")
def get_top_products(limit: int = 10, session: Session = Depends(get_db_session)):
    """
    Fetch top products from the dbt-transformed Mart.
    """
    # Query your dbt-created fct_medical_mentions table
    query = f"""
        SELECT entity_name, entity_type, mention_count, total_reached_views
        FROM public.fct_medical_mentions
        ORDER BY mention_count DESC
        LIMIT {limit}
    """
    df = pd.read_sql(query, session.bind)
    return df.to_dict(orient="records")

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "version": "2.0"}