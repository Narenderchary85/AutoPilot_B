import uvicorn
from fastapi import FastAPI, Depends, UploadFile, File, Form
from pydantic import BaseModel
from src.agents.personal_assistant import PersonalAssistant
from src.routers.auth import router as auth_router
from src.routers.google_oauth import router as google_router
from src.routers.agent_router import router as agent_router
from src.auth.dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from src.agents.agent_logger import analyze_and_store
import time
from src.utils.file_extractor import extract_text_from_file

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = PersonalAssistant()

app.include_router(auth_router)
app.include_router(google_router)
app.include_router(agent_router)

class Query(BaseModel):
    message: str

# @app.post("/chat")
# def chat(data: Query, current_user: str = Depends(get_current_user)):
#     result = assistant.invoke(data.message, user_id=current_user)
#     return {"reply": result}

# @app.post("/chat")
# async def chat(data: Query, current_user: str = Depends(get_current_user)):
#     start = time.time()

#     result = await asyncio.to_thread(
#         assistant.invoke,
#         data.message,
#         user_id=current_user
#     )

#     execution_time = (time.time() - start) * 1000 

#     asyncio.create_task(
#         analyze_and_store(
#             user_message=data.message,
#             agent_response=result,
#             user_id=current_user,
#             execution_time=execution_time
#         )
#     )

#     return {"reply": result}

@app.post("/chat")
async def chat(
    message: str = Form(None),
    file: UploadFile = File(None),
    current_user: str = Depends(get_current_user)
    ):
    start = time.time()

    if file:
        extracted_text = await extract_text_from_file(file)

        final_input = f"""
            User uploaded a file.

            File name: {file.filename}

            File content:
            {extracted_text}
            user message: {message if message else '[No additional message]'}
            """
        user_message_for_logs = f"[FILE] {file.filename}"

    else:
        final_input = message
        user_message_for_logs = message

    result = await asyncio.to_thread(
        assistant.invoke,
        final_input,
        user_id=current_user
    )

    execution_time = (time.time() - start) * 1000

    asyncio.create_task(
        analyze_and_store(
            user_message=user_message_for_logs,
            agent_response=result,
            user_id=current_user,
            execution_time=execution_time
        )
    )

    return {
        "reply": result
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
