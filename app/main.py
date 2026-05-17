from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import upload, pose, measurements, recommendation


app = FastAPI(
    title="BodyFit Extension API",
    description="AI-powered body measurement and shirt size recommendation",
    version="0.6.0"
)


# CORS Configuration - Allow Chrome extension to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein specific extension ID rakhenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount uploads folder as static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Include routers
app.include_router(upload.router)
app.include_router(pose.router)
app.include_router(measurements.router)
app.include_router(recommendation.router)


@app.get("/")
def root():
    return {"message": "Hello! BodyFit API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.6.0"}