from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import os
from pydantic import BaseModel, Field, field_validator
from postgrest.exceptions import APIError
from datetime import datetime, timezone

app = FastAPI()
    
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
    

