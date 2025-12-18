import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.agents.personal_assistant import PersonalAssistant
from src.routers.auth import router as auth_router
from src.routers.google_oauth import router as google_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
assistant = PersonalAssistant()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(google_router)

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(data: Query):
    result = assistant.invoke(data.message)
    return {"reply": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
