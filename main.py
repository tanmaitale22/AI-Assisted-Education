from fastapi import FastAPI
from app.api.routes import router
from app.database.session import init_db

app = FastAPI(title="Memory Importance Scoring API", version="1.0.0")

init_db()
app.include_router(router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Secure Persistent Memory Architecture prototype is running."}
