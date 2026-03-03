"""
This script serves as the main FastAPI application entry point.
It prepares initial app setup — DB creation, role initialization, and router registration.
"""

from app.api.v1.routes import auth, sso, user, masterdata, project, image, ai_integration, dam
from app.utils.exception_handlers import http_exception_handler, global_exception_handler
from app.services.user_masterlist_helper import seed_user_masterlist
from app.services.masterdata_helper import seed_master_data
from starlette.middleware.cors import CORSMiddleware
from app.utils.user_master_role import user_roles
from fastapi import FastAPI, HTTPException

def lifespan(app: FastAPI):
    print("App starting...")
    user_roles()
    seed_master_data()
    seed_user_masterlist()
    yield
    print("App shutting down...")

app = FastAPI(title="Merch Design API", lifespan=lifespan)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(sso.router)
app.include_router(user.router)
app.include_router(masterdata.router)
app.include_router(project.router)
app.include_router(image.router)
app.include_router(ai_integration.router)
app.include_router(dam.router)
