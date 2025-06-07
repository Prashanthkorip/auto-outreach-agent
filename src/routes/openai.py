from fastapi import APIRouter, Request, HTTPException
import os
import json
from json import JSONDecodeError
from src.core.config import PATH_HELPER

router = APIRouter()


@router.get("/get-openai-key")
async def get_openai_key():
    openai_key_path = PATH_HELPER.OPENAI_API_JSON
    if not os.path.isfile(openai_key_path):
        return {"OPENAI_API_KEY": ""}
    with open(openai_key_path, "r") as f:
        try:
            data = json.load(f)
            key = data.get("OPENAI_API_KEY")
        except (JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=500, detail="Invalid OPENAI_API_KEY file format"
            )
    return {"OPENAI_API_KEY": key}


@router.put("/put-openai-key")
async def put_openai_key(request: Request):
    data = await request.json()
    key = data.get("OPENAI_API_KEY")
    if not key:
        raise HTTPException(
            status_code=400, detail="Missing 'OPENAI_API_KEY' in request body"
        )
    openai_key_path = PATH_HELPER.OPENAI_API_JSON
    if not os.path.isfile(openai_key_path):
        with open(openai_key_path, "w") as f:
            json.dump({"OPENAI_API_KEY": key, "OPENAI_MODEL": "gpt-4o-mini"}, f)
    else:
        with open(openai_key_path, "r") as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                data = {}
        data["OPENAI_API_KEY"] = key
        with open(openai_key_path, "w") as f:
            json.dump(data, f, indent=2)
    return {"message": "OPENAI_API_KEY updated successfully"}
