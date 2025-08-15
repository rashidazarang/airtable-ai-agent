# Complete MCP Integration Documentation

This document provides comprehensive information about our Airtable MCP Server integration for AI agents.

## 🚀 MCP Server Overview

Our Airtable MCP Server v1.6.0 is the most comprehensive Airtable integration available, featuring **33 tools** across 6 categories.

### Server Details
- **Version**: 1.6.0
- **Total Tools**: 33
- **Protocol**: JSON-RPC 2.0
- **URL**: http://localhost:8010/mcp
- **NPM Package**: @rashidazarang/airtable-mcp

## 🛠️ All Available Tools (33 Total)

### 📊 Data Operations (7 tools)
1. **`list_tables`** - Get all tables in base with schema information
2. **`list_records`** - Query records with filtering and pagination
3. **`get_record`** - Retrieve single record by ID
4. **`create_record`** - Add new record to table
5. **`update_record`** - Modify existing record fields
6. **`delete_record`** - Remove record from table
7. **`search_records`** - Advanced search with Airtable formulas

### 🪝 Webhook Management (5 tools)
8. **`list_webhooks`** - View all webhooks configured for base
9. **`create_webhook`** - Set up real-time notifications
10. **`delete_webhook`** - Remove webhook configurations
11. **`get_webhook_payloads`** - Retrieve webhook notification history
12. **`refresh_webhook`** - Extend webhook expiration time

### 🔍 Schema Discovery (6 tools)
13. **`list_bases`** - List all accessible Airtable bases with permissions
14. **`get_base_schema`** - Get complete schema information for any base
15. **`describe_table`** - Detailed table info including all field specifications
16. **`list_field_types`** - Reference guide for all available field types
17. **`get_table_views`** - List all views for specific table with configurations

### 🏗️ Table Management (3 tools)
18. **`create_table`** - Create new tables with custom field definitions
19. **`update_table`** - Modify table names and descriptions
20. **`delete_table`** - Remove tables (with safety confirmation required)

### 🔧 Field Management (3 tools)
21. **`create_field`** - Add new fields to existing tables with all field types
22. **`update_field`** - Modify field properties, names, and options
23. **`delete_field`** - Remove fields (with safety confirmation required)

### ⚡ Batch Operations (4 tools) - **New in v1.6.0**
24. **`batch_create_records`** - Create up to 10 records at once
25. **`batch_update_records`** - Update up to 10 records simultaneously
26. **`batch_delete_records`** - Delete up to 10 records in single operation
27. **`batch_upsert_records`** - Update existing or create new based on key fields

### 📎 Attachment Management (1 tool) - **New in v1.6.0**
28. **`upload_attachment`** - Attach files from public URLs to attachment fields

### 👁️ Advanced Views (2 tools) - **New in v1.6.0**
29. **`create_view`** - Create new views (grid, form, calendar, etc.)
30. **`get_view_metadata`** - Get detailed view information including filters

### 🏢 Base Management (3 tools) - **New in v1.6.0**
31. **`create_base`** - Create new Airtable bases with initial table structures
32. **`list_collaborators`** - View base collaborators and permission levels
33. **`list_shares`** - List shared views and their public configurations

## 🔧 Tool Usage Patterns

### Basic CRUD Operations
```javascript
// List tables
tools/call: list_tables {}

// Get records with filtering
tools/call: list_records {
  "table": "Tasks",
  "maxRecords": 10,
  "filterByFormula": "Status = 'Active'"
}

// Create single record
tools/call: create_record {
  "table": "Tasks",
  "fields": {
    "Name": "New Task",
    "Status": "Draft",
    "Priority": "High"
  }
}
```

### Batch Operations (High Performance)
```javascript
// Create multiple records at once
tools/call: batch_create_records {
  "table": "Tasks", 
  "records": [
    {"fields": {"Name": "Task 1", "Status": "Active"}},
    {"fields": {"Name": "Task 2", "Status": "Draft"}},
    {"fields": {"Name": "Task 3", "Status": "Pending"}}
  ]
}

// Update multiple records
tools/call: batch_update_records {
  "table": "Tasks",
  "records": [
    {"id": "recXXX", "fields": {"Status": "Completed"}},
    {"id": "recYYY", "fields": {"Status": "In Progress"}}
  ]
}
```

### Schema Management
```javascript
// Get complete base schema
tools/call: get_base_schema {}

// Create new table
tools/call: create_table {
  "name": "Projects",
  "description": "Project tracking table",
  "fields": [
    {"name": "Name", "type": "singleLineText"},
    {"name": "Status", "type": "singleSelect", "options": {
      "choices": [
        {"name": "Active", "color": "greenBright"},
        {"name": "Completed", "color": "blueBright"}
      ]
    }},
    {"name": "Due Date", "type": "date"}
  ]
}

// Add field to existing table
tools/call: create_field {
  "table": "Projects",
  "name": "Priority",
  "type": "singleSelect",
  "options": {
    "choices": [
      {"name": "Low", "color": "grayBright"},
      {"name": "Medium", "color": "yellowBright"},
      {"name": "High", "color": "redBright"}
    ]
  }
}
```

### Attachment Management
```javascript
// Attach file from URL
tools/call: upload_attachment {
  "table": "Projects",
  "recordId": "recXXXXXXXXXXXXXX",
  "fieldName": "Documents",
  "url": "https://example.com/document.pdf",
  "filename": "project-spec.pdf"
}
```

### Webhook Management
```javascript
// Create webhook for real-time updates
tools/call: create_webhook {
  "notificationUrl": "https://your-app.com/webhook",
  "specification": {
    "options": {
      "filters": {
        "dataTypes": ["tableData"],
        "changeTypes": ["add", "update"],
        "fromSources": ["client"]
      }
    }
  }
}
```

### Advanced Views
```javascript
// Create custom view
tools/call: create_view {
  "table": "Tasks",
  "name": "High Priority Tasks",
  "type": "grid",
  "visibleFieldIds": ["fldName", "fldStatus", "fldPriority"],
  "fieldOrder": ["fldPriority", "fldName", "fldStatus"]
}
```

## 🔄 MCP Protocol Communication

### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "parameter1": "value1",
      "parameter2": "value2"
    }
  }
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Operation completed successfully..."
      }
    ]
  }
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Airtable API error (422): Invalid field name"
  }
}
```

## 🎯 Best Practices for AI Agents

### Performance Optimization
1. **Use batch operations** when handling multiple records
2. **Cache schema information** to avoid repeated calls
3. **Prefer specific tools** over generic ones when possible
4. **Combine operations** logically in workflows

### Error Handling
1. **Check tool responses** for error indicators
2. **Validate parameters** before making calls
3. **Handle rate limits** gracefully
4. **Provide meaningful error messages** to users

### User Experience
1. **Confirm destructive operations** (delete_table, delete_field)
2. **Provide progress updates** for batch operations
3. **Explain field type options** when creating fields
4. **Show record IDs** for reference in subsequent operations

## 🔒 Security Considerations

### Authentication
- MCP server handles all authentication with Airtable
- No need to expose tokens to AI agent
- All operations respect token permissions

### Validation
- All inputs validated before API calls
- Destructive operations require confirmation
- Rate limiting enforced automatically

## 🚦 Rate Limiting

### Airtable Limits
- 5 requests per second per base
- Batch operations count as single requests
- Automatic retry with exponential backoff

### MCP Server Handling
- Intelligent batching where possible
- Error reporting for rate limit violations
- Graceful degradation under load

## 📊 Monitoring and Debugging

### Logging
- Server logs all operations
- Error details provided in responses
- Performance metrics available

### Testing
- Comprehensive test suite included
- All tools verified with real API
- Edge cases and error conditions tested

## 🔄 Integration Examples

### Simple Task Management
```javascript
// 1. List current tasks
list_records {"table": "Tasks", "maxRecords": 10}

// 2. Create new task
create_record {
  "table": "Tasks",
  "fields": {"Name": "Review proposal", "Status": "Todo"}
}

// 3. Update task status
update_record {
  "table": "Tasks", 
  "recordId": "recXXX",
  "fields": {"Status": "In Progress"}
}
```

### Complex Workflow
```javascript
// 1. Get base schema to understand structure
get_base_schema {}

// 2. Create project with multiple tasks
create_record {"table": "Projects", "fields": {...}}

// 3. Batch create related tasks
batch_create_records {
  "table": "Tasks",
  "records": [multiple task objects]
}

// 4. Set up webhook for notifications
create_webhook {
  "notificationUrl": "https://app.com/webhook",
  "specification": {...}
}
```

This comprehensive documentation provides AI agents with complete knowledge of our MCP server capabilities and optimal usage patterns.