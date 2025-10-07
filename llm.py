import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------------------------------------
# GOOGLE LLM SETUP
# ----------------------------------------------------------------------
try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None
    genai = None

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_google_llm(model_name: str = "gemini-2.5-flash-preview-05-20", **kwargs):
    """Return a Google Gemini LLM (via LangChain)."""
    if not genai or not ChatGoogleGenerativeAI:
        raise ImportError("Please install google-generativeai and langchain-google-genai.")
    genai.configure(api_key=GOOGLE_API_KEY)
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=GOOGLE_API_KEY, **kwargs)


# ----------------------------------------------------------------------
# OPENROUTER LLM SETUP
# ----------------------------------------------------------------------
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_openrouter_llm(model_name: str = "deepseek/deepseek-chat-v3.1:free", **kwargs):
    """Return an OpenRouter LLM (via LangChain)."""
    if not ChatOpenAI:
        raise ImportError("Please install langchain-openai.")
    return ChatOpenAI(
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        model_name=model_name,
        **kwargs,
    )


# ----------------------------------------------------------------------
# UNIFIED ACCESS POINT
# ----------------------------------------------------------------------
def get_llm(provider: str = "google", model_name: str | None = None, **kwargs):
    """
    Get an LLM instance by provider and optional model.
    
    Args:
        provider: "google" | "openrouter"
        model_name: optional, overrides the default model for the provider
        **kwargs: additional arguments to pass to the LLM constructor
    """
    provider = provider.lower()
    
    if provider == "google":
        if model_name is None:
            model_name = "gemini-2.5-flash-preview-05-20"  # default Google model
        return get_google_llm(model_name=model_name, **kwargs)
    
    elif provider == "openrouter":
        if model_name is None:
            model_name = "deepseek/deepseek-chat-v3.1:free"  # default OpenRouter model
        return get_openrouter_llm(model_name=model_name, **kwargs)
    
    else:
        raise ValueError("Provider must be 'google' or 'openrouter'.")


# ----------------------------------------------------------------------
# DEFAULT INSTANCE 
# ----------------------------------------------------------------------
llm = get_llm(provider="google")  # default Google model
# or llm = get_llm(provider="openrouter", model_name="deepseek-chat-v3.0:free")


"""
# To check available models for Google Gemini:
import google.generativeai as genai
GOOGLE_API_KEY = "your_api_key_here"
genai.configure(api_key=GOOGLE_API_KEY)
for m in genai.list_models():
    print(m.name)
"""
