import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.agents.personal_assistant import PersonalAssistant
from src.routers.auth import router as auth_router
from src.routers.google_oauth import router as google_router

app = FastAPI()
assistant = PersonalAssistant()

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
