from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

def create_gemini_llm(
    api_key: str,
    model_name: str = "gemini-1.5-flash",
    temperature: float = 0.7,
    top_p: float = 0.95,
    top_k: int = 40,
    max_output_tokens: Optional[int] = None
):
    """
    Create a Gemini LLM instance with specified parameters
    """
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=model_name,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_output_tokens=max_output_tokens,
        # Remove the deprecated parameter
        convert_system_message_to_human=False
    )