# League of Legends Builds MCP CLI

A command-line interface for fetching League of Legends champion build information using MCP (Model Context Protocol) and Gemini AI.

## Features

- **Build Information**: Get detailed build analysis including core items, boots, situational items, and build orders
- **Champion Statistics**: Get champion statistics like win rate, pick rate, ban rate, and tier
- **Gemini AI Integration**: Uses Gemini to extract and format information from OP.GG HTML
- **File Output**: Save build information to text files
- **Multiple Output Modes**: Get build info, stats, or both

## Installation

1. Ensure you have the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

### Basic Usage

Get build information for a champion:
```bash
python cli/builds_mcp_cli.py jinx
```

Get champion statistics:
```bash
python cli/builds_mcp_cli.py yasuo --stats
```

Get both build information and statistics:
```bash
python cli/builds_mcp_cli.py ahri --both
```

Save build information to a file:
```bash
python cli/builds_mcp_cli.py jinx --output jinx_build.txt
```

### Command Line Options

- `champion`: Champion name (e.g., jinx, yasuo, ahri)
- `--stats`: Get champion statistics instead of build information
- `--both`: Get both build information and statistics
- `--output OUTPUT, -o OUTPUT`: Save output to specified file
- `--version, -v`: Show program version
- `--help, -h`: Show help message

### Examples

```bash
# Get build info for Jinx
python cli/builds_mcp_cli.py jinx

# Get stats for Yasuo
python cli/builds_mcp_cli.py yasuo --stats

# Save Ahri build info to file
python cli/builds_mcp_cli.py ahri --output ahri_build.txt

# Get both build info and stats for Jinx
python cli/builds_mcp_cli.py jinx --both
```

## Output Format

### Build Information
The CLI provides structured build information including:
- **Core Items**: Most popular item combinations with pick rates and win rates
- **Boots**: Recommended boots with statistics
- **Situational Items**: Items built in 4th and 5th slots
- **Item Build Order**: Typical build progression
- **Win Rates**: Performance metrics for different builds
- **Key Statistics**: Analysis of item effectiveness

### Champion Statistics
Basic champion statistics including:
- Patch version
- Position/role
- Tier ranking
- Games played
- Win rate, pick rate, ban rate

## Requirements

- Python 3.8+
- Gemini API key
- Internet connection for OP.GG data fetching
- Required Python packages (see requirements.txt)

## Error Handling

The CLI includes comprehensive error handling for:
- Network connectivity issues
- Invalid champion names
- API key configuration problems
- File I/O errors

## Notes

- Champion names are case-insensitive
- Data is sourced from OP.GG and processed using Gemini AI
- Build information is extracted from current meta data
- Statistics are based on recent patch data 