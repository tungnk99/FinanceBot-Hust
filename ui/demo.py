"""
FinanceBot Demo - Gradio Interface
"""
import gradio as gr
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.chat_service import ChatService
from app.core.config import get_settings

class FinanceBotDemo:
    def __init__(self):
        self.chat_service = None
        self.settings = None
        
    async def initialize(self):
        """Initialize the chat service"""
        try:
            self.settings = get_settings()
            self.chat_service = ChatService()
            return True
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    async def chat_with_bot(self, message, history):
        """Process chat message and return response"""
        if not self.chat_service:
            return "❌ Chat service not initialized. Please check your configuration."
        
        try:
            # Process the message
            result = await self.chat_service.process_chat_message(message)
            
            if result["success"]:
                response = result["response"]
                agent_info = result.get("selected_agent", {})
                execution_time = result.get("execution_time", 0)
                
                # Format the response
                formatted_response = f"🤖 **FinanceBot Response:**\n\n{response}\n\n"
                
                if agent_info:
                    formatted_response += f"📊 **Agent Used:** {agent_info.get('agent_name', 'Unknown')}\n"
                    formatted_response += f"⏱️ **Response Time:** {execution_time:.2f}s\n"
                
                return formatted_response
            else:
                return f"❌ **Error:** {result.get('error', 'Unknown error occurred')}"
                
        except Exception as e:
            return f"❌ **Error:** {str(e)}"
    
    async def analyze_stock(self, symbol, analysis_type, timeframe):
        """Analyze a stock"""
        if not self.chat_service:
            return "❌ Chat service not initialized."
        
        try:
            result = await self.chat_service.analyze_stock(
                symbol=symbol,
                analysis_type=analysis_type,
                timeframe=timeframe
            )
            
            if result["success"]:
                return f"📈 **Stock Analysis for {symbol}:**\n\n{result['response']}"
            else:
                return f"❌ **Error:** {result.get('error', 'Analysis failed')}"
                
        except Exception as e:
            return f"❌ **Error:** {str(e)}"
    
    async def generate_chart(self, symbol, chart_type, timeframe):
        """Generate a financial chart"""
        if not self.chat_service:
            return "❌ Chat service not initialized."
        
        try:
            result = await self.chat_service.generate_chart(
                symbol=symbol,
                chart_type=chart_type,
                timeframe=timeframe
            )
            
            if result["success"]:
                return f"📊 **Chart for {symbol}:**\n\n{result['response']}"
            else:
                return f"❌ **Error:** {result.get('error', 'Chart generation failed')}"
                
        except Exception as e:
            return f"❌ **Error:** {str(e)}"

# Create demo instance
demo_bot = FinanceBotDemo()

# Initialize the demo
async def init_demo():
    success = await demo_bot.initialize()
    if success:
        print("✅ FinanceBot Demo initialized successfully!")
    else:
        print("❌ FinanceBot Demo initialization failed!")

# Create Gradio interface
def create_interface():
    with gr.Blocks(
        title="FinanceBot Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        .chat-message {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        """
    ) as demo:
        
        gr.Markdown(
            """
            # 🤖 FinanceBot Demo
            **Multi-Agent Financial Analysis System**
            
            This demo showcases the FinanceBot's capabilities including:
            - 💬 Natural language financial queries
            - 📈 Stock analysis and technical indicators
            - 📊 Chart generation
            - 🔍 Market research and sentiment analysis
            """
        )
        
        with gr.Tabs():
            # Chat Tab
            with gr.Tab("💬 Chat with FinanceBot"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="Chat History",
                            height=400,
                            show_label=True,
                            container=True,
                            bubble_full_width=False
                        )
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Ask me anything about finance, stocks, or market analysis...",
                            lines=2
                        )
                        with gr.Row():
                            send_btn = gr.Button("Send", variant="primary", size="lg")
                            clear_btn = gr.Button("Clear", variant="secondary")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 💡 Example Questions:")
                        gr.Markdown("""
                        - "Analyze AAPL stock performance"
                        - "What are the current market trends?"
                        - "Calculate RSI for TSLA"
                        - "Generate a price chart for MSFT"
                        - "What's the sentiment around Bitcoin?"
                        """)
                
                # Chat functionality
                def chat_fn(message, history):
                    if not message.strip():
                        return history, ""
                    
                    # Add user message to history
                    history.append([message, None])
                    
                    # Get bot response
                    response = asyncio.run(demo_bot.chat_with_bot(message, history))
                    
                    # Add bot response to history
                    history[-1][1] = response
                    
                    return history, ""
                
                msg.submit(chat_fn, [msg, chatbot], [chatbot, msg])
                send_btn.click(chat_fn, [msg, chatbot], [chatbot, msg])
                clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
            
            # Stock Analysis Tab
            with gr.Tab("📈 Stock Analysis"):
                with gr.Row():
                    with gr.Column():
                        stock_symbol = gr.Textbox(
                            label="Stock Symbol",
                            placeholder="e.g., AAPL, MSFT, TSLA",
                            value="AAPL"
                        )
                        analysis_type = gr.Dropdown(
                            choices=["comprehensive", "technical", "fundamental", "sentiment"],
                            label="Analysis Type",
                            value="comprehensive"
                        )
                        timeframe = gr.Dropdown(
                            choices=["1 month", "3 months", "6 months", "1 year", "2 years"],
                            label="Timeframe",
                            value="1 year"
                        )
                        analyze_btn = gr.Button("Analyze Stock", variant="primary")
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="Analysis Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                def analyze_stock_fn(symbol, analysis_type, timeframe):
                    if not symbol.strip():
                        return "Please enter a stock symbol."
                    
                    return asyncio.run(demo_bot.analyze_stock(symbol, analysis_type, timeframe))
                
                analyze_btn.click(
                    analyze_stock_fn,
                    [stock_symbol, analysis_type, timeframe],
                    analysis_output
                )
            
            # Chart Generation Tab
            with gr.Tab("📊 Chart Generation"):
                with gr.Row():
                    with gr.Column():
                        chart_symbol = gr.Textbox(
                            label="Stock Symbol",
                            placeholder="e.g., AAPL, MSFT, TSLA",
                            value="AAPL"
                        )
                        chart_type = gr.Dropdown(
                            choices=[
                                "price with moving averages",
                                "candlestick",
                                "volume",
                                "RSI",
                                "MACD",
                                "Bollinger Bands"
                            ],
                            label="Chart Type",
                            value="price with moving averages"
                        )
                        chart_timeframe = gr.Dropdown(
                            choices=["1 month", "3 months", "6 months", "1 year", "2 years"],
                            label="Timeframe",
                            value="1 year"
                        )
                        generate_btn = gr.Button("Generate Chart", variant="primary")
                    
                    with gr.Column():
                        chart_output = gr.Textbox(
                            label="Chart Generation Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                def generate_chart_fn(symbol, chart_type, timeframe):
                    if not symbol.strip():
                        return "Please enter a stock symbol."
                    
                    return asyncio.run(demo_bot.generate_chart(symbol, chart_type, timeframe))
                
                generate_btn.click(
                    generate_chart_fn,
                    [chart_symbol, chart_type, chart_timeframe],
                    chart_output
                )
        
        # Footer
        gr.Markdown(
            """
            ---
            **FinanceBot Multi-Agent System** | Built with Gradio | Powered by OpenAI GPT-4
            """
        )
    
    return demo

# Main function
def main():
    print("🚀 Starting FinanceBot Demo...")
    
    # Initialize the demo
    asyncio.run(init_demo())
    
    # Create and launch the interface
    demo = create_interface()
    
    print("🌐 Launching Gradio interface...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()

