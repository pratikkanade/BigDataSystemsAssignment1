from fastapi import FastAPI
from backend_fastapi.routes import upload, fetch

# Create FastAPI app instance
app = FastAPI(
    title="PDF Parser API",
    description="An API to upload PDFs, parse their content, and fetch parsed Markdown files from S3.",
    version="1.0.0",
)

# Include your route modules
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(fetch.router, prefix="/fetch", tags=["Fetch"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Parser API! Use the /upload and /fetch endpoints."}
