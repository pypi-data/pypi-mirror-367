from llm_custom_call import get_llm
 
def start_llm_console():
    print("💬 Welcome to the Interactive LLM Console!\n")
    model = input("Enter model name (e.g., gpt-4 / llama3-8b-8192): ").strip()
    api_key = input(f"Enter API key for Groq ").strip()
 
    llm = get_llm(model=model, api_key=api_key)
    print("\n✅ LLM is ready! Type your queries. Type `exit` to quit.\n")
    
    while True:
        prompt = input("You: ")
        if prompt.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            break
        response = llm.invoke(prompt)
        print("LLM:", response.content)