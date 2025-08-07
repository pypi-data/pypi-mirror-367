from langchain_groq import ChatGroq
def get_llm( model, api_key=None, **kwargs):
    return ChatGroq(model_name=model, api_key=api_key, **kwargs)