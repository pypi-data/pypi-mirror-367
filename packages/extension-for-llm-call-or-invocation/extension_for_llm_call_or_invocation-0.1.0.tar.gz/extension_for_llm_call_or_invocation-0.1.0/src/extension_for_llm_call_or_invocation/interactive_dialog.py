from extension_for_llm_call_or_invocation import get_llm
import os
from dotenv import load_dotenv
load_dotenv()
def start_llm_console():
    print("💬 Welcome to the Interactive LLM Console!\n")
    model = input("Enter model name (or press enter if you want to continue with default model): ").strip()
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
    if model=="":
        llm=get_llm("meta-llama/llama-prompt-guard-2-22m")
    else:
        llm = get_llm(model)
    print("\n✅ LLM is ready! Type your queries. Type `exit` to quit.\n")
    
    while True:
        prompt = input("You: ")
        if prompt.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            break
        print(prompt)
        response = llm.invoke(prompt)
        print("LLM:", response.content)
