from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import upload, pose, measurements


app = FastAPI(
    title="BodyFit Extension API",
    description="AI-powered body measurement and shirt size recommendation",
    version="0.4.0"
)


# Mount uploads folder as static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Include routers
app.include_router(upload.router)
app.include_router(pose.router)
app.include_router(measurements.router)


@app.get("/")
def root():
    return {"message": "Hello! BodyFit API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.4.0"}