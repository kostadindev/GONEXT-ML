import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
import threading
import queue

from app.agents.chatbot_agent import ChatbotAgent
from app.utils.logger import get_logger

# Get module logger
logger = get_logger("chatbot_services")

# Global chatbot agent instance
_chatbot_agent: Optional[ChatbotAgent] = None


async def startup_mcp_connection():
    """Initialize the MCP connection during application startup."""
    global _chatbot_agent
    
    try:
        logger.info("Initializing ChatbotAgent and MCP connection...")
        _chatbot_agent = ChatbotAgent()
        
        # Start the persistent event loop
        _chatbot_agent._start_event_loop()
        
        # Connect to MCP server
        await _chatbot_agent.connect_to_server()
        logger.info("MCP connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP connection: {e}")
        raise


async def shutdown_mcp_connection():
    """Shutdown the MCP connection during application shutdown."""
    global _chatbot_agent
    
    try:
        if _chatbot_agent:
            logger.info("Shutting down MCP connection...")
            await _chatbot_agent.cleanup()
            _chatbot_agent = None
            logger.info("MCP connection shutdown completed")
    except Exception as e:
        logger.error(f"Error during MCP connection shutdown: {e}")


async def handle_chatbot_request(
    thread_id: str,
    query: str,
    modelName: str,
    match: Optional[Dict] = None,
    language: str = "en"
) -> AsyncGenerator[str, None]:
    """
    Handle chatbot request and yield response chunks with real-time tool updates.
    
    Args:
        thread_id: The conversation thread ID
        query: The user query
        modelName: The model name to use
        match: Optional match data
        language: The response language
        
    Yields:
        Response chunks from the chatbot including tool call updates
    """
    global _chatbot_agent
    
    if not _chatbot_agent:
        logger.error("ChatbotAgent not initialized")
        yield "❌ Chatbot service not available. Please try again later."
        return
    
    if not _chatbot_agent.is_connected:
        logger.error("ChatbotAgent not connected to MCP server")
        yield "❌ Chatbot service not connected. Please try again later."
        return
    
    try:
        logger.info(f"Processing chatbot request for thread {thread_id}")
        
        # Clear the message queue to ensure we get fresh tool call updates
        while not _chatbot_agent.message_queue.empty():
            try:
                _chatbot_agent.message_queue.get_nowait()
            except queue.Empty:
                break
        
        # Start processing the query asynchronously
        result_container = {"result": None, "error": None, "completed": False}
        
        def run_query_async():
            try:
                # Convert history for this thread (empty for now, could be expanded)
                history = []
                result = _chatbot_agent._run_in_loop(
                    _chatbot_agent.process_query_async(query, history, match)
                )
                result_container["result"] = result
                result_container["completed"] = True
            except Exception as e:
                result_container["error"] = str(e)
                result_container["completed"] = True
        
        # Start the query processing in a background thread
        query_thread = threading.Thread(target=run_query_async)
        query_thread.start()
        
        # Monitor for tool calls and provide real-time updates
        current_tool = None
        tool_messages_sent = []
        
        while not result_container["completed"]:
            try:
                # Check for tool call messages with timeout
                message_type, *args = _chatbot_agent.message_queue.get(timeout=0.5)
                
                if message_type == "tool_start":
                    tool_name, input_str = args
                    current_tool = tool_name
                    # Format input as JSON-like structure for the custom markdown
                    import json
                    try:
                        # Try to parse as JSON first
                        input_data = json.loads(input_str)
                        formatted_input = json.dumps(input_data, indent=2)
                    except:
                        # If not JSON, wrap in quotes
                        formatted_input = f'"{input_str}"'
                    
                    tool_msg = f"@tool[{tool_name}]{{\n{formatted_input}\n}}\n\n"
                    tool_messages_sent.append(tool_msg)
                    yield tool_msg
                
                elif message_type == "tool_end":
                    output = args[0]
                    if current_tool:
                        # Format output as JSON-like structure
                        import json
                        try:
                            # Try to parse as JSON first
                            output_data = json.loads(output)
                            formatted_output = json.dumps(output_data, indent=2)
                        except:
                            # If not JSON, wrap in quotes and truncate if too long
                            display_output = output[:150] + "..." if len(output) > 150 else output
                            formatted_output = f'"{display_output}"'
                        
                        tool_msg = f"@tool[{current_tool}.result]{{\n{formatted_output}\n}}\n\n"
                        tool_messages_sent.append(tool_msg)
                        yield tool_msg
                        current_tool = None
                
                elif message_type == "tool_error":
                    error = args[0]
                    if current_tool:
                        tool_msg = f"@tool[{current_tool}.error]{{\n  \"error\": \"{error}\"\n}}\n\n"
                        tool_messages_sent.append(tool_msg)
                        yield tool_msg
                        current_tool = None
            
            except queue.Empty:
                # No tool messages, continue waiting
                continue
            except Exception as e:
                logger.error(f"Error processing tool message: {e}")
                continue
        
        # Wait for the query thread to complete
        query_thread.join(timeout=30)  # 30 second timeout
        
        if result_container["error"]:
            yield f"\n❌ Error processing request: {result_container['error']}"
            return
        
        if not result_container["result"]:
            yield "\n❌ No response generated."
            return
        
        # Yield the final response
        final_response = result_container["result"]
        
        # Add a separator if we sent tool messages
        if tool_messages_sent:
            yield "\n" + "="*50 + "\n"
        
        # Stream the final response in chunks
        chunk_size = 100
        for i in range(0, len(final_response), chunk_size):
            chunk = final_response[i:i + chunk_size]
            yield chunk
            # Small delay to simulate more natural streaming
            await asyncio.sleep(0.01)
            
    except Exception as e:
        logger.error(f"Error processing chatbot request: {e}")
        yield f"❌ Error processing request: {str(e)}"


def get_chatbot_agent() -> Optional[ChatbotAgent]:
    """Get the global chatbot agent instance."""
    return _chatbot_agent