from fastapi import FastAPI

app = FastAPI(title="Tourist Safety System")


@app.get("/")
def home():
    return {
        "message": "Tourist Safety System API is running"
    }