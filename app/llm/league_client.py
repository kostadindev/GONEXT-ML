import asyncio
import logging
from typing import Optional, List, Dict
import threading
import queue

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from app.config import settings
from app.utils.callbacks import ToolCallLogger

load_dotenv()  # load environment variables from .env

# Set up logging - only show warnings and errors by default
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set specific loggers to show important info
logging.getLogger(__name__).setLevel(logging.INFO)  # Allow INFO for our important logs

class LeagueMCPClient:
    def __init__(self):
        # Initialize client objects
        self.mcp_client: Optional[MultiServerMCPClient] = None
        self.agent = None
        self.tools = []
        self.resources = []
        self.prompts = []
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
        
        # Initialize callback handler for tool logging
        self.callback_handler = ToolCallLogger(self.message_queue)
    
    async def process_query_async(self, query: str, history: List[Dict] = None) -> str:
        """Process a League-related query using LangChain ReAct agent with Gemini"""
        if not self.agent:
            return "❌ Agent not initialized. Please connect to the MCP server first."
        
        try:
            # Convert history to LangChain messages
            input_messages = []
            
            if history:
                for msg in history:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    metadata = msg.get('metadata', None)
                    
                    # Skip tool call messages (they have metadata) and system messages
                    if metadata:
                        continue
                    if content.startswith("Let me help you with that League of Legends query"):
                        continue
                    if content.startswith("Using ") and "tool" in content:
                        continue
                    if content.startswith("Tool returned:"):
                        continue
                    if content.startswith("Tool error:"):
                        continue
                    
                    # Convert to LangChain message format
                    if role == "user":
                        input_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        input_messages.append(AIMessage(content=content))
            
            # Add the current query if it's not already the last message
            if not input_messages or input_messages[-1].content != query:
                input_messages.append(HumanMessage(content=query))
            
            # Run the agent with callback for tool logging
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
            error_msg = f"Error processing query with agent: {str(e)}"
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
        self.loop_ready.wait()  # Wait for the loop to be ready

    def _run_in_loop(self, coro):
        """Run a coroutine in the background event loop"""
        if not self.loop:
            raise RuntimeError("Event loop not started")
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    async def connect_to_server(self):
        """Connect to the League MCP server and initialize the LangChain agent"""
        logger.info(f"Connecting to League MCP server")

        # Create MCP client configuration
        self.mcp_client = MultiServerMCPClient(
            {
                "league-mcp": {
                    "command": "league-mcp",  # Using the installed pip package
                    "args": [],  # Arguments for the command
                    "transport": "stdio",  # Specify the transport type
                    "env": {
                        "RIOT_API_KEY": settings.riot_api_key
                    }
                }
            }
        )
        
        # Get tools from MCP server
        self.tools = await self.mcp_client.get_tools()
        # Note: Resources and prompts are available but not easily listable with MultiServerMCPClient
        self.resources = []  # Will be accessed on-demand
        self.prompts = []   # Will be accessed on-demand
        
        logger.info(f"✅ Retrieved {len(self.tools)} tools from MCP server (resources and prompts available on-demand)")
        
        # Create the ReAct agent
        
        system_prompt = """You are a League of Legends AI assistant specialized exclusively in League of Legends. You have access to Riot Games API tools, static game data resources, and workflow prompts through MCP (Model Context Protocol).

IMPORTANT: You are ONLY for League of Legends queries. If users ask about other games, topics, or general questions unrelated to League of Legends, politely redirect them to ask about League of Legends instead.

CRITICAL: You MUST use the provided tools to get real data. NEVER generate code snippets, fake data, or example responses.

Available MCP Capabilities:

1. TOOLS - API Functions (you can use these directly):

ACCOUNT TOOLS:
- get_account_by_riot_id(game_name, tag_line, region="americas") - Look up account by Riot ID (e.g., game_name="Faker", tag_line="T1")
- get_account_by_puuid(puuid, region="americas") - Get account info by PUUID
- get_active_shard(game, puuid, region="americas") - Get active shard for games like VALORANT, Legends of Runeterra
- get_active_region(game, puuid, region="americas") - Get active region for LoL/TFT

MATCH TOOLS:
- get_match_ids_by_puuid(puuid, start_time=None, end_time=None, queue=None, match_type=None, start=0, count=20, region="na1") - Get match IDs for a player
- get_match_details(match_id, region="na1") - Get detailed match information
- get_match_timeline(match_id, region="na1") - Get match timeline

SUMMONER TOOLS:
- get_summoner_by_puuid(puuid, region="na1") - Get summoner info by PUUID
- get_summoner_by_name(name, region="na1") - Get summoner info by name

SPECTATOR TOOLS:
- get_active_game(puuid, region="na1") - Get current game info
- get_featured_games(region="na1") - Get featured games

LEAGUE TOOLS:
- get_challenger_league(queue, region="na1") - Get challenger league
- get_grandmaster_league(queue, region="na1") - Get grandmaster league  
- get_master_league(queue, region="na1") - Get master league

IMPORTANT PARAMETERS:
- Routing regions: americas, asia, europe (for account tools)
- Platform regions: na1, euw1, eun1, kr, jp1, br1, la1, la2, oc1, tr1, ru (for game-specific tools)
- Games: lol (League of Legends), tft (Teamfight Tactics), val (VALORANT), lor (Legends of Runeterra)

EXAMPLE WORKFLOW for "get puuid of Sneaky#NA1 then get match details":
1. Call get_account_by_riot_id(game_name="Sneaky", tag_line="NA1", region="americas")
2. Extract the puuid from the result
3. Call get_match_ids_by_puuid(puuid=extracted_puuid, region="na1")
4. Extract match id from the result
5. Call get_match_details(match_id=extracted_match_id, region="na1")

2. RESOURCES - Static Game Data (ask user to use these when needed):
- ddragon://versions - All Data Dragon versions
- ddragon://languages - Supported languages
- ddragon://champions - All champions summary
- ddragon://champion_data - Detailed champion data
- ddragon://items - All items data
- ddragon://summoner_spells - Summoner spells data
- constants://queues - Queue types and IDs
- constants://maps - Map IDs and names
- constants://game_modes - Game modes info
- constants://game_types - Game types info
- constants://seasons - Season IDs
- constants://ranked_tiers - Ranked tier information
- constants://routing - Platform/regional routing

3. PROMPTS - Workflow Templates:
When users request prompts, you will receive detailed workflow instructions to follow step-by-step.
- find_player_stats - Complete player analysis workflow  
- tournament_setup - Tournament organization workflow
- champion_analysis - Deep champion analysis workflow
- team_composition_analysis - Team comp analysis workflow
- player_improvement - Personalized improvement plan

IMPORTANT USAGE GUIDELINES:

**When to suggest Resources:**
- User asks for "all champions", "champion list", "items", "queues" → Suggest ddragon:// or constants:// resources
- User wants reference data, game constants, static information → Use resources directly

**When executing Prompts:**
- Follow the provided workflow instructions exactly
- Use the specified tools in the recommended order
- Gather all required data before providing analysis
- Present results in the structured format requested

**Resource Access:**
If a user types a resource URI directly (e.g., "ddragon://champions"), the system will automatically fetch it.
If resources fail due to network issues, provide helpful fallback information.

**Error Handling:**
- Data Dragon resources require internet connectivity
- Constants resources should work offline
- Always provide informative error messages with alternatives

DO NOT generate Python code, print statements, or fake data. USE THE ACTUAL TOOLS."""

        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=system_prompt,
            debug=True  # Enable debug mode for more logging
        )

        # List available tools
        tool_names = [tool.name for tool in self.tools]
        logger.info(f"Connected with {len(self.tools)} available tools: {tool_names}")
        
        self.is_connected = True

    def get_connection_status(self) -> dict:
        """Get the current connection status and available tools, resources, and prompts"""
        if not self.is_connected:
            return {
                "status": "❌ **Not Connected** - Please connect to MCP server first",
                "tools": "",
                "resources": "",
                "prompts": ""
            }
        
        tool_names = [tool.name for tool in self.tools]
        
        # Group tools by category for better display
        account_tools = [t for t in tool_names if 'account' in t]
        match_tools = [t for t in tool_names if 'match' in t]
        summoner_tools = [t for t in tool_names if 'summoner' in t]
        league_tools = [t for t in tool_names if 'league' in t]
        spectator_tools = [t for t in tool_names if 'active' in t or 'featured' in t]
        other_tools = [t for t in tool_names if t not in account_tools + match_tools + summoner_tools + league_tools + spectator_tools]
        
        # Main status
        main_status = f"✅ **Connected** - {len(self.tools)} tools + resources & prompts available"
        
        # Tools section
        tools_content = ""
        if account_tools:
            tools_content += f"**Account Tools:** {', '.join(account_tools)}\n\n"
        if summoner_tools:
            tools_content += f"**Summoner Tools:** {', '.join(summoner_tools)}\n\n"
        if match_tools:
            tools_content += f"**Match Tools:** {', '.join(match_tools)}\n\n"
        if league_tools:
            tools_content += f"**League Tools:** {', '.join(league_tools)}\n\n"
        if spectator_tools:
            tools_content += f"**Spectator Tools:** {', '.join(spectator_tools)}\n\n"
        if other_tools:
            tools_content += f"**Other Tools:** {', '.join(other_tools)}\n\n"
        
        tools_content += f"**Total:** {len(self.tools)} tools for real-time League of Legends data"
        
        # Resources section
        resources_content = """**Data Dragon Resources (Static Game Data):**
- `ddragon://versions` - All available Data Dragon versions
- `ddragon://languages` - Supported localization languages  
- `ddragon://champions` - All champions summary data
- `ddragon://champion_data` - Detailed champion information (sample: Ahri)
- `ddragon://items` - Complete items database with stats and costs
- `ddragon://summoner_spells` - Summoner spells data and cooldowns

**Game Constants Resources (Reference Data):**
- `constants://queues` - Queue types and IDs (Ranked, Normal, ARAM, etc.)
- `constants://maps` - Map information (Summoner's Rift, ARAM, etc.)
- `constants://game_modes` - Game mode details and descriptions
- `constants://game_types` - Game type classifications
- `constants://seasons` - Season information and IDs
- `constants://ranked_tiers` - Ranking system details and LP thresholds
- `constants://routing` - API routing information for different regions

**Usage:** Type resource URIs directly (e.g., "Show me ddragon://champions")"""
        
        # Prompts section  
        prompts_content = """**Available Workflow Prompts:**

- **`find_player_stats`** - Complete player analysis workflow
  - *Usage:* "Use find_player_stats for Sneaky#NA69"
  - *Provides:* Step-by-step player analysis including stats, matches, and performance

- **`tournament_setup`** - Tournament organization workflow
  - *Usage:* "Use tournament_setup for My Tournament"
  - *Provides:* Complete tournament setup guide with compliance requirements

- **`champion_analysis`** - Deep champion analysis workflow
  - *Usage:* "Use champion_analysis for Azir"
  - *Provides:* Comprehensive champion analysis including meta, builds, and strategies

- **`team_composition_analysis`** - Team comp analysis workflow
  - *Usage:* "Use team_composition_analysis for Azir,Graves,Thresh,Jinx,Malphite"
  - *Provides:* Team synergy analysis and strategic recommendations

- **`player_improvement`** - Personalized improvement plan
  - *Usage:* "Use player_improvement for MyName#NA1 targeting Gold as ADC"
  - *Provides:* Customized coaching plan and skill development roadmap

**Usage:** Reference prompt names in your queries for complex workflow automation"""
        
        return {
            "status": main_status,
            "tools": tools_content.strip(),
            "resources": resources_content.strip(),
            "prompts": prompts_content.strip()
        }
    
    def process_query(self, query: str, history: List[Dict] = None) -> str:
        """Process a query and return the response with tool call information"""
        if not query.strip():
            return ""
        
        if not self.is_connected:
            return "❌ Not connected to MCP server. Please check connection."
        
        print("\n🤖 Processing your League of Legends query...")
        
        try:
            # Check if this is a resource or prompt request
            query_lower = query.lower()
            
            # Handle resource requests
            if any(prefix in query_lower for prefix in ['ddragon://', 'constants://']):
                for line in query.split():
                    if '://' in line:
                        resource_uri = line.strip()
                        server_name = "league-mcp"
                        print(f"🔍 Fetching resource: {resource_uri}")
                        
                        content = self._run_in_loop(self.get_resource_content(server_name, resource_uri))
                        return content
            
            # Handle prompt requests
            prompt_keywords = ['find_player_stats', 'tournament_setup', 'champion_analysis', 'team_composition_analysis', 'player_improvement']
            for prompt_name in prompt_keywords:
                if prompt_name in query_lower:
                    server_name = "league"
                    print(f"🚀 Executing workflow: {prompt_name}")
                    
                    # Extract parameters from the query if possible
                    kwargs = {}
                    if 'for ' in query_lower:
                        parts = query.split('for ')
                        if len(parts) > 1:
                            player_part = parts[1].strip()
                            if '#' in player_part:
                                game_name, tag_line = player_part.split('#', 1)
                                kwargs['game_name'] = game_name.strip()
                                kwargs['tag_line'] = tag_line.strip()
                            elif prompt_name == 'champion_analysis':
                                kwargs['champion_name'] = player_part
                            elif prompt_name == 'team_composition_analysis':
                                kwargs['champions'] = player_part
                            elif prompt_name == 'player_improvement':
                                if 'targeting ' in player_part:
                                    targeting_part = player_part.split('targeting ')[1]
                                    if ' as ' in targeting_part:
                                        rank_part, role_part = targeting_part.split(' as ', 1)
                                        kwargs['target_rank'] = rank_part.strip()
                                        kwargs['current_role'] = role_part.strip()
                                    else:
                                        kwargs['target_rank'] = targeting_part.strip()
                                if '#' in player_part.split(' targeting')[0]:
                                    name_part = player_part.split(' targeting')[0]
                                    game_name, tag_line = name_part.split('#', 1)
                                    kwargs['game_name'] = game_name.strip()
                                    kwargs['tag_line'] = tag_line.strip()
                            elif prompt_name == 'tournament_setup':
                                kwargs['tournament_name'] = player_part
                    
                    # Get the workflow prompt content
                    workflow_instructions = self._run_in_loop(self.get_prompt_content(server_name, prompt_name, **kwargs))
                    
                    # Create an enhanced query that includes the workflow instructions
                    enhanced_query = f"""
Execute the following workflow for the user's request: "{query}"

WORKFLOW INSTRUCTIONS:
{workflow_instructions}

Please follow these instructions step by step and use the available tools to gather the required data and provide a comprehensive analysis.
"""
                    
                    # Clear the message queue before processing
                    while not self.message_queue.empty():
                        try:
                            self.message_queue.get_nowait()
                        except queue.Empty:
                            break
                    
                    # Process the enhanced query with workflow instructions
                    def run_workflow():
                        return self._run_in_loop(self.process_query_async(enhanced_query, history))
                    
                    # Start processing the workflow
                    result_container = {"result": None, "error": None}
                    
                    def workflow_thread():
                        try:
                            result_container["result"] = run_workflow()
                        except Exception as e:
                            result_container["error"] = str(e)
                    
                    thread = threading.Thread(target=workflow_thread)
                    thread.start()
                    
                    # Monitor for tool calls while processing the workflow
                    current_tool = None
                    while thread.is_alive():
                        try:
                            message_type, *args = self.message_queue.get(timeout=0.1)
                            
                            if message_type == "tool_start":
                                tool_name, input_str = args
                                current_tool = tool_name
                                display_input = input_str[:200] + "..." if len(input_str) > 200 else input_str
                                print(f"🔧 Using {tool_name} tool with input: {display_input}")
                            
                            elif message_type == "tool_end":
                                output = args[0]
                                if current_tool:
                                    display_output = output[:300] + "..." if len(output) > 300 else output
                                    print(f"🛠️ Tool '{current_tool}' returned: {display_output}")
                                    current_tool = None
                            
                            elif message_type == "tool_error":
                                error = args[0]
                                if current_tool:
                                    print(f"💥 Error in tool '{current_tool}': {error}")
                                    current_tool = None
                        
                        except queue.Empty:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing tool message during workflow: {e}")
                            continue
                    
                    # Wait for the workflow to complete
                    thread.join()
                    
                    # Return the final workflow result
                    if result_container["error"]:
                        return f"❌ Workflow execution error: {result_container['error']}"
                    else:
                        return result_container["result"]
            
            # Clear the message queue
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Process the query in the background
            def run_query():
                return self._run_in_loop(self.process_query_async(query, history))
            
            # Start processing
            result_container = {"result": None, "error": None}
            
            def query_thread():
                try:
                    result_container["result"] = run_query()
                except Exception as e:
                    result_container["error"] = str(e)
            
            thread = threading.Thread(target=query_thread)
            thread.start()
            
            # Monitor for tool calls while processing
            current_tool = None
            while thread.is_alive():
                try:
                    message_type, *args = self.message_queue.get(timeout=0.1)
                    
                    if message_type == "tool_start":
                        tool_name, input_str = args
                        current_tool = tool_name
                        display_input = input_str[:200] + "..." if len(input_str) > 200 else input_str
                        print(f"🔧 Using {tool_name} tool with input: {display_input}")
                    
                    elif message_type == "tool_end":
                        output = args[0]
                        if current_tool:
                            display_output = output[:300] + "..." if len(output) > 300 else output
                            print(f"🛠️ Tool '{current_tool}' returned: {display_output}")
                            current_tool = None
                    
                    elif message_type == "tool_error":
                        error = args[0]
                        if current_tool:
                            print(f"💥 Error in tool '{current_tool}': {error}")
                            current_tool = None
                
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing tool message: {e}")
                    continue
            
            # Wait for the query to complete
            thread.join()
            
            # Return the final response
            if result_container["error"]:
                return f"❌ Error: {result_container['error']}"
            else:
                return result_container["result"]
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"

    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            try:
                # MultiServerMCPClient doesn't have a close method, so we'll just clean up references
                self.mcp_client = None
            except Exception as e:
                logger.warning(f"Error cleaning up MCP client: {e}")
        
        # Stop the event loop
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.loop_thread:
                self.loop_thread.join(timeout=5)

    async def get_resource_content(self, server_name: str, resource_uri: str) -> str:
        """Get content from an MCP resource with enhanced error handling"""
        if not self.mcp_client:
            return "❌ MCP client not connected"
        
        try:
            logger.info(f"Attempting to fetch resource: {resource_uri}")
            
            # Add timeout and better error handling
            import asyncio
            resources = await asyncio.wait_for(
                self.mcp_client.get_resources(server_name, uris=[resource_uri]),
                timeout=30.0
            )
            
            if resources and len(resources) > 0:
                content = resources[0].data
                logger.info(f"Successfully fetched resource {resource_uri}, length: {len(content)}")
                return content
            else:
                error_msg = f"❌ Resource {resource_uri} not found or empty"
                logger.warning(error_msg)
                
                # Check for common typos and suggest corrections
                suggestions = self._get_resource_suggestions(resource_uri)
                if suggestions:
                    error_msg += f"\n\n💡 **Did you mean:**\n{suggestions}"
                
                return error_msg
                
        except asyncio.TimeoutError:
            error_msg = f"❌ Timeout while fetching resource {resource_uri} (30s)"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Error reading resource {resource_uri}: {str(e)}"
            logger.error(error_msg)
            
            # Check for common typos and suggest corrections
            suggestions = self._get_resource_suggestions(resource_uri)
            if suggestions:
                error_msg += f"\n\n💡 **Did you mean:**\n{suggestions}"
            
            # Provide helpful fallback information
            if "ddragon://" in resource_uri:
                return f"""{error_msg}

🔧 **Fallback Information:**
This resource provides League of Legends static game data from Riot's Data Dragon service.

📚 **Available Data Dragon Resources:**
- **ddragon://versions** - Game version information
- **ddragon://languages** - Supported languages
- **ddragon://champions** - All champion data summary
- **ddragon://champion_data** - Detailed champion information (sample: Ahri)
- **ddragon://items** - Complete items database
- **ddragon://summoner_spells** - Summoner spells data

⚠️ **Note:** Data Dragon resources require internet connectivity to fetch live data from Riot's CDN.
"""
            elif "constants://" in resource_uri:
                return f"""{error_msg}

🔧 **Fallback Information:**
This resource provides League of Legends game constants and reference data.

📚 **Available Constants Resources:**
- **constants://queues** - Queue types and IDs (Ranked, Normal, ARAM, etc.)
- **constants://maps** - Map information (Summoner's Rift, ARAM, etc.)
- **constants://game_modes** - Game mode details
- **constants://game_types** - Game type classifications
- **constants://seasons** - Season information
- **constants://ranked_tiers** - Ranking system details
- **constants://routing** - API routing information

✅ **Note:** Constants are static data and should work offline.
"""
            else:
                return error_msg

    def _get_resource_suggestions(self, resource_uri: str) -> str:
        """Get suggestions for common resource name typos"""
        suggestions = []
        
        # Common typos and corrections
        if "ranked_tier" in resource_uri and "ranked_tiers" not in resource_uri:
            corrected = resource_uri.replace("ranked_tier", "ranked_tiers")
            suggestions.append(f"- `{corrected}` (plural form)")
        
        if "champion:" in resource_uri:
            corrected = resource_uri.replace("champion:", "champion_data")
            suggestions.append(f"- `{corrected}` (use champion_data for detailed info)")
        
        if "queue:" in resource_uri:
            corrected = resource_uri.replace("queue:", "queues")
            suggestions.append(f"- `{corrected}` (use queues for all queue types)")
        
        # Check for missing protocol
        if not "://" in resource_uri:
            if any(word in resource_uri.lower() for word in ["champion", "item", "spell"]):
                suggestions.append(f"- `ddragon://{resource_uri}` (add ddragon protocol)")
            elif any(word in resource_uri.lower() for word in ["queue", "map", "mode", "tier", "season"]):
                suggestions.append(f"- `constants://{resource_uri}` (add constants protocol)")
        
        return "\n".join(suggestions) if suggestions else ""

    async def get_prompt_content(self, server_name: str, prompt_name: str, **kwargs) -> str:
        """Get content from an MCP prompt with arguments"""
        if not self.mcp_client:
            return "❌ MCP client not connected"
        
        try:
            messages = await self.mcp_client.get_prompt(server_name, prompt_name, arguments=kwargs)
            if messages:
                # Combine all message contents
                content = "\n".join([msg.content for msg in messages])
                return content
            else:
                return f"❌ Prompt {prompt_name} not found"
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_name}: {e}")
            return f"❌ Error getting prompt: {str(e)}"

    async def list_available_resources(self) -> List[dict]:
        """List all available MCP resources"""
        if not self.mcp_client:
            return []
        
        try:
            # Note: MultiServerMCPClient doesn't have a direct list_resources method
            # We'll need to use a session to get this info
            return []  # Will be populated during connection
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []

    async def list_available_prompts(self) -> List[dict]:
        """List all available MCP prompts"""
        if not self.mcp_client:
            return []
        
        try:
            # Note: MultiServerMCPClient doesn't have a direct list_prompts method
            # We'll need to use a session to get this info
            return []  # Will be populated during connection
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return [] 