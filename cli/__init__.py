"""
CLI Chatbots Package

This package contains command-line interface chatbot implementations.
Moved from app/services/ to organize CLI-specific functionality.
"""

from .chatbot_services import main, create_cli_interface

__all__ = ['main', 'create_cli_interface'] 