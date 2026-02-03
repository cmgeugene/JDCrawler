from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This will look in the current directory and also parent directories (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv() # Fallback to local .env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jdcrawler.api.analysis import router as analysis_router
from jdcrawler.api.crawl import router as crawl_router
from jdcrawler.api.jobs import router as jobs_router
from jdcrawler.api.keywords import router as keywords_router
from jdcrawler.api.notifications import router as notifications_router
from jdcrawler.api.profile import router as profile_router
from jdcrawler.db.client import DatabaseClient
from jdcrawler.scheduler import scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Initialize DB
    db = DatabaseClient()
    db.create_tables()
    app.state.db = db
    
    # Start Scheduler
    start_scheduler()
    
    yield
    
    # Cleanup
    if scheduler.running:
        scheduler.shutdown()
    db.close()


app = FastAPI(title="JDCrawler API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(keywords_router)
app.include_router(notifications_router)
app.include_router(crawl_router)
app.include_router(analysis_router)
app.include_router(profile_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
