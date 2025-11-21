from fastapi import FastAPI, Request, Response
import time, logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
logging.basicConfig(level=logging.INFO)
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["method","path"])
app = FastAPI(title="Article Eater Service")
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    try: REQUESTS.labels(request.method, request.url.path).inc()
    except Exception: pass
    return response
@app.get("/healthz")
async def healthz(): return {"status": "ok"}
@app.get("/metrics")
async def metrics(): return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)