import asyncio
import sys
import logging
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from app
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.agents.builds_agent import BuildsAgent

# Set up logging - only show warnings and errors by default
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_cli_interface(client: BuildsAgent):
    """Create and run the command-line interface"""
    
    def print_header():
        """Print the application header"""
        print("\n" + "="*80)
        print("🔨 League of Legends Builds Agent - Command Line Interface")
        print("="*80)
        print("AI-powered League of Legends builds assistant")
        print("📊 Contextual build recommendations based on current match")
        print()
        
        # Show connection status
        status_info = client.get_connection_status()
        print(f"Status: {status_info['status']}")
        print()
        
        if client.is_connected:
            print("💡 Example Queries:")
            print("  • 'Recommend a build for me'")
            print("  • 'What should I build against this team?'")
            print("  • 'Give me a 6-item build for my champion'")
            print("  • 'What's the optimal build for this match?'")
            print()
            print("Commands:")
            print("  • 'status' - Show connection status and available tools")
            print("  • 'match' - Show current match context")
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
            
            print(f"\n🎯 Capabilities:")
            print(status_info['capabilities'])
    
    def print_match_context():
        """Print current match context"""
        current_match = client.get_current_match()
        if current_match:
            from app.utils.formatters import format_match_for_llm
            formatted_match = format_match_for_llm(current_match)
            print("\n" + "="*60)
            print("📊 CURRENT MATCH CONTEXT")
            print("="*60)
            print(formatted_match)
            print("="*60)
        else:
            print("\n❌ No match context loaded")
    
    def print_help():
        """Print help information"""
        print("\n" + "="*60)
        print("🔨 League of Legends Builds Agent - Help")
        print("="*60)
        print()
        print("CONTEXTUAL BUILD RECOMMENDATIONS:")
        print("  Get personalized build recommendations based on your current match.")
        print("  The AI analyzes team compositions, enemy threats, and game situation.")
        print()
        print("  Examples:")
        print("    'Recommend a build for me'")
        print("    'What should I build against this team?'")
        print("    'Give me a 6-item build for my champion'")
        print("    'What's the optimal build for this match?'")
        print()
        print("MATCH ANALYSIS:")
        print("  Understand the current match context and enemy threats.")
        print()
        print("  Examples:")
        print("    'What threats should I watch out for?'")
        print("    'How should I adapt my build for this team comp?'")
        print("    'What are the key power spikes in this match?'")
        print("    'What defensive items do I need?'")
        print()
        print("BUILD ANALYSIS:")
        print("  Understand build reasoning, power spikes, and item synergies.")
        print()
        print("  Examples:")
        print("    'Why build Infinity Edge on Jinx?'")
        print("    'When should I buy Zhonya's on mages?'")
        print("    'What's the power spike timing for Trinity Force?'")
        print("    'Explain the synergy between items in this build'")
        print()
        print("COMMANDS:")
        print("  'status' - Show connection status and available capabilities")
        print("  'match' - Show current match context")
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
                user_input = input("🔨 Ask about League of Legends builds: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Thanks for using the League of Legends Builds Agent!")
                    break
                elif user_input.lower() == 'status':
                    print_status()
                    continue
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                elif user_input.lower() == 'match':
                    print_match_context()
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
                print("\n\n👋 Thanks for using the League of Legends Builds Agent!")
                break
            except EOFError:
                print("\n\n👋 Thanks for using the League of Legends Builds Agent!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    
    return 0

def main():
    client = BuildsAgent()
    
    try:
        # Initialize the builds agent
        print("🔧 Initializing Builds Agent...")
        status = client.initialize()
        print(f"✅ {status}")
        
        if not client.is_connected:
            print("❌ Failed to initialize Builds Agent")
            return 1
        
        # Set the default match data for contextual recommendations
        print("📊 Loading match context...")
        match_data = client.get_default_match_data()
        client.set_match_data(match_data)
        print(f"✅ Match context loaded for {match_data.get('searchedSummoner', {}).get('riotId', 'unknown player')}")
        
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
