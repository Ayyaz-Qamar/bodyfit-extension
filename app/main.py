from fastapi import FastAPI
from app.routes import upload


app = FastAPI(
    title="BodyFit Extension API",
    description="AI-powered body measurement and shirt size recommendation",
    version="0.2.0"
)


# Include routers
app.include_router(upload.router)


@app.get("/")
def root():
    return {"message": "Hello! BodyFit API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.2.0"}