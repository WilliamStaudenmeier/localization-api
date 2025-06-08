# localization-api
This is the api for Supabase.  Endpoint is live on Render.

Simple GET:

```curl "https://localization-api-0fci.onrender.com/localizations/helium-us/en"```

Simple Post:

```curl -X POST "https://localization-api.onrender.com/localizations" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "helium-us",
    "locale": "en",
    "key": "button.submit",
    "value": "Submit",
    "updated_by": "nida"
}' ```

