"""
FinanceBot Demo - Master Agent Interface
"""
import gradio as gr
import requests

def chat_with_bot(message):
    """Chat function with Master Agent"""
    try:
        # Call API
        response = requests.post(
            "http://0.0.0.0:8000/chat",
            json={
                "message": message,
                "session_id": "demo",
                "user_id": "demo"
            },
            timeout=10000
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("response", "No response")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        else:
            return f"API Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Create interface
with gr.Blocks(title="FinanceBot - Master Agent") as demo:
    gr.Markdown("""
    # 🤖 FinanceBot Master Agent
    
    **Chào bạn! Tôi là Master Agent của FinanceBot.**
    
    💬 **Trò chuyện thường:** Trả lời ngắn gọn, xúc tích
    🔍 **Phân tích chuyên sâu:** Sử dụng multi-agent system
    
    *Hỏi tôi về tài chính, cổ phiếu, thị trường...*
    """)
    
    chatbot = gr.Chatbot(
        label="💬 Chat with Master Agent",
        height=400,
        avatar_images=("👤", "🤖")
    )
    
    msg = gr.Textbox(
        label="Your Message",
        placeholder="Hỏi tôi về tài chính, cổ phiếu, thị trường...",
        lines=2
    )
    
    with gr.Row():
        send_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear")
    
    gr.Markdown("""
    ### 💡 Ví dụ câu hỏi:
    - **Thường:** "Giá VIC hôm nay?", "Thị trường thế nào?"
    - **Chuyên sâu:** "Phân tích kỹ thuật VIC", "Báo cáo tài chính VCB"
    """)
    
    def chat_fn(message, history):
        if not message.strip():
            return history, ""
        
        # Add user message
        history.append([message, None])
        
        # Get bot response
        response = chat_with_bot(message)
        history[-1][1] = response
        
        return history, ""
    
    msg.submit(chat_fn, [msg, chatbot], [chatbot, msg])
    send_btn.click(chat_fn, [msg, chatbot], [chatbot, msg])
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

