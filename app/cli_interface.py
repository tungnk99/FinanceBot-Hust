#!/usr/bin/env python3
"""
FinanceBot CLI Interface - Command Line Interface for FinanceBot
"""
import asyncio
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv

from api_interface import FinanceBotAPI
from src.agents.planner_agents.master_agent import QueryType, Priority

# Load environment variables
load_dotenv(".env", override=True)


class FinanceBotCLI:
    """Command Line Interface for FinanceBot"""
    
    def __init__(self):
        self.api = FinanceBotAPI()
    
    async def initialize(self):
        """Initialize the FinanceBot system"""
        print("🚀 Initializing FinanceBot...")
        success = await self.api.initialize()
        if not success:
            print("❌ Failed to initialize FinanceBot")
            sys.exit(1)
        print("✅ FinanceBot initialized successfully!")
    
    async def interactive_mode(self):
        """Run interactive mode"""
        print("\n🎯 FinanceBot Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 FinanceBot: Thinking...")
                result = await self.api.ask(user_input)
                
                if result['success']:
                    print(f"✅ Success! Selected Agent: {result.get('selected_agent', {}).get('agent_name', 'Unknown')}")
                    print(f"📊 Response: {result['answer']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("\n📖 FinanceBot Commands:")
        print("=" * 30)
        print("General Commands:")
        print("  ask <question>           - Ask any financial question")
        print("  stock <symbol>           - Research a stock (e.g., 'stock VIC')")
        print("  analyze <symbol>         - Quantitative analysis (e.g., 'analyze AAPL')")
        print("  chart <symbol>           - Generate charts (e.g., 'chart VIC')")
        print("  risk <symbol>            - Risk assessment (e.g., 'risk VIC')")
        print("  report <symbol>          - Generate investment report (e.g., 'report VIC')")
        print("\nSystem Commands:")
        print("  help                     - Show this help")
        print("  quit/exit/q              - Exit the application")
        print("\nExamples:")
        print("  ask 'Thị trường chứng khoán VN hôm nay thế nào?'")
        print("  stock VIC")
        print("  analyze AAPL")
        print("  chart VIC with moving averages")
    
    async def process_command(self, command: str):
        """Process a single command"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == 'ask':
            question = ' '.join(parts[1:])
            if question:
                result = await self.api.ask(question)
                self.print_result(result)
            else:
                print("❌ Please provide a question")
        
        elif cmd == 'stock':
            if len(parts) > 1:
                symbol = parts[1]
                result = await self.api.stock_research(symbol)
                self.print_result(result)
            else:
                print("❌ Please provide a stock symbol")
        
        elif cmd == 'analyze':
            if len(parts) > 1:
                symbol = parts[1]
                indicators = ' '.join(parts[2:]) if len(parts) > 2 else "RSI, MACD, Moving Averages"
                result = await self.api.quantitative_analysis(symbol, indicators)
                self.print_result(result)
            else:
                print("❌ Please provide a stock symbol")
        
        elif cmd == 'chart':
            if len(parts) > 1:
                symbol = parts[1]
                chart_type = ' '.join(parts[2:]) if len(parts) > 2 else "price with moving averages"
                result = await self.api.generate_chart(symbol, chart_type)
                self.print_result(result)
            else:
                print("❌ Please provide a stock symbol")
        
        elif cmd == 'risk':
            if len(parts) > 1:
                symbol = parts[1]
                timeframe = ' '.join(parts[2:]) if len(parts) > 2 else "1 year"
                result = await self.api.risk_assessment(symbol, timeframe)
                self.print_result(result)
            else:
                print("❌ Please provide a stock symbol")
        
        elif cmd == 'report':
            if len(parts) > 1:
                symbol = parts[1]
                report_type = ' '.join(parts[2:]) if len(parts) > 2 else "investment analysis"
                result = await self.api.write_report(symbol, report_type)
                self.print_result(result)
            else:
                print("❌ Please provide a stock symbol")
        
        else:
            # Treat as general question
            result = await self.api.ask(command)
            self.print_result(result)
    
    def print_result(self, result: dict):
        """Print formatted result"""
        if result['success']:
            print(f"✅ Success!")
            if 'selected_agent' in result and result['selected_agent']:
                print(f"🤖 Selected Agent: {result['selected_agent'].get('agent_name', 'Unknown')}")
            if 'execution_time' in result and result['execution_time']:
                print(f"⏱️  Execution Time: {result['execution_time']:.2f}s")
            print(f"📊 Response: {result['answer']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    async def shutdown(self):
        """Shutdown the system"""
        await self.api.shutdown()


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="FinanceBot CLI - Your AI Financial Assistant")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--command", "-c", type=str, help="Run a single command")
    parser.add_argument("--demo", "-d", action="store_true", help="Run demo examples")
    
    args = parser.parse_args()
    
    cli = FinanceBotCLI()
    
    try:
        await cli.initialize()
        
        if args.demo:
            print("🎯 Running FinanceBot Demo...")
            print("=" * 40)
            
            # Demo examples
            examples = [
                ("ask", "Thị trường chứng khoán Việt Nam hôm nay như thế nào?"),
                ("stock", "VIC"),
                ("analyze", "AAPL"),
                ("chart", "VIC with Bollinger Bands")
            ]
            
            for cmd_type, query in examples:
                print(f"\n📝 Example: {cmd_type} {query}")
                if cmd_type == "ask":
                    result = await cli.api.ask(query)
                elif cmd_type == "stock":
                    result = await cli.api.stock_research(query)
                elif cmd_type == "analyze":
                    result = await cli.api.quantitative_analysis(query)
                elif cmd_type == "chart":
                    result = await cli.api.generate_chart(query.split()[0], query.split()[1:])
                
                cli.print_result(result)
            
            print(f"\n✅ Demo completed!")
        
        elif args.command:
            await cli.process_command(args.command)
        
        else:
            # Default to interactive mode
            await cli.interactive_mode()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        await cli.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
