from fastapi import FastAPI
from app.routers import ingest, classify, anomalies, insights, chat, auth

app = FastAPI(title="Personal Finance Agent")

# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["Anomalies"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])