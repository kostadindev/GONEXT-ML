#!/usr/bin/env python3
"""
CLI tool for League of Legends champion build information using MCP.
"""

import asyncio
import sys
import os
import argparse
from typing import Optional

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.mcp.builds_mcp import get_champion_build, get_champion_stats


async def get_build_info(champion: str, output_file: Optional[str] = None) -> str:
    """Get build information for a champion."""
    print(f"🔍 Fetching build information for {champion.title()}...")
    
    try:
        # Get the extracted build information
        build_info = await get_champion_build(champion)
        
        # Print the information
        print(f"\n📊 Build Information for {champion.title()}:")
        print("=" * 60)
        print(build_info)
        print("=" * 60)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(build_info)
            print(f"\n💾 Build information saved to: {output_file}")
        
        return build_info
        
    except Exception as e:
        error_msg = f"❌ Error getting build information for {champion}: {str(e)}"
        print(error_msg)
        return error_msg


async def get_champion_statistics(champion: str) -> str:
    """Get champion statistics."""
    print(f"📈 Fetching statistics for {champion.title()}...")
    
    try:
        stats_result = await get_champion_stats(champion)
        
        print(f"\n📊 Statistics for {champion.title()}:")
        print("=" * 60)
        print(stats_result)
        print("=" * 60)
        
        return stats_result
        
    except Exception as e:
        error_msg = f"❌ Error getting statistics for {champion}: {str(e)}"
        print(error_msg)
        return error_msg


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="League of Legends Champion Build Information CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python builds_mcp_cli.py jinx                    # Get build info for Jinx
  python builds_mcp_cli.py yasuo --stats          # Get stats for Yasuo
  python builds_mcp_cli.py ahri --output ahri.txt # Save build info to file
  python builds_mcp_cli.py jinx --both            # Get both build info and stats
        """
    )
    
    parser.add_argument(
        "champion",
        help="Champion name (e.g., jinx, yasuo, ahri)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Get champion statistics instead of build information"
    )
    
    parser.add_argument(
        "--both",
        action="store_true",
        help="Get both build information and statistics"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Save output to specified file"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="builds_mcp_cli v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Normalize champion name
    champion = args.champion.lower().strip()
    
    print("🎮 League of Legends Builds MCP CLI")
    print("=" * 50)
    
    try:
        if args.both:
            # Get both build info and stats
            print("📋 Getting both build information and statistics...\n")
            
            # Get build info
            build_info = await get_build_info(champion, args.output)
            
            print("\n" + "=" * 50 + "\n")
            
            # Get stats
            stats = await get_champion_statistics(champion)
            
        elif args.stats:
            # Get only statistics
            stats = await get_champion_statistics(champion)
            
        else:
            # Get only build info (default)
            build_info = await get_build_info(champion, args.output)
        
        print("\n✅ Operation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 