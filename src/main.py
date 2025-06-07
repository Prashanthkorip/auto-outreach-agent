import subprocess
import threading
import time
import webbrowser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import router
from contextlib import asynccontextmanager
from src.core.config import PATH_HELPER
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ⏳ STARTUP code here
    base_dir = os.path.dirname(__file__)
    ui_dir = os.path.abspath(os.path.join(base_dir, "..", "ui"))
    out_dir = os.path.join(ui_dir, "out")

    # Build the frontend if needed
    if not os.path.exists(out_dir):
        print("Building Next.js app...")
        subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
        subprocess.run(["npm", "run", "build"], cwd=ui_dir, check=True)

    # Dynamically mount static files after build
    app.mount("/", StaticFiles(directory=out_dir, html=True), name="static")

    PATH_HELPER.initialize_resources()

    # Open the browser in a background thread
    def open_browser():
        time.sleep(1.5)  # Give the server a moment to start
        webbrowser.open("http://localhost:8000")

    threading.Thread(target=open_browser).start()

    yield  # ⛳ Control passes to FastAPI to start handling requests

    # 🔚 SHUTDOWN code here
    print("🧹 Cleaning up resources after FastAPI stops")
    # db.disconnect()
    # cleanup()


app = FastAPI(lifespan=lifespan)

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
# Serve Next.js static output
static_dir = os.path.join(PATH_HELPER.BASE_DIR, "ui", "out")
