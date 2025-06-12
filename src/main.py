import json
import subprocess
import threading
import time
import webbrowser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.routes import router
from contextlib import asynccontextmanager
import os


app = FastAPI()

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

base_dir = os.path.dirname(__file__)
ui_dir = os.path.abspath(os.path.join(base_dir, "..", "ui"))
out_dir = os.path.join(ui_dir, "out")
app.mount("/", StaticFiles(directory=out_dir, html=True), name="static")
