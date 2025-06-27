import asyncio
import sys
import logging
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from app
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.agents.chatbot_agent import ChatbotAgent

# Set up logging - only show warnings and errors by default
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_cli_interface(client: ChatbotAgent):
    """Create and run the command-line interface"""
    
    def print_header():
        """Print the application header"""
        print("\n" + "="*80)
        print("🎮 League of Legends MCP Client - Command Line Interface")
        print("="*80)
        print("AI-powered League of Legends assistant with access to Riot Games API")
        print()
        
        # Show connection status
        status_info = client.get_connection_status()
        print(f"Status: {status_info['status']}")
        print()
        
        if client.is_connected:
            print("💡 Example Queries:")
            print("  • 'What lane and against who did Sneaky#NA69 play in the last match?'")
            print("  • 'What is the current rank of Sneaky#NA69?'")
            print("  • 'Show me ddragon://champions'")
            print("  • 'Use find_player_stats for Sneaky#NA69'")
            print()
            print("Commands:")
            print("  • 'status' - Show connection status and available tools")
            print("  • 'help' - Show this help message")
            print("  • 'quit' or 'exit' - Exit the application")
            print()
    
    def print_status():
        """Print detailed status information"""
        status_info = client.get_connection_status()
        print(f"\n{status_info['status']}")
        
        if client.is_connected:
            print(f"\n🔧 Available Tools:")
            print(status_info['tools'])
            
            print(f"\n📚 Available Resources:")
            print(status_info['resources'])
            
            print(f"\n🚀 Available Prompts:")
            print(status_info['prompts'])
    
    def print_help():
        """Print help information"""
        print("\n" + "="*60)
        print("🎮 League of Legends MCP Client - Help")
        print("="*60)
        print()
        print("TOOL-BASED QUERIES:")
        print("  Ask natural language questions about League of Legends players,")
        print("  matches, rankings, and more. The AI will use real-time API tools.")
        print()
        print("  Examples:")
        print("    'What champions did Sneaky#NA69 play in the last 3 matches?'")
        print("    'Is Faker#T1 currently in a game?'")
        print("    'Show me the challenger ladder for ranked solo queue'")
        print()
        print("RESOURCE QUERIES:")
        print("  Access static game data by typing resource URIs directly.")
        print()
        print("  Data Dragon Resources (require internet):")
        print("    'ddragon://champions' - All champions summary")
        print("    'ddragon://items' - Complete items database")
        print("    'ddragon://summoner_spells' - Summoner spells data")
        print()
        print("  Constants Resources (work offline):")
        print("    'constants://queues' - Queue types and IDs")
        print("    'constants://ranked_tiers' - Ranking system details")
        print("    'constants://maps' - Map information")
        print()
        print("WORKFLOW EXECUTION:")
        print("  Execute complex workflows by referencing prompt names.")
        print()
        print("  Examples:")
        print("    'Use find_player_stats for Sneaky#NA69'")
        print("    'Use champion_analysis for Azir'")
        print("    'Use player_improvement for MyName#NA1 targeting Gold as ADC'")
        print()
        print("COMMANDS:")
        print("  'status' - Show connection status and available capabilities")
        print("  'help' - Show this help message")
        print("  'quit' or 'exit' - Exit the application")
        print()
    
    # Start the CLI
    print_header()
    
    # Chat history for context
    chat_history = []
    
    try:
        while True:
            try:
                # Get user input
                user_input = input("🎮 Ask about League of Legends: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Thanks for using the League of Legends MCP Client!")
                    break
                elif user_input.lower() == 'status':
                    print_status()
                    continue
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                
                # Add user message to history
                chat_history.append({"role": "user", "content": user_input})
                
                # Process the query
                print()  # Add some space before processing
                response = client.process_query(user_input, chat_history, match=None)
                
                # Add assistant response to history
                chat_history.append({"role": "assistant", "content": response})
                
                # Print the response
                print(f"\n🤖 {response}")
                print("\n" + "-"*80)
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using the League of Legends MCP Client!")
                break
            except EOFError:
                print("\n\n👋 Thanks for using the League of Legends MCP Client!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    
    return 0

def main():
    client = ChatbotAgent()
    
    try:
        # Start the persistent event loop
        print("🔧 Starting event loop...")
        client._start_event_loop()
        
        print("🔗 Connecting to MCP server...")
        client._run_in_loop(client.connect_to_server())
        print("✅ Connected successfully!")
        
        # Start the CLI interface
        return create_cli_interface(client)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Startup error: {e}")
        return 1
    finally:
        asyncio.run(client.cleanup())

if __name__ == "__main__":
    sys.exit(main()) 