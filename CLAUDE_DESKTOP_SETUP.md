# Setting Up Tamil Panchang MCP Server with Claude Desktop

This guide will help you connect Claude Desktop to your Tamil Panchang MCP server.

## Prerequisites

- Claude Desktop application installed on your computer
- Your MCP server deployed and running at: `https://panchang.karthikwrites.com/mcp/sse`

## Configuration Steps

### 1. Locate the Claude Desktop Configuration File

The configuration file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Edit the Configuration File

Open the `claude_desktop_config.json` file in your text editor. If the file doesn't exist, create it.

Add the Tamil Panchang MCP server configuration:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "url": "https://panchang.karthikwrites.com/mcp/sse",
      "description": "Tamil Panchang calculations for any date and location"
    }
  }
}
```

**If you already have other MCP servers configured**, add the Tamil Panchang server to the existing list:

```json
{
  "mcpServers": {
    "existing-server": {
      "url": "https://example.com/sse"
    },
    "tamil-panchang": {
      "url": "https://panchang.karthikwrites.com/mcp/sse",
      "description": "Tamil Panchang calculations for any date and location"
    }
  }
}
```

### 3. Restart Claude Desktop

After saving the configuration file:
1. Completely quit Claude Desktop (not just close the window)
2. Restart Claude Desktop
3. The MCP server should now be available

### 4. Verify the Connection

In Claude Desktop, you should see an indicator that the MCP server is connected (usually a small icon or status message).

Try asking Claude:
- *"What's today's panchang in Chennai?"*
- *"Get the panchang for January 1st, 2025 in Chennai (13.0827 N, 80.2707 E)"*
- *"Calculate today's panchang for my location in Mumbai (19.0760 N, 72.8777 E)"*

## Available Tools

Once connected, Claude will have access to these tools:

### 1. `get_panchang`
Calculate Tamil Panchang for a specific date and location.

**Parameters:**
- `date` (required): Date in YYYY-MM-DD format (e.g., "2025-01-15")
- `latitude` (required): Latitude (-90 to +90)
- `longitude` (required): Longitude (-180 to +180)
- `timezone` (optional): UTC offset in hours (default: 5.5 for IST)

### 2. `get_today_panchang`
Get today's Tamil Panchang for a specified location.

**Parameters:**
- `latitude` (required): Latitude (-90 to +90)
- `longitude` (required): Longitude (-180 to +180)
- `timezone` (optional): UTC offset in hours (default: 5.5 for IST)

## Example Queries

Here are some example questions you can ask Claude:

1. **Today's panchang:**
   - "What's today's panchang in Chennai?"
   - "Show me today's Tamil panchang for Bangalore"
   - "Get today's nakshatra and tithi for Coimbatore"

2. **Specific date:**
   - "What was the panchang on January 26, 2025 in Chennai?"
   - "Get the panchang for Pongal 2025 in Tamil Nadu"
   - "Show me the sunrise and sunset times for December 25, 2024 in Mumbai"

3. **Inauspicious timings:**
   - "What's the Rahu Kalam today in Chennai?"
   - "When should I avoid starting new work today in Bangalore?"
   - "Show me all inauspicious timings for tomorrow in Coimbatore"

4. **Custom locations:**
   - "Get today's panchang for latitude 11.0168 and longitude 76.9558" (Coimbatore)
   - "Calculate panchang for 13.0827 N, 80.2707 E on January 14, 2025"

## Troubleshooting

### MCP Server Not Connecting

1. **Verify the server is running:**
   ```bash
   curl https://panchang.karthikwrites.com/mcp/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "service": "tamil-panchang-mcp",
     "endpoints": {
       "sse": "/sse",
       "messages": "/messages/",
       "health": "/health"
     }
   }
   ```

2. **Check the SSE endpoint:**
   ```bash
   # Run the test script (requires Python and requests library)
   python test_sse_endpoint.py https://panchang.karthikwrites.com/mcp/sse
   ```

3. **Verify JSON syntax:**
   - Make sure your `claude_desktop_config.json` is valid JSON
   - Use a JSON validator: https://jsonlint.com/

4. **Check Claude Desktop logs:**
   - On macOS: `~/Library/Logs/Claude/`
   - On Windows: `%APPDATA%\Claude\logs\`
   - On Linux: `~/.config/Claude/logs/`

### Common Issues

**Issue: "Server not found" or "Connection failed"**
- Solution: Verify the URL is correct and the server is accessible
- Test with: `curl https://panchang.karthikwrites.com/mcp/health`

**Issue: "Invalid configuration"**
- Solution: Check JSON syntax in `claude_desktop_config.json`
- Make sure all brackets and commas are correct

**Issue: "Tools not available"**
- Solution: Restart Claude Desktop completely
- Wait a few seconds for the connection to establish

## Advanced Configuration

### Using Local Development Server

If you're running the server locally for development:

```json
{
  "mcpServers": {
    "tamil-panchang-local": {
      "url": "http://localhost:8001/sse",
      "description": "Tamil Panchang (Local Dev)"
    }
  }
}
```

### Multiple Environments

You can configure both production and local servers:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "url": "https://panchang.karthikwrites.com/mcp/sse",
      "description": "Tamil Panchang (Production)"
    },
    "tamil-panchang-local": {
      "url": "http://localhost:8001/sse",
      "description": "Tamil Panchang (Local Dev)"
    }
  }
}
```

## API Rate Limits

The public API has rate limiting configured:
- **100 requests per minute** per IP address
- **Burst capacity**: 50 requests

This should be more than sufficient for personal use with Claude Desktop.

## Data Privacy

- All calculations are performed server-side
- No personal data is stored
- Requests contain only: date, latitude, longitude, timezone
- Server logs may contain IP addresses (standard web server logs)

## Support

For issues or questions:
- GitHub Issues: https://github.com/karthiknitt/tamil-panchang-api/issues
- Test endpoint: `python test_sse_endpoint.py`
- Check logs: `docker-compose logs mcp`

## Example Conversation

Here's what a typical conversation might look like:

**You:** "What's today's panchang in Chennai?"

**Claude:** *[Uses get_today_panchang tool with Chennai coordinates]*

"Here's today's Tamil Panchang for Chennai:

📅 Date: 2025-11-29
📍 Location: 13.0827°N, 80.2707°E (Timezone: UTC+5.5)

🌙 Panchang Elements:
  Weekday: சனி (Saturday)
  Tithi: சதுர்த்தி
  Nakshatra: உத்திரம்
  Yoga: வ்ரித்தி
  Karana: கரஜா
  Tamil Month: கார்த்திகை

☀️ Sun Timings:
  Sunrise: 06:12 AM
  Sunset: 05:43 PM

⚠️ Inauspicious Timings (Avoid for important activities):
  Rahu Kalam: 09:00 AM - 10:30 AM
  Yamagandam: 01:30 PM - 03:00 PM
  Gulikai Kalam: 06:00 AM - 07:30 AM"

---

That's it! You're now ready to use the Tamil Panchang MCP server with Claude Desktop.
