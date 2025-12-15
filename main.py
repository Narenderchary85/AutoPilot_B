import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.agents.personal_assistant import PersonalAssistant

app = FastAPI()
assistant = PersonalAssistant()

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(data: Query):
    result = assistant.invoke(data.message)
    return {"reply": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
