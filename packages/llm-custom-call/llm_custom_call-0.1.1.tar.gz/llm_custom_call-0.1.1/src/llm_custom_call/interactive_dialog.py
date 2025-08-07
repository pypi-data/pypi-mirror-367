from llm_custom_call import get_llm
import os
def start_llm_console():
    print("💬 Welcome to the Interactive LLM Console!\n")
    model = input("Enter model name (or press enter if you want to continue with meta-llama/llama-prompt-guard-2-22m): ").strip()
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
 
    llm = get_llm(model=model)
    print("\n✅ LLM is ready! Type your queries. Type `exit` to quit.\n")
    
    while True:
        prompt = input("You: ")
        if prompt.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            break
        response = llm.invoke(prompt)
        print("LLM:", response.content)