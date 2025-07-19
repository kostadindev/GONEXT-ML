import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
import threading
import queue

from app.agents.chatbot_agent import ChatbotAgent
from app.utils.logger import get_logger

logger = get_logger("chatbot_services")

_chatbot_agent: Optional[ChatbotAgent] = None


async def startup_mcp_connection():
    global _chatbot_agent
    
    try:
        logger.info("Initializing ChatbotAgent and MCP connection...")
        _chatbot_agent = ChatbotAgent()
        
        _chatbot_agent._start_event_loop()
        
        await _chatbot_agent.connect_to_server()
        logger.info("MCP connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP connection: {e}")
        raise


async def shutdown_mcp_connection():
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
        
        while not _chatbot_agent.message_queue.empty():
            try:
                _chatbot_agent.message_queue.get_nowait()
            except queue.Empty:
                break
        
        result_container = {"result": None, "error": None, "completed": False}
        
        def run_query_async():
            try:
                history = []
                result = _chatbot_agent._run_in_loop(
                    _chatbot_agent.process_query_async(query, history, match)
                )
                result_container["result"] = result
                result_container["completed"] = True
            except Exception as e:
                result_container["error"] = str(e)
                result_container["completed"] = True
        
        query_thread = threading.Thread(target=run_query_async)
        query_thread.start()
        
        current_tool = None
        tool_messages_sent = []
        
        while not result_container["completed"]:
            try:
                message_type, *args = _chatbot_agent.message_queue.get(timeout=0.5)
                
                if message_type == "tool_start":
                    tool_name, input_str = args
                    current_tool = tool_name
                    import json
                    try:
                        input_data = json.loads(input_str)
                        formatted_input = json.dumps(input_data, indent=2)
                    except:
                        formatted_input = f'"{input_str}"'
                    
                    tool_msg = f"@tool[{tool_name}]{{\n{formatted_input}\n}}\n\n"
                    tool_messages_sent.append(tool_msg)
                    yield tool_msg
                
                elif message_type == "tool_end":
                    output = args[0]
                    if current_tool:
                        import json
                        try:
                            output_data = json.loads(output)
                            formatted_output = json.dumps(output_data, indent=2)
                        except:
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
                continue
            except Exception as e:
                logger.error(f"Error processing tool message: {e}")
                continue
        
        query_thread.join(timeout=30)
        
        if result_container["error"]:
            yield f"\n❌ Error processing request: {result_container['error']}"
            return
        
        if not result_container["result"]:
            yield "\n❌ No response generated."
            return
        
        final_response = result_container["result"]
        
        if tool_messages_sent:
            yield "\n" + "="*50 + "\n"
        
        chunk_size = 100
        for i in range(0, len(final_response), chunk_size):
            chunk = final_response[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.01)
            
    except Exception as e:
        logger.error(f"Error processing chatbot request: {e}")
        yield f"❌ Error processing request: {str(e)}"


def get_chatbot_agent() -> Optional[ChatbotAgent]:
    return _chatbot_agent