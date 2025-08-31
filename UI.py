# ui.py
import gradio as gr
from APP import gemini_chat_wrapper   # استدعاء الفنكشن من backend

# واجهة Gradio
demo = gr.ChatInterface(
    fn=gemini_chat_wrapper,
    title="AMIT RAG Chatbot 🤖",
    description="Ask me anything from the local documents. I'm powered by AMIT RAG Chatbot 🤖",
)

if __name__ == "__main__":
    demo.launch(share=True)  # share=True لو عايز لينك خارجي

