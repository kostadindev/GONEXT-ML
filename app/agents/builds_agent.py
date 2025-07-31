import asyncio
import logging
from typing import Optional, List, Dict
import threading
import queue

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from app.config import settings
from app.utils.callbacks import ToolCallLogger
from app.utils.formatters import format_match_for_llm
# Import the MCP functions
from app.mcp.builds_mcp import get_champion_build, get_champion_stats

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)

# Create LangChain tool wrappers for the MCP functions
@tool
async def champion_build_tool(champion: str) -> str:
    """Get comprehensive build analysis for a League of Legends champion from OP.GG.
    
    This tool provides detailed build information including:
    - Core item combinations with pick rates and win rates (e.g., "Yun Tal -> IE -> Hurricane: 34.19% pick, 60.58% win")
    - Recommended boots with usage statistics
    - Situational items categorized by purpose (anti-tank, anti-heal, defensive)
    - Complete 6-item build order progression
    - Performance metrics for different item choices
    - Strategic itemization priorities and reasoning
    
    Args:
        champion: Champion name (e.g. jinx, yasuo, ahri)
    
    Returns:
        Comprehensive build analysis with statistical data, item recommendations,
        and strategic guidance for optimal itemization.
    """
    return await get_champion_build(champion)

@tool  
async def champion_stats_tool(champion: str) -> str:
    """Get current meta statistics for a League of Legends champion from OP.GG.
    
    This tool provides performance metrics including:
    - Current patch version and tier ranking (1-5 scale)
    - Win rate, pick rate, and ban rate percentages
    - Total games played for statistical confidence
    - Primary position/role information
    - Meta viability assessment
    
    Args:
        champion: Champion name (e.g. jinx, yasuo, ahri)
    
    Returns:
        Current meta statistics and performance data for strategic decision making.
    """
    return await get_champion_stats(champion)

class BuildsAgent:
    def __init__(self):
        # Initialize core components
        self.agent = None
        self.tools = [champion_build_tool, champion_stats_tool]
        self.is_connected = False
        self.message_queue = queue.Queue()
        
        # Event loop management
        self.loop = None
        self.loop_thread = None
        self.loop_ready = threading.Event()
        
        # Initialize LangChain model with Google Gemini
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=settings.gemini_api_key
        )
        
        # Initialize callback handler for logging
        self.callback_handler = ToolCallLogger(self.message_queue)
    
    async def process_query_async(self, query: str, history: List[Dict] = None, match: Dict = None) -> str:
        """Process a League of Legends builds-related query"""
        if not self.agent:
            return "❌ Agent not initialized. Please connect first."
        
        try:
            # Convert history to LangChain messages
            input_messages = []
            
            if history:
                for msg in history:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    metadata = msg.get('metadata', None)
                    
                    # Skip tool call messages and system messages
                    if metadata or content.startswith("Let me help you with"):
                        continue
                    
                    # Convert to LangChain message format
                    if role == "user":
                        input_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        input_messages.append(AIMessage(content=content))
            
            # Prepare the query with match context
            enhanced_query = query
            match_to_use = match if match is not None else self.get_current_match()
            
            if match_to_use:
                formatted_match = format_match_for_llm(match_to_use)
                enhanced_query = f"""CURRENT MATCH CONTEXT:
{formatted_match}

USER QUERY: {query}

Please analyze the above match context and recommend an optimal 6-item build for the player marked as (YOU). Consider the team compositions, enemy champions, and game situation when making your recommendation."""
            
            # Add the current query
            if not input_messages or input_messages[-1].content != enhanced_query:
                input_messages.append(HumanMessage(content=enhanced_query))
            
            # Run the agent
            result = await self.agent.ainvoke(
                {"messages": input_messages},
                config={"callbacks": [self.callback_handler]}
            )
            
            # Extract the final message
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                response = final_message.content if hasattr(final_message, 'content') else str(final_message)
                return response
            else:
                return "❌ No response from agent"
                
        except Exception as e:
            error_msg = f"Error processing builds query: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _start_event_loop(self):
        """Start the event loop in a background thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop_ready.set()
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        self.loop_ready.wait()

    def _run_in_loop(self, coro):
        """Run a coroutine in the background event loop"""
        if not self.loop:
            raise RuntimeError("Event loop not started")
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    async def initialize_agent(self):
        """Initialize the builds agent with appropriate system prompt"""
        logger.info("Initializing League of Legends Builds Agent")

        system_prompt = """You are a League of Legends Expert recommending builds for a player.

You will be given a match with the champions of both teams.
You have access to real-time tools to check current best performing builds and detailed statistics for any champion from OP.GG.

Available Tools:
- champion_build_tool: Get detailed build information including core items, boots, situational items, build order, and win rates
- champion_stats_tool: Get champion statistics including tier ranking, win rate, pick rate, ban rate, and patch information

Given the match context and current meta builds, you will need to recommend a 6 item build for the player. Include boots unless the champion does not need them.

**BUILD RECOMMENDATION GUIDELINES:**

1. **Analyze the Match Context:**
   - Identify the player's champion and role
   - Consider enemy team composition and threats
   - Evaluate your team's composition and needs
   - Assess the game mode and queue type
   - Consider the enemy laner or jungler

2. **Build Structure:**
   - Recommend exactly 6 items for a full build
   - Include core items that synergize with the champion
   - Add situational items based on enemy threats
   - Consider defensive items when needed
   - Include boots unless the champion does not need them

3. **Reasoning:**
   - Explain why each item is chosen
   - Mention power spikes and timing
   - Address specific enemy threats
   - Consider team composition synergy

4. **Adaptation:**
   - Provide alternative items for different situations
   - Explain when to deviate from the recommended build
   - Consider early, mid, and late game priorities

5. **Tool Usage:**
   - Use champion_build_tool to get current meta builds for the player's champion
   - Use champion_stats_tool to check champion performance and tier rankings
   - Use tools for enemy champions to understand threats and counter-build accordingly
   - Compare current patch data with match context

Always provide clear reasoning for your build recommendations, use the available tools to get current meta information, and consider the specific match context provided."""

        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,  # Now includes champion build and stats tools
            prompt=system_prompt,
            debug=True
        )

        logger.info("✅ Builds Agent initialized successfully")
        self.is_connected = True

    def get_connection_status(self) -> dict:
        """Get the current connection status"""
        if not self.is_connected:
            return {
                "status": "❌ **Not Connected** - Please initialize the agent first",
                "tools": "No tools available yet",
                "capabilities": ""
            }
        
        return {
            "status": "✅ **Connected** - Builds Agent ready",
            "tools": "OP.GG Integration: champion_build_tool, champion_stats_tool",
            "capabilities": """**Current Capabilities:**
            - Real-time champion build data from OP.GG
            - Champion statistics and meta analysis
            - Situational build recommendations based on match context
            - Core items, boots, and situational item suggestions
            - Win rate and pick rate analysis"""
        }
    
    def process_query(self, query: str, history: List[Dict] = None, match: Dict = None) -> str:
        """Process a builds query and return the response"""
        if not query.strip():
            return ""
        
        if not self.is_connected:
            return "❌ Agent not initialized. Please initialize first."
        
        print("\n🔨 Processing your League of Legends builds query...")
        
        try:
            # Start event loop if not already running
            if not self.loop:
                self._start_event_loop()
            
            # Clear the message queue
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Process the query in the background
            def run_query():
                return self._run_in_loop(self.process_query_async(query, history, match))
            
            result_container = {"result": None, "error": None}
            
            def query_thread():
                try:
                    result_container["result"] = run_query()
                except Exception as e:
                    result_container["error"] = str(e)
            
            thread = threading.Thread(target=query_thread)
            thread.start()
            
            # Monitor for any processing messages
            while thread.is_alive():
                try:
                    message_type, *args = self.message_queue.get(timeout=0.1)
                    # Handle any future tool call messages here
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
            
            # Wait for completion
            thread.join()
            
            # Return result
            if result_container["error"]:
                return f"❌ Error: {result_container['error']}"
            else:
                return result_container["result"]
            
        except Exception as e:
            error_msg = f"Error processing builds query: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"

    def initialize(self):
        """Initialize the builds agent (synchronous wrapper)"""
        try:
            if not self.loop:
                self._start_event_loop()
            
            self._run_in_loop(self.initialize_agent())
            return "✅ Builds Agent initialized successfully"
        except Exception as e:
            error_msg = f"Error initializing builds agent: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"

    def get_default_match_data(self) -> Dict:
        """Get the default/constant match data for testing purposes"""
        from app.utils.formatters import match_data
        return match_data
    
    def set_match_data(self, match_data: Dict):
        """Set the current match data for the agent to use"""
        self.current_match = match_data
        logger.info(f"Match data set for {match_data.get('searchedSummoner', {}).get('riotId', 'unknown player')}")
    
    def get_current_match(self) -> Dict:
        """Get the current match data"""
        return getattr(self, 'current_match', None)

    async def cleanup(self):
        """Clean up resources"""
        # Stop the event loop
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.loop_thread:
                self.loop_thread.join(timeout=5)
        
        self.is_connected = False
        logger.info("Builds Agent cleaned up")
