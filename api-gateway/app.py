import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

SERVICES = {
    "products": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001"),
    "orders": os.getenv("ORDER_SERVICE_URL", "http://localhost:8002"),
    "users": os.getenv("USER_SERVICE_URL", "http://localhost:8003"),
}

app = FastAPI(title="E-commerce API Gateway", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    statuses = {}
    async with httpx.AsyncClient(timeout=3) as client:
        for name, url in SERVICES.items():
            try:
                statuses[name] = (await client.get(f"{url}/health")).json()["status"]
            except Exception:
                statuses[name] = "unhealthy"
    overall = "healthy" if all(value == "healthy" for value in statuses.values()) else "degraded"
    return {"status": overall, "service": "api-gateway", "dependencies": statuses}

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return Response(content='{"detail":"Unknown service"}', status_code=404, media_type="application/json")
    url = f"{SERVICES[service]}/{service}/{path}".rstrip("/")
    headers = {key: value for key, value in request.headers.items() if key.lower() not in {"host", "content-length"}}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            upstream = await client.request(request.method, url, params=request.query_params, content=await request.body(), headers=headers)
            return Response(content=upstream.content, status_code=upstream.status_code, headers={"content-type": upstream.headers.get("content-type", "application/json")})
        except httpx.RequestError:
            return Response(content='{"detail":"Upstream service unavailable"}', status_code=503, media_type="application/json")

