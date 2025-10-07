from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingest, classify, insights, chat, user, plaid, accounts, households

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
app.include_router(households.router, prefix="/households", tags=["Households"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(plaid.router, prefix="/plaid", tags=["Plaid"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])