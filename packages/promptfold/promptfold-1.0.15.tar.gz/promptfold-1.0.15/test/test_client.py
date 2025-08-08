import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from promptfold_client import PromptFold

# Add the src directory to Python path for local development
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))


# Load environment variables from .env file
load_dotenv()

PF_API_KEY = os.getenv("PF_API_KEY")
if not PF_API_KEY:
    raise ValueError("PF_API_KEY environment variable is required. Please set it in .env file.")


# Initialize PromptFold client, compress your system prompt
pf_client = PromptFold(api_key=PF_API_KEY, system_prompt="you are a helpful assistant")

# Compress the original user prompt and system prompt
compressed = pf_client.compress_prompt(user_prompt="I want you to tell me about mars")

print(compressed)