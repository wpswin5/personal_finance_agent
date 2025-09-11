from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingest, classify, anomalies, insights, chat, user

app = FastAPI(title="Personal Finance Agent")

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # frontend URLs allowed
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, OPTIONS, etc.
    allow_headers=["*"],         # Authorization, Content-Type, etc.
)

# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["Anomalies"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(user.router, prefix="/auth", tags=["Auth"])