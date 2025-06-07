from fastapi import APIRouter, Request, HTTPException
import os
import json
from json import JSONDecodeError
from src.core.config import PATH_HELPER

router = APIRouter()


@router.get("/get-credentials")
async def get_credentials():
    credentials_path = PATH_HELPER.CREDENTIALS_JSON
    if not os.path.isfile(credentials_path):
        return {"credentials": {}}
    with open(credentials_path, "r") as f:
        try:
            credentials = json.load(f)
        except JSONDecodeError:
            raise HTTPException(
                status_code=500, detail="Invalid credentials.json format"
            )
    return {"credentials": credentials}


@router.put("/put-credentials")
async def put_credentials(request: Request):
    data = await request.json()
    credentials = data.get("credentials")
    if not credentials:
        raise HTTPException(
            status_code=400, detail="Missing 'credentials' in request body"
        )
    if not isinstance(credentials, dict):
        raise HTTPException(
            status_code=400, detail="'credentials' must be a JSON object"
        )
    credentials_path = PATH_HELPER.CREDENTIALS_JSON
    with open(credentials_path, "w") as f:
        json.dump(credentials, f, indent=2)
    return {"message": "credentials.json updated successfully"}
