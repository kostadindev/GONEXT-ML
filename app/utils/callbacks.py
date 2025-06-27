import logging
import queue
from typing import Optional
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

class ToolCallLogger(BaseCallbackHandler):
    """Custom callback handler to log tool calls"""
    
    def __init__(self, message_queue: Optional[queue.Queue] = None):
        super().__init__()
        self.message_queue = message_queue
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        """Log when a tool starts executing"""
        tool_name = serialized.get("name", "Unknown")
        
        if self.message_queue:
            self.message_queue.put(("tool_start", tool_name, input_str))
        
        logger.info(f"Tool started: {tool_name} with input: {input_str}")
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Log when a tool finishes executing"""
        if self.message_queue:
            self.message_queue.put(("tool_end", output))
            
        logger.info(f"Tool completed with output: {output[:200]}...")
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Log when a tool encounters an error"""
        if self.message_queue:
            self.message_queue.put(("tool_error", str(error)))
            
        logger.error(f"Tool error: {error}") 