# Weather MCP Server

An MCP server that gives AI models access to real-time weather data using the [Open-Meteo API](https://open-meteo.com/) — **completely free, no API key required**.

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather` | Current conditions for any city |
| `get_weather_forecast` | 1–7 day forecast |
| `compare_cities_weather` | Side-by-side comparison of up to 5 cities |

## Run It

### Option 1: Inspector (Recommended for Testing)
```bash
cd 04-intermediate/03-weather-server
mcp dev weather_server.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Open the interactive inspector in your browser
4. Display all available weather tools

In the inspector:
- Test weather queries for any city
- Get current conditions and forecasts
- Compare weather across cities
- View full API responses
- No API key needed (uses Open-Meteo free API)
- Stop with `Ctrl+C`

### Option 2: Start as Server (Integration)
```bash
cd 04-intermediate/03-weather-server
python weather_server.py
```

This starts the server on stdio transport, ready for a client like Claude Desktop to connect.

## Example Prompts

- "What's the weather in Tokyo right now?"
- "Give me a 5-day forecast for London"
- "Compare the weather in New York, Paris, and Sydney"
- "Is it raining in Seattle?"
- "What should I pack for a trip to Dubai tomorrow?"

## Key Patterns Demonstrated

1. **External API integration** — Calling REST APIs from MCP tools
2. **Async HTTP** — Using `httpx.AsyncClient` for non-blocking requests
3. **Multi-step tools** — Geocoding city → fetching weather
4. **Error handling** — Graceful messages when city not found or API fails
5. **Data transformation** — Converting WMO codes to human-readable conditions
