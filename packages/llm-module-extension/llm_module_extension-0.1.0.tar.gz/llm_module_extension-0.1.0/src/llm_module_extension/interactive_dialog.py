from llm_module_extension import get_llm
import os
from dotenv import load_dotenv
load_dotenv()
def start_llm_console(prompt:str,model:str="meta-llama/llama-prompt-guard-2-22m"):
    model = model.strip()
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
    llm = get_llm(model)
    response = llm.invoke(prompt)
    return response.content
