from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import upload, pose, measurements, recommendation


app = FastAPI(
    title="BodyFit Extension API",
    description="AI-powered body measurement and shirt size recommendation",
    version="0.5.0"
)


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(upload.router)
app.include_router(pose.router)
app.include_router(measurements.router)
app.include_router(recommendation.router)


@app.get("/")
def root():
    return {"message": "Hello! BodyFit API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.5.0"}