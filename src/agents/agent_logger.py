import json
from src.models.agent_history import AgentHistory, AgentStatus
from src.core.llm import PerplexityLLM
from src.db.mongo import agent_history_collection

llm = PerplexityLLM()


async def analyze_and_store(
    user_message: str,
    agent_response: str,
    user_id: str,
    execution_time: float
):
    """
    Analyze agent response using LLM and store structured history in MongoDB
    """

    system_prompt = """
You are an agent activity analyzer.
Your job is to convert conversations into structured JSON.
Return ONLY valid JSON. No markdown. No explanation.
"""

    user_prompt = f"""
Convert the following interaction into JSON strictly matching this schema:

{{
  "task_name": string,
  "task_description": string,
  "agent_type": string,
  "status": "completed" | "failed",
  "execution_time": number,
  "result_summary": string
}}

User Message:
{user_message}

Agent Response:
{agent_response}
"""

    try:
        llm_response = llm.generate(system_prompt, user_prompt)
        content = llm_response["choices"][0]["message"]["content"].strip()

        parsed = json.loads(content)

        agent_history = AgentHistory(
            task_name=parsed["task_name"],
            task_description=parsed["task_description"],
            agent_type=parsed["agent_type"],
            status=AgentStatus(parsed["status"]),
            execution_time=execution_time,
            result_summary=parsed.get("result_summary"),
            user_id=user_id
        )

        await agent_history_collection.insert_one(agent_history.dict())

    except Exception as e:
        print("Error analyzing/storing agent history:", str(e))