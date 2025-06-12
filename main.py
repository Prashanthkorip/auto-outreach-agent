# main.py
import subprocess
import os
import signal
import time

# Ensure dependencies are installed
if not os.path.exists(os.path.join("ui", "node_modules")):
    subprocess.run(["npm", "install"], cwd="ui", check=True)

# Start Next.js dev server (live logs to terminal)
next_process = subprocess.Popen(["npm", "run", "dev"], cwd="ui", preexec_fn=os.setsid)

# Start FastAPI server with uvicorn (live logs to terminal)
fastapi_process = subprocess.Popen(
    ["uvicorn", "src.main:app", "--host", "localhost", "--port", "8000", "--reload"],
    preexec_fn=os.setsid,
)

print("✅ Both FastAPI (8000) and Next.js (3000) are running... Press Ctrl+C to stop.")

try:
    # Wait for both to finish (e.g., if one exits unexpectedly)
    fastapi_process.wait()
    next_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down both servers...")

    # Send termination signals
    os.killpg(os.getpgid(next_process.pid), signal.SIGTERM)
    os.killpg(os.getpgid(fastapi_process.pid), signal.SIGTERM)

    # Wait for both to shut down cleanly
    fastapi_process.wait()
    next_process.wait()

    print("✅ Cleanup complete. Exiting.")
