from fastapi import FastAPI
from app.routes.auth import router as auth_router

app = FastAPI(title="IAARE Authentication & Risk Engine")

app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Intelligent Adaptive Authentication & Risk Assessment Engine Running"
    }