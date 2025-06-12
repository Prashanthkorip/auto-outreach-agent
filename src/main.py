from src.core.config import PATH_HELPER

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


def get_package_version(package_json_path):
    with open(package_json_path, "r") as f:
        return json.load(f).get("version")


def get_build_version(version_file_path):
    if not os.path.exists(version_file_path):
        return None
    with open(version_file_path, "r") as f:
        return f.read().strip()


def versions_differ(ui_dir):
    out_dir = os.path.join(ui_dir, "out")
    package_json = os.path.join(ui_dir, "package.json")
    build_version_file = os.path.join(out_dir, "version.txt")

    pkg_version = get_package_version(package_json)
    build_version = get_build_version(build_version_file)

    return pkg_version != build_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ⏳ STARTUP code here
    base_dir = os.path.dirname(__file__)
    ui_dir = os.path.abspath(os.path.join(base_dir, "..", "ui"))
    out_dir = os.path.join(ui_dir, "out")

    # Build the frontend if needed
    if not os.path.exists(out_dir) or versions_differ(ui_dir):
        print("Building Next.js app...")
        subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
        subprocess.run(["npm", "run", "build-stable"], cwd=ui_dir, check=True)

    # Dynamically mount static files after build
    app.mount("/", StaticFiles(directory=out_dir, html=True), name="static")

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
