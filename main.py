from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import os
from pydantic import BaseModel, Field, field_validator
from postgrest.exceptions import APIError
from datetime import datetime, timezone

app = FastAPI()

class LocalizationCreate(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=20)
    locale: str = Field(..., min_length=1, max_length=20)
    key: str = Field(..., min_length=1, max_length=20)
    value: str = Field(..., min_length=1, max_length=20)
    updated_by: str = Field(..., min_length=1, max_length=20)

    @field_validator("project_id", "locale", "key", "value", "updated_by")
    @classmethod
    def not_empty(cls, v: str, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} must not be empty")
        return v
    
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
@app.get("/localizations/{project_id}/{locale}")
async def get_localizations(project_id: str, locale: str):
    try:
        response = (
            supabase.table("translations")
            .select("*")
            .eq("project_id", project_id)
            .eq("locale", locale)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No translations found")

        return {
            "project_id": project_id,
            "locale": locale,
            "localizations": response.data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/localizations")
async def create_localization(item: LocalizationCreate):
    
    item.value = item.value.strip()
    item.key = item.key.strip()
    item.locale = item.locale.strip()
    item.project_id = item.project_id.strip()
    item.updated_by = item.updated_by.strip()

    if item.value.isalnum()== False or not item.value:
        raise HTTPException(
                status_code=400,
                detail=f"value must be a non-empty alphanumeric string"
            )
    
    now = datetime.now(timezone.utc).isoformat()

    # Check if record exists
    existing = supabase.table("translations")\
        .select("id")\
        .eq("project_id", item.project_id)\
        .eq("locale", item.locale)\
        .eq("key", item.key)\
        .execute()

    if existing.data:
        # UPDATE
        response = supabase.table("translations")\
            .update({
                "value": item.value,
                "updated_by": item.updated_by,
                "updated_at": now
            })\
            .eq("project_id", item.project_id)\
            .eq("locale", item.locale)\
            .eq("key", item.key)\
            .execute()
        message = "Localization updated"
    else:
        # INSERT
        response = supabase.table("translations")\
            .insert({
                "project_id": item.project_id,
                "locale": item.locale,
                "key": item.key,
                "value": item.value,
                "updated_by": item.updated_by,
                "updated_at": now
            })\
            .execute()
        message = "Localization created"

    return {"message": message, "result": response.data}