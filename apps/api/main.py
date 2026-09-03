from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import evidence, graph, analysis, clusters, settings
from db.session import neo4j_driver

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS origins allowed for MVP dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evidence.router, prefix=f"{settings.API_V1_STR}/evidence", tags=["Evidence"])
app.include_router(graph.router, prefix=f"{settings.API_V1_STR}/graph", tags=["Graph Analytics"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Analysis"])
app.include_router(clusters.router, prefix=f"{settings.API_V1_STR}/clusters", tags=["Clusters"])
app.include_router(settings.router, prefix=f"{settings.API_V1_STR}/settings", tags=["Settings"])

@app.on_event("shutdown")
def shutdown_event():
    neo4j_driver.close()

@app.get("/")
def root():
    return {"message": "PRISM API is running."}
