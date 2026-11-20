from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "gateway service running"}

@app.get("/health")
def health():
    return {"status": "ok"}
