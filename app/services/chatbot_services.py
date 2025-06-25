from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.config import settings
from app.utils.logger import get_logger
from typing_extensions import Annotated, TypedDict
from typing import Sequence, Optional, Dict, Any, List
from langgraph.graph.message import add_messages
import asyncio
import subprocess

# Get module logger
logger = get_logger("chatbot_react_agent")

# Define custom state schema that extends the default AgentState
class ChatbotState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    remaining_steps: int  # Required by ReACT agent
    match: Optional[Dict[str, Any]]
    modelName: str
    language: str

# Custom prompt function that incorporates match context and language
def create_system_prompt(state: ChatbotState) -> List[BaseMessage]:
    """Create a system prompt with match context and language specification."""
    match = state.get("match", {})
    language = state.get("language", "English")
    
    base_prompt = f"""You are a League of Legends assistant. Answer the user's question about this active match directly and accurately.

Rules:
1. Read the user's question carefully
2. Answer ONLY what they asked
3. Use the match data if relevant
4. Be brief and accurate
5. Respond in {language}

{f"Match data available: {match}" if match else "No match data provided."}

Answer the user's question directly."""
    
    # Return system message + existing messages from state
    system_message = SystemMessage(content=base_prompt)
    messages = state.get("messages", [])
    return [system_message] + list(messages)

# Initialize in-memory message history
memory = MemorySaver()

# MCP server connection management
mcp_client = None
mcp_tools = []

async def initialize_mcp_connection():
    """Initialize connection to the league-mcp server on stdio."""
    global mcp_client, mcp_tools
    try:
        logger.info("Initializing MCP connection to league-mcp server")
        
        # Check if league-mcp command is available
        import shutil
        league_mcp_path = shutil.which("league-mcp")
        
        # Create MCP client with league-mcp server configuration
        config = {
            "league-mcp": {
                "command": "league-mcp",  # Using the installed pip package
                "args": [],  # Arguments for the command
                "transport": "stdio",  # Specify the transport type
                "env": {
                    "RIOT_API_KEY": settings.riot_api_key
                }
            }
        }
        
        mcp_client = MultiServerMCPClient(config)
        
        # Get available tools from the MCP server
        mcp_tools = await mcp_client.get_tools()
        
        logger.info(f"Successfully connected to league-mcp MCP server. Available tools: {[tool.name for tool in mcp_tools]}")
        
    except Exception as e:
        logger.error(f"Failed to connect to league-mcp MCP server: {type(e).__name__}: {str(e)}")
        mcp_tools = []  # Fallback to empty tools list

def get_mcp_tools():
    """Get the current MCP tools, initializing connection if needed."""
    global mcp_tools
    
    if mcp_tools is None or len(mcp_tools) == 0:
        # Try to initialize connection synchronously
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # If we're already in an async context, we can't run another event loop
                logger.warning("Already in async context, MCP tools may not be available immediately")
                return []
            except RuntimeError:
                # No running event loop, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(initialize_mcp_connection())
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Failed to get MCP tools: {e}")
            return []
    
    return mcp_tools

# Counter to track ReACT agent iterations
iteration_counters = {}

def post_model_logging_hook(state: ChatbotState) -> Dict[str, Any]:
    """Hook that logs after each model call in the ReACT agent loop."""
    thread_id = "unknown"  # We don't have direct access to thread_id in the hook
    
    # Get the current iteration count for this state
    state_key = str(hash(str(state.get("messages", []))))
    if state_key not in iteration_counters:
        iteration_counters[state_key] = 0
    iteration_counters[state_key] += 1
    
    current_iteration = iteration_counters[state_key]
    remaining_steps = state.get("remaining_steps", 0)
    
    # Get the last message to see what the agent just did
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            has_tool_calls = hasattr(last_message, 'tool_calls') and last_message.tool_calls
            content_preview = (last_message.content[:100] + "...") if len(last_message.content) > 100 else last_message.content
            
            logger.info(
                f"ReACT Agent Iteration {current_iteration}",
                extra={
                    "iteration": current_iteration,
                    "remaining_steps": remaining_steps,
                    "has_tool_calls": has_tool_calls,
                    "tool_calls_count": len(last_message.tool_calls) if has_tool_calls else 0,
                    "response_preview": content_preview,
                    "language": state.get("language", "en"),
                    "model": state.get("modelName", "unknown")
                }
            )
            
            # Log tool calls if any
            if has_tool_calls:
                for i, tool_call in enumerate(last_message.tool_calls):
                    logger.info(
                        f"Tool Call {i+1}: {tool_call.get('name', 'unknown')}",
                        extra={
                            "iteration": current_iteration,
                            "tool_name": tool_call.get('name', 'unknown'),
                            "tool_args": tool_call.get('args', {}),
                            "tool_id": tool_call.get('id', 'unknown')
                        }
                    )
    
    # Return empty dict since we're not modifying state
    return {}

# Create the ReACT agent
def create_chatbot_agent(model_name: str = "gemini-2.0-flash"):
    """Create a ReACT agent for the chatbot with MCP tools."""
    model = llm.get(model_name)
    
    # Get MCP tools from the league-mcp server (use cached tools)
    tools = mcp_tools if mcp_tools else []
    
    logger.info(f"Creating ReACT agent with {len(tools)} MCP tools: {[tool.name for tool in tools] if tools else 'No tools available'}")
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=create_system_prompt,
        state_schema=ChatbotState,
        checkpointer=memory,
        debug=True
    )
    
    return agent

# Global agent instance (will be created when first used)
_agent_cache = {}

def get_agent(model_name: str = "gemini-2.0-flash"):
    """Get or create an agent for the specified model."""
    if model_name not in _agent_cache:
        _agent_cache[model_name] = create_chatbot_agent(model_name)
    return _agent_cache[model_name]

# Function to handle chatbot requests with language support
def handle_chatbot_request(thread_id: str, query: str, match: dict = None, modelName="gemini-1.5-flash", language="English"):
    """Handle chatbot requests using the ReACT agent."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        agent = get_agent(modelName)
        
        # Prepare the state with all required fields
        state = {
            "messages": [HumanMessage(content=query)],
            "remaining_steps": 25,  # Default number of steps for ReACT agent
            "match": match or {},
            "modelName": modelName,
            "language": language
        }
        
        logger.info(f"Starting ReACT agent conversation for thread {thread_id}")
        logger.info(f"Language: {language}, Model: {modelName}, Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        # Note: MCP connection will be established on startup
        # For now, we'll use the cached tools or fallback to empty list
        current_tools = mcp_tools if mcp_tools else []
        logger.info(f"Available MCP tools for this conversation: {len(current_tools)}")
        
        # Reset iteration counter for this new conversation
        state_key = str(hash(str(state.get("messages", []))))
        if state_key in iteration_counters:
            del iteration_counters[state_key]
        
        # Stream the agent response
        stream = agent.stream(state, config, stream_mode="messages")
        
        # Wrap the stream to add completion logging and iteration tracking
        def logged_stream():
            total_chunks = 0
            iteration_count = 0
            for chunk in stream:
                total_chunks += 1
                
                # Log response chunks
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    content_preview = content[:100] + "..." if len(content) > 100 else content
                    logger.debug(f"Agent chunk {total_chunks}: {content_preview}")
                
                yield chunk
                
            logger.info(f"ReACT agent completed for thread {thread_id}. Total chunks: {total_chunks}")
        
        return logged_stream()
        
    except Exception as e:
        logger.error(f"Error in handle_chatbot_request: {e}")
        return "An error occurred while processing your request. Please try again later."

# Startup function to initialize MCP connection
async def startup_mcp_connection():
    """Initialize MCP connection on application startup."""
    try:
        await initialize_mcp_connection()
        logger.info("MCP connection initialized successfully on startup")
        
        # Log available tools
        if mcp_tools:
            logger.info(f"Available MCP tools on startup: {len(mcp_tools)} tools - {[tool.name for tool in mcp_tools]}")
        else:
            logger.warning("No MCP tools available - league-mcp server may not be running or 'league-mcp' command not in PATH")
            
    except Exception as e:
        logger.error(f"Failed to initialize MCP connection on startup: {e}")

# Function to gracefully close MCP connection
async def shutdown_mcp_connection():
    """Close MCP connection on application shutdown."""
    global mcp_client
    try:
        if mcp_client:
            # MCP client cleanup (if close method exists)
            if hasattr(mcp_client, 'close'):
                await mcp_client.close()
            logger.info("MCP connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing MCP connection: {e}")
