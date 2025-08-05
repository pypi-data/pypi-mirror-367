# Uber Central MCP Server

This is a Model Context Protocol (MCP) server that provides access to the Uber Central API functionality. It allows LLMs like Claude to interact with the Uber Central service to manage ride bookings, get estimates, and track usage.

## Features

The MCP server exposes the following tools:

### User Management
- **initialize_user**: Create a new client account and get a client_id
- **get_client_stats**: Get usage statistics for a specific client
- **get_usage_history**: Get detailed API usage history
- **get_ride_history**: Get complete ride booking history

### Ride Operations
- **get_estimates**: Get ride price estimates for all available vehicle types
- **book_ride**: Book an immediate Uber ride
- **schedule_ride**: Schedule an Uber ride for future pickup
- **get_ride_status**: Get current ride status and driver details
- **cancel_ride**: Cancel an existing ride

### System
- **health_check**: Check API service health and connectivity

## Prerequisites

- Python 3.10 or higher
- Uber Central API key
- `uv` package manager

## Installation

1. Clone or download this directory
2. Install dependencies:
```bash
uv sync
```

3. Set your API key:
   - Set environment variable: `export UBER_CENTRAL_API_KEY="your-api-key-here"`
   - This is **required** - the server will not start without a valid API key

## Usage

### Testing the Server

Run the server directly to test:
```bash
uv run uber_central_mcp_server.py
```

The server will start and wait for MCP protocol messages on stdin/stdout.

### Using with Claude Desktop

Add this configuration to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "uber-central": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/uber_central/uber-central-mcp",
        "run",
        "uber_central_mcp_server.py"
      ],
      "env": {
        "UBER_CENTRAL_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Important**: Replace `/ABSOLUTE/PATH/TO/uber_central/uber-central-mcp` with the actual absolute path to this directory.

### Using with Other MCP Clients

This server follows the standard MCP protocol and can be used with any compatible MCP client.

## Example Usage

Once connected to Claude Desktop, you can ask natural language questions like:

- "Create a new user account for John Doe with email john@example.com"
- "Get ride estimates from Union Square San Francisco to SFO Airport for 2 passengers"
- "Book an immediate ride from 123 Market St to 456 Mission St for Sarah Johnson, phone 5551234567"
- "Schedule a ride for tomorrow at 3 PM from my office to the airport"
- "What's the status of ride abc-123-def?"
- "Show me the ride history for client xyz-456-789"
- "Check if the Uber Central API is healthy"

## API Configuration

The server connects to the Uber Central API endpoint configured in your deployment. This provides the following capabilities:
- Enterprise-grade ride management
- User tracking and analytics
- Comprehensive audit trails
- Real-time ride status tracking

## Security

- API keys are passed via environment variables or secure configuration
- All requests use Bearer token authentication
- The server validates all inputs and handles errors gracefully
- No sensitive data is logged to stdout (MCP protocol requirement)

## Development

To modify or extend the server:

1. Edit `uber_central_mcp_server.py`
2. Add new tools using the `@mcp.tool()` decorator
3. Follow the fastMCP pattern for type hints and docstrings
4. Test with `uv run uber_central_mcp_server.py`

## Troubleshooting

### Server Not Connecting
- Check that the absolute path in Claude Desktop config is correct
- Verify the API key is set correctly
- Check Claude Desktop logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

### API Errors
- Verify the API key is valid and not expired
- Check if the Uber Central API is healthy using the health_check tool
- Ensure client_ids are valid (created with initialize_user)

### Tool Failures
- Most tools require a valid client_id from initialize_user
- Phone numbers should be 10 digits (US format)
- Addresses should be specific and valid locations
- Pickup times for scheduling should be in ISO 8601 format

## License

This MCP server is part of the Uber Central project.
