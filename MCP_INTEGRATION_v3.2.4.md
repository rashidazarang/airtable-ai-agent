# MCP Integration Guide - v3.2.4

## Overview
This guide documents the integration between `airtable-ai-agent` and `airtable-mcp` v3.2.4, which includes critical security fixes and architectural improvements.

## What's New in v3.2.4

### Security Fixes
- ✅ **XSS Protection**: Complete fix for Cross-Site Scripting vulnerabilities in OAuth2 endpoints
- ✅ **Command Injection**: Full resolution of command injection vulnerabilities in Python test client
- ✅ **Input Validation**: Comprehensive validation across all user inputs
- ✅ **Unicode Escaping**: Proper character escaping in JSON contexts

### Architecture Improvements
- ✅ **TypeScript Fixed**: Proper separation of types and runtime code
- ✅ **World-Class Organization**: Restructured with src/typescript, src/javascript, src/python
- ✅ **NPM Package**: Available as `@rashidazarang/airtable-mcp` on NPM

## Installation Methods

### Method 1: NPM Global Install (Recommended)
```bash
# Install the MCP server globally
npm install -g @rashidazarang/airtable-mcp@3.2.4

# Start the MCP server
AIRTABLE_TOKEN="your_token" \
AIRTABLE_BASE_ID="your_base" \
npx @rashidazarang/airtable-mcp
```

### Method 2: Docker Compose (Production)
```bash
# The docker-compose.yml is pre-configured to use v3.2.4
docker-compose up -d

# This will:
# 1. Build the MCP server from Dockerfile.mcp (using NPM v3.2.4)
# 2. Start the AI agent
# 3. Connect them via Docker network
```

### Method 3: Local Development
```bash
# Install as dependency
npm install @rashidazarang/airtable-mcp@3.2.4

# Or clone and build from source
git clone https://github.com/rashidazarang/airtable-mcp.git
cd airtable-mcp
npm install
npm run build  # For TypeScript version
```

## Configuration

### Environment Variables
```bash
# Required
AIRTABLE_TOKEN=your_personal_access_token
AIRTABLE_BASE_ID=your_base_id

# Optional
MCP_SERVER_URL=http://localhost:8010/mcp  # Default
LOG_LEVEL=INFO  # DEBUG, INFO, WARN, ERROR
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "airtable-mcp": {
      "command": "npx",
      "args": [
        "@rashidazarang/airtable-mcp@3.2.4"
      ],
      "env": {
        "AIRTABLE_TOKEN": "your_token",
        "AIRTABLE_BASE_ID": "your_base_id"
      }
    }
  }
}
```

## MCP Client Integration

The AI agent's MCP client (`src/mcp_client.py`) is fully compatible with v3.2.4:

```python
from src.mcp_client import MCPClient

# Initialize client
client = MCPClient(server_url="http://localhost:8010/mcp")

# Test connection
status = await client.test_connection()
print(f"MCP Server v3.2.4 Status: {status}")

# Execute tools
result = await client.execute_tool("list_tables", {})
```

## Available Tools (33 Total)

### Data Operations (7)
- `list_tables` - Get all tables with schema
- `list_records` - Query records with filtering
- `get_record` - Retrieve single record
- `create_record` - Add new records
- `update_record` - Modify existing records
- `delete_record` - Remove records
- `search_records` - Advanced search with formulas

### Batch Operations (4) 
- `batch_create_records` - Create up to 10 records
- `batch_update_records` - Update up to 10 records
- `batch_delete_records` - Delete up to 10 records
- `batch_upsert_records` - Update or create records

### Schema Management (11)
- `list_bases` - List accessible bases
- `get_base_schema` - Complete base schema
- `describe_table` - Detailed table info
- `list_field_types` - Available field types
- `get_table_views` - List table views
- `create_table` - Create new tables
- `update_table` - Modify tables
- `delete_table` - Remove tables
- `create_field` - Add fields
- `update_field` - Modify fields
- `delete_field` - Remove fields

### Webhook Management (5)
- `list_webhooks` - View webhooks
- `create_webhook` - Set up webhooks
- `delete_webhook` - Remove webhooks
- `get_webhook_payloads` - Webhook history
- `refresh_webhook` - Extend expiration

### Other Operations (6)
- `upload_attachment` - Attach files via URLs
- `create_view` - Create new views
- `get_view_metadata` - View information
- `create_base` - Create new bases
- `list_collaborators` - View collaborators
- `list_shares` - List shared views

## TypeScript Support

v3.2.4 includes full TypeScript support:

```typescript
import { 
  AirtableMCPServer,
  ListRecordsInput,
  ToolResponse 
} from '@rashidazarang/airtable-mcp/types';

const server = new AirtableMCPServer();

// Type-safe operations
const params: ListRecordsInput = {
  table: 'Tasks',
  maxRecords: 100,
  filterByFormula: "Status = 'Active'"
};

const result: ToolResponse = await server.handleToolCall('list_records', params);
```

## Migration from Previous Versions

### From < v3.2.1
```bash
# Update to latest version
npm update @rashidazarang/airtable-mcp

# If using git clone, pull latest
git pull origin main
npm install
npm run build  # For TypeScript
```

### Breaking Changes
- None! v3.2.4 maintains full backward compatibility

### Security Recommendations
- **Update immediately** to v3.2.4 for security fixes
- Review OAuth2 implementations if using authorization endpoints
- Validate all user inputs before passing to MCP tools

## Testing

### Verify Installation
```bash
# Check version
npm list @rashidazarang/airtable-mcp

# Test MCP server
curl http://localhost:8010/health

# Test via AI agent
python -c "
import asyncio
from src.mcp_client import MCPClient

async def test():
    client = MCPClient()
    result = await client.test_connection()
    print(f'Status: {result}')
    
asyncio.run(test())
"
```

### Run Test Suite
```bash
# Python tests for AI agent
pytest tests/ -v

# Docker health checks
docker-compose ps
docker-compose exec airtable-ai-agent curl http://airtable-mcp:8010/health
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure MCP server is running on port 8010
   - Check firewall settings
   - Verify Docker network connectivity

2. **Authentication Failed**
   - Verify AIRTABLE_TOKEN is valid
   - Check token has required scopes
   - Ensure BASE_ID is correct

3. **TypeScript Compilation Errors**
   - Update to v3.2.4 which fixes all TS issues
   - Run `npm run build` after updates

4. **Docker Issues**
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Performance Optimization

### Caching
The AI agent includes Redis caching for MCP responses:
```python
# Responses are cached for 5 minutes by default
result = await client.list_tables()  # First call: hits API
result = await client.list_tables()  # Second call: from cache
```

### Batch Operations
Use batch tools for better performance:
```python
# Instead of multiple create_record calls
records = [{"Name": "Task 1"}, {"Name": "Task 2"}, ...]
await client.batch_create_records("Tasks", records)
```

## Security Best Practices

1. **Environment Variables**: Never hardcode credentials
2. **Token Scopes**: Use minimum required permissions
3. **Input Validation**: Always validate user inputs
4. **HTTPS Only**: Use TLS in production
5. **Rate Limiting**: Implement rate limits for API calls

## Support

- **MCP Server Issues**: https://github.com/rashidazarang/airtable-mcp/issues
- **AI Agent Issues**: https://github.com/rashidazarang/airtable-ai-agent/issues
- **Documentation**: This guide + README.md + COMPREHENSIVE_DOCUMENTATION.md

## Version Compatibility

| AI Agent Version | MCP Server Version | Status |
|-----------------|-------------------|---------|
| 1.0.0 | 3.2.4 | ✅ Current |
| 1.0.0 | 3.2.1-3.2.3 | ⚠️ Works but upgrade recommended |
| 1.0.0 | < 3.2.1 | ❌ TypeScript issues |

---

**Last Updated**: September 9, 2025  
**MCP Version**: 3.2.4  
**Security Status**: ✅ All vulnerabilities patched