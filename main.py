import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Project, Meme

app = FastAPI(title="Meme Generator Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert ObjectId to string recursively

def serialize_doc(doc):
    if not doc:
        return doc
    out = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out

@app.get("/")
def read_root():
    return {"message": "Meme Generator Marketplace API"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Projects endpoints
@app.post("/api/projects", response_model=dict)
def create_project(project: Project):
    project_id = create_document("project", project)
    return {"id": project_id}

@app.get("/api/projects", response_model=List[dict])
def list_projects(limit: Optional[int] = 50):
    docs = get_documents("project", {}, limit)
    return [serialize_doc(d) for d in docs]

# Memes endpoints
@app.post("/api/memes", response_model=dict)
def create_meme(meme: Meme):
    # Validate project exists
    try:
        pid = ObjectId(meme.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")
    project = db["project"].find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meme_id = create_document("meme", meme)
    return {"id": meme_id}

@app.get("/api/memes", response_model=List[dict])
def list_memes(project_id: Optional[str] = None, limit: Optional[int] = 50):
    query = {}
    if project_id:
        try:
            query["project_id"] = project_id
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    docs = get_documents("meme", query, limit)
    return [serialize_doc(d) for d in docs]

# Simple action: upvote and reward tokens (demo only)
class UpvotePayload(BaseModel):
    meme_id: str

@app.post("/api/memes/upvote", response_model=dict)
def upvote_meme(payload: UpvotePayload):
    try:
        mid = ObjectId(payload.meme_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid meme id")

    meme = db["meme"].find_one({"_id": mid})
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    new_values = {
        "$inc": {"upvotes": 1, "tokens_earned": 1}
    }
    db["meme"].update_one({"_id": mid}, new_values)
    updated = db["meme"].find_one({"_id": mid})
    return serialize_doc(updated)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
