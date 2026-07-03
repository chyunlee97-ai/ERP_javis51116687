from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import query
import uvicorn
import config

app = FastAPI(title="사내 캐릭터 챗봇 API 서버", version="1.0.0")

# Setup CORS (Allow localhost and private network IPs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(query.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.API_PORT, reload=True)
