#!/usr/bin/env python3
"""
Example usage of the get_champion_build function that returns the full HTML body.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.mcp.builds_mcp import get_champion_build, get_champion_stats


async def main():
    """Example usage of the champion build functions."""
    
    champion = "jinx"
    
    print(f"=== Example: Getting {champion.title()} Build Data ===\n")
    
    # Get the Item Builds section HTML for the champion
    print("1. Getting Item Builds section HTML:")
    print("-" * 40)
    html_result = await get_champion_build(champion)
    print(f"HTML length: {len(html_result)} characters")
    print(f"First 500 characters: {html_result[:500]}...")
    
    # Write HTML to file
    filename = f"{champion}_item_builds.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_result)
    print(f"HTML saved to: {filename}")
    print()
    
    # Get parsed statistics for comparison
    print("2. Getting parsed statistics:")
    print("-" * 40)
    stats_result = await get_champion_stats(champion)
    print(stats_result)
    print()
    
    print("=== Usage Notes ===")
    print("- get_champion_build() returns the Item Builds section HTML")
    print("- get_champion_stats() returns parsed, formatted statistics")
    print("- Both functions accept champion names (e.g., 'jinx', 'yasuo', 'ahri')")
    print(f"- HTML content is saved to {filename} for inspection")


if __name__ == "__main__":
    asyncio.run(main()) 