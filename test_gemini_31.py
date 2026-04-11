import os
from dotenv import load_dotenv
from v2.api_adapters import UnifiedLLMClient
from v2.config import LLMProvider

load_dotenv(".env")
provider = LLMProvider(
    name="Gemini Test",
    model_id="gemini-3.1-pro-preview",
    api_type="google",
    api_key_env="GOOGLE_API_KEY"
)
print(f"Testing {provider.model_id}...")
client = UnifiedLLMClient(provider)
try:
    res = client.generate("You are an AI.", "Ping?", tools=[], max_tool_calls=0)
    print("SUCCESS")
    print(res)
except Exception as e:
    print("FAILED")
    print(str(e))
