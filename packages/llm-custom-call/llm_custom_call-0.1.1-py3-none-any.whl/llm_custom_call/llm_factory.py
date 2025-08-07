from langchain_groq import ChatGroq
def get_llm( model_name="meta-llama/llama-prompt-guard-2-22m", **kwargs):
    return ChatGroq(model=model_name,temperature=0)