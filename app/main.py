from fastapi import FastAPI

# FastAPI app banaya
app = FastAPI(title="BodyFit Extension API")

# Root route - jab koi "/" pe aaye to ye response
@app.get("/")
def root():
    return {"message": "Hello! BodyFit API is running 🚀"}

# Health check route - jab koi "/health" pe aaye
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}