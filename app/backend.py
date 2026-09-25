from fastapi import FastAPI
app = FastAPI(title="Demo Upstream Service")

@app.get("/health")
def health():
    return {"status":"ok","service":"backend"}

@app.get("/orders")
def orders():
    return {"orders":[{"id":"ord-100","status":"created"},{"id":"ord-101","status":"processing"}]}
