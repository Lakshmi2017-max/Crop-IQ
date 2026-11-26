"""FastAPI application entry point and routes for CropIQ."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.recommender import CropRecommender
from app.schemas import RecommendRequest, RecommendResponse

# Holds initialized recommender state loaded at startup.
app_state: dict[str, CropRecommender] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load models, crop profiles, and dataset bounds once on startup."""
    app_state["recommender"] = CropRecommender()
    yield
    app_state.clear()


app = FastAPI(title="CropIQ API", version="0.1.0", lifespan=lifespan)

# Allow the Vite React frontend on localhost:5173 (and 127.0.0.1:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_recommender() -> CropRecommender:
    """Return the loaded CropRecommender, initializing lazily if needed in tests."""
    if "recommender" not in app_state:
        app_state["recommender"] = CropRecommender()
    return app_state["recommender"]


@app.get("/")
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "CropIQ API running"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest) -> RecommendResponse:
    """Validate inputs, select the appropriate soil-mode model, and return top 3 crops."""
    recommender = get_recommender()
    validation_errors = recommender.validate_inputs(req)
    if validation_errors:
        raise HTTPException(status_code=422, detail=validation_errors)

    result = recommender.recommend(req)
    return RecommendResponse(**result)
