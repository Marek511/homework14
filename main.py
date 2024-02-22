"""
Module defining the FastAPI application and its configuration.
"""

from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from src.routes import router_endpoints, router_contacts, auth

app = FastAPI()

# Include routers from different modules
app.include_router(router_endpoints.router, prefix="/contacts")
app.include_router(router_contacts.router, prefix="/contacts")
app.include_router(auth.router, prefix="")

# CORS middleware configuration
origins = ["http://localhost:8000", "https://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint to welcome users to the API.

    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"message": "Welcome to the API!"}


if __name__ == '__main__':
    # Run the application using uvicorn
    uvicorn.run(app, host='localhost', port=8000)
