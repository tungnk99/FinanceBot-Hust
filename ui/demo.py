"""
FinanceBot Demo - Master Agent Interface
"""
import gradio as gr
import requests
import logging
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# Setup logging
log_dir = Path(__file__).parent
log_file = log_dir / 'demo.log'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_avatar_icon(icon_type: str, size: int = 64, bg_color: str = "#E3F2FD") -> Path:
    """Create a simple avatar icon"""
    icon_dir = log_dir / "icons"
    icon_dir.mkdir(exist_ok=True)
    
    # Create filename
    icon_path = icon_dir / f"{icon_type}.png"
    
    # If icon already exists, return it
    if icon_path.exists():
        return icon_path
    
    # Create a simple circular icon
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle background
    margin = 4
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=bg_color,
        outline="#BBDEFB",
        width=2
    )
    
    # Draw icon based on type
    icon_color = "#1976D2"
    center_x, center_y = size // 2, size // 2
    
    if icon_type == "user":
        # Draw simple user icon (head + shoulders)
        # Head (circle)
        head_radius = size // 6
        draw.ellipse(
            [center_x - head_radius, center_y - size // 3,
             center_x + head_radius, center_y - size // 3 + head_radius * 2],
            fill=icon_color
        )
        # Body (rectangle/trapezoid)
        body_top = center_y - size // 3 + head_radius * 2
        body_bottom = center_y + size // 4
        draw.rectangle(
            [center_x - size // 4, body_top,
             center_x + size // 4, body_bottom],
            fill=icon_color
        )
    elif icon_type == "bot":
        # Draw simple robot icon (square head + body)
        # Head (rounded square)
        head_size = size // 3
        head_x = center_x - head_size // 2
        head_y = center_y - size // 3
        draw.rounded_rectangle(
            [head_x, head_y, head_x + head_size, head_y + head_size],
            radius=head_size // 4,
            fill=icon_color
        )
        # Eyes (two small circles)
        eye_radius = size // 20
        eye_y = head_y + head_size // 3
        draw.ellipse(
            [center_x - head_size // 4 - eye_radius, eye_y - eye_radius,
             center_x - head_size // 4 + eye_radius, eye_y + eye_radius],
            fill="#FFFFFF"
        )
        draw.ellipse(
            [center_x + head_size // 4 - eye_radius, eye_y - eye_radius,
             center_x + head_size // 4 + eye_radius, eye_y + eye_radius],
            fill="#FFFFFF"
        )
        # Body (rounded rectangle)
        body_top = head_y + head_size
        body_bottom = center_y + size // 4
        draw.rounded_rectangle(
            [center_x - size // 4, body_top,
             center_x + size // 4, body_bottom],
            radius=size // 20,
            fill=icon_color
        )
    
    # Save icon
    img.save(icon_path, "PNG")
    logger.info(f"Created icon: {icon_path}")
    return icon_path

# Create avatar icons
user_icon_path = create_avatar_icon("user", bg_color="#E3F2FD")
bot_icon_path = create_avatar_icon("bot", bg_color="#FFF3E0")

def chat_with_bot(message):
    """Chat function with Master Agent"""
    logger.info(f"Received message from user: {message[:100]}...")
    start_time = datetime.now()
    
    try:
        # Call API
        logger.info("Calling API: http://0.0.0.0:8000/chat")
        response = requests.post(
            "http://0.0.0.0:8000/chat",
            json={
                "message": message,
                "session_id": "demo",
                "user_id": "demo"
            },
            timeout=10000
        )
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"API response received in {elapsed_time:.2f}s - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                response_text = result.get("response", "No response")
                logger.info(f"Successfully processed message. Response length: {len(response_text)}")
                return response_text
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"API returned error: {error_msg}")
                return f"Error: {error_msg}"
        else:
            logger.error(f"API returned non-200 status: {response.status_code} - {response.text[:200]}")
            return f"API Error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Request timeout after {elapsed_time:.2f}s")
        return "Error: Request timeout. Please try again."
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return f"Error: Cannot connect to API server. Please check if the server is running."
    except Exception as e:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.exception(f"Unexpected error after {elapsed_time:.2f}s: {str(e)}")
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
        avatar_images=(str(user_icon_path), str(bot_icon_path))
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
            logger.debug("Empty message received, ignoring")
            return history, ""
        
        logger.info(f"Processing chat message in Gradio interface")
        
        # Add user message
        history.append([message, None])
        
        # Get bot response
        response = chat_with_bot(message)
        history[-1][1] = response
        
        logger.debug("Chat response added to history")
        return history, ""
    
    msg.submit(chat_fn, [msg, chatbot], [chatbot, msg])
    send_btn.click(chat_fn, [msg, chatbot], [chatbot, msg])
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])

if __name__ == "__main__":
    logger.info("Starting FinanceBot Demo UI on http://0.0.0.0:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860)

