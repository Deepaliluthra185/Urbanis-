"""LLM helper for THOT / IRIS / LYRA agents via Emergent Universal Key (Gemini 3.1 Pro)."""
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

MODEL_PROVIDER = "gemini"
MODEL_NAME = "gemini-3.1-pro-preview"


async def llm_generate(system_message: str, prompt: str, session_id: str) -> str:
    chat = LlmChat(
        api_key=os.environ["EMERGENT_LLM_KEY"],
        session_id=session_id,
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)
    resp = await chat.send_message(UserMessage(text=prompt))
    if isinstance(resp, str):
        return resp
    return getattr(resp, "content", str(resp))
