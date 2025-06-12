# This file can be used to run the FastAPI app with uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="localhost", port=8000, reload=True)
