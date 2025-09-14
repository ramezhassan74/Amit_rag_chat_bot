from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="RAG Chatbot API", version="1.0")


class ChatRequest(BaseModel):
    user_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[str] = []

class ChatHistoryItem(BaseModel):
    role: str 
    message: str

chat_histories: Dict[str, List[ChatHistoryItem]] = {}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    history = chat_histories.setdefault(request.user_id, [])
    history.append(ChatHistoryItem(role="user", message=request.query))


    mock_answer = f"ده رد تجريبي على سؤالك: {request.query}"
    mock_citations = ["[1]"]


    history.append(ChatHistoryItem(role="assistant", message=mock_answer))

    return ChatResponse(answer=mock_answer, citations=mock_citations)

@app.get("/chat/history/{user_id}", response_model=List[ChatHistoryItem])
def get_history(user_id: str):
    return chat_histories.get(user_id, [])
