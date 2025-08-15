# Complete Airtable Web API Documentation

This comprehensive guide covers the entire Airtable Web API, providing complete context for AI agents.

## 🔐 Authentication

### Personal Access Tokens (PATs)
- **Current Method**: Personal Access Tokens (as of Feb 2024)
- **Deprecated**: API Keys (deprecated Feb 1, 2024)
- **Header Format**: `Authorization: Bearer YOUR_PERSONAL_ACCESS_TOKEN`

### Required Scopes
```yaml
data.records:read: Read records from tables
data.records:write: Create, update, delete records
schema.bases:read: View table schemas and metadata
schema.bases:write: Create/modify tables, fields, views, bases
webhook:manage: Create and manage webhooks (optional)
```

## 🌐 Base URL and Rate Limits

### API Base URL
```
https://api.airtable.com/v0/
```

### Rate Limits
- **5 requests per second per base**
- **Consistent across all pricing tiers**
- **No increased rate limits available**

## 📊 Data Operations

### List Records
```http
GET /v0/{baseId}/{tableIdOrName}
```

**Query Parameters:**
- `fields[]`: Specific fields to return
- `filterByFormula`: Airtable formula to filter records
- `maxRecords`: Maximum records to return (default: 100)
- `pageSize`: Number of records per page (max: 100)
- `sort[0][field]`: Field to sort by
- `sort[0][direction]`: "asc" or "desc"
- `view`: View ID or name
- `cellFormat`: "json" (default) or "string"
- `timeZone`: Timezone for datetime fields
- `userLocale`: Locale for number/date formatting
- `offset`: Pagination token

**Response Format:**
```json
{
  "records": [
    {
      "id": "recXXXXXXXXXXXXXX",
      "createdTime": "2024-08-15T12:00:00.000Z",
      "fields": {
        "Name": "Example Record",
        "Status": "Active"
      }
    }
  ],
  "offset": "itrXXXXXXXXXXXXXX/recXXXXXXXXXXXXXX"
}
```

### Get Single Record
```http
GET /v0/{baseId}/{tableIdOrName}/{recordId}
```

### Create Records
```http
POST /v0/{baseId}/{tableIdOrName}
```

**Single Record:**
```json
{
  "fields": {
    "Name": "New Record",
    "Status": "Draft"
  }
}
```

**Multiple Records (up to 10):**
```json
{
  "records": [
    {
      "fields": {
        "Name": "Record 1",
        "Status": "Active"
      }
    },
    {
      "fields": {
        "Name": "Record 2", 
        "Status": "Draft"
      }
    }
  ]
}
```

### Update Records
```http
PATCH /v0/{baseId}/{tableIdOrName}
```

**Single Record:**
```json
{
  "id": "recXXXXXXXXXXXXXX",
  "fields": {
    "Status": "Completed"
  }
}
```

**Multiple Records (up to 10):**
```json
{
  "records": [
    {
      "id": "recXXXXXXXXXXXXXX",
      "fields": {
        "Status": "Completed"
      }
    }
  ]
}
```

**Upsert Operation:**
```json
{
  "records": [...],
  "performUpsert": {
    "fieldsToMergeOn": ["Name", "Email"]
  }
}
```

### Delete Records
```http
DELETE /v0/{baseId}/{tableIdOrName}?records[]=recXXX&records[]=recYYY
```

## 🏗️ Schema Management (Metadata API)

### List Bases
```http
GET /v0/meta/bases
```

**Response:**
```json
{
  "bases": [
    {
      "id": "appXXXXXXXXXXXXXX",
      "name": "My Base",
      "permissionLevel": "create"
    }
  ]
}
```

### Get Base Schema
```http
GET /v0/meta/bases/{baseId}/tables
```

**Response:**
```json
{
  "tables": [
    {
      "id": "tblXXXXXXXXXXXXXX",
      "name": "Table Name",
      "description": "Table description",
      "primaryFieldId": "fldXXXXXXXXXXXXXX",
      "fields": [
        {
          "id": "fldXXXXXXXXXXXXXX",
          "name": "Field Name",
          "type": "singleLineText",
          "description": "Field description",
          "options": {}
        }
      ],
      "views": [
        {
          "id": "viwXXXXXXXXXXXXXX",
          "name": "Grid view",
          "type": "grid"
        }
      ]
    }
  ]
}
```

### Create Table
```http
POST /v0/meta/bases/{baseId}/tables
```

**Request:**
```json
{
  "name": "New Table",
  "description": "Table description",
  "fields": [
    {
      "name": "Name",
      "type": "singleLineText",
      "description": "Primary field"
    },
    {
      "name": "Status",
      "type": "singleSelect",
      "options": {
        "choices": [
          {"name": "Active", "color": "greenBright"},
          {"name": "Inactive", "color": "redBright"}
        ]
      }
    }
  ]
}
```

### Update Table
```http
PATCH /v0/meta/bases/{baseId}/tables/{tableId}
```

### Delete Table
```http
DELETE /v0/meta/bases/{baseId}/tables/{tableId}
```

### Create Field
```http
POST /v0/meta/bases/{baseId}/tables/{tableId}/fields
```

### Update Field
```http
PATCH /v0/meta/bases/{baseId}/tables/{tableId}/fields/{fieldId}
```

### Delete Field
```http
DELETE /v0/meta/bases/{baseId}/tables/{tableId}/fields/{fieldId}
```

## 📎 Attachment Management

### Upload Attachment
```http
POST /v0/{baseId}/attachments
```

**Note**: Airtable doesn't support direct file uploads. Instead, provide public URLs:

**Update Record with Attachment:**
```json
{
  "fields": {
    "Attachments": [
      {
        "url": "https://example.com/file.pdf",
        "filename": "document.pdf"
      }
    ]
  }
}
```

## 🪝 Webhooks

### List Webhooks
```http
GET /v0/bases/{baseId}/webhooks
```

### Create Webhook
```http
POST /v0/bases/{baseId}/webhooks
```

**Request:**
```json
{
  "notificationUrl": "https://your-domain.com/webhook",
  "specification": {
    "options": {
      "filters": {
        "dataTypes": ["tableData"],
        "changeTypes": ["add", "remove", "update"],
        "fromSources": ["client"]
      }
    }
  }
}
```

### Delete Webhook
```http
DELETE /v0/bases/{baseId}/webhooks/{webhookId}
```

### List Webhook Payloads
```http
GET /v0/bases/{baseId}/webhooks/{webhookId}/payloads
```

### Refresh Webhook
```http
POST /v0/bases/{baseId}/webhooks/{webhookId}/refresh
```

## 🎨 Field Types Reference

### Basic Field Types
- `singleLineText`: Single line text input
- `multilineText`: Multi-line text input
- `richText`: Rich text with formatting
- `email`: Email address field
- `url`: URL field
- `phoneNumber`: Phone number field
- `number`: Number field with formatting options
- `percent`: Percentage field
- `currency`: Currency field
- `singleSelect`: Single choice from predefined options
- `multipleSelectionList`: Multiple choices from predefined options
- `date`: Date field
- `dateTime`: Date and time field
- `checkbox`: Boolean checkbox
- `rating`: Star rating field
- `duration`: Duration/time field

### Advanced Field Types
- `multipleAttachment`: File attachments
- `linkedRecord`: Link to records in another table
- `lookup`: Lookup values from linked records
- `rollup`: Calculate values from linked records
- `count`: Count of linked records
- `formula`: Calculated field with formulas
- `createdTime`: Auto-timestamp when record created
- `createdBy`: Auto-user who created record
- `lastModifiedTime`: Auto-timestamp when record modified
- `lastModifiedBy`: Auto-user who last modified record
- `autoNumber`: Auto-incrementing number
- `barcode`: Barcode/QR code field
- `button`: Action button field

## 👁️ Views Management

### List Views
```http
GET /v0/meta/bases/{baseId}/tables/{tableId}/views
```

### Get View Metadata
```http
GET /v0/meta/bases/{baseId}/tables/{tableId}/views/{viewId}
```

### Create View
```http
POST /v0/meta/bases/{baseId}/tables/{tableId}/views
```

**Request:**
```json
{
  "name": "Custom View",
  "type": "grid",
  "visibleFieldIds": ["fldXXX", "fldYYY"],
  "fieldOrder": ["fldXXX", "fldYYY", "fldZZZ"]
}
```

## 🏢 Base Management

### Create Base
```http
POST /v0/meta/bases
```

### List Collaborators
```http
GET /v0/meta/bases/{baseId}/collaborators
```

### List Shares
```http
GET /v0/meta/bases/{baseId}/shares
```

## ⚠️ Error Handling

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not found (invalid base/table/record ID)
- `422`: Unprocessable entity (validation errors)
- `429`: Too many requests (rate limited)
- `500`: Internal server error

### Error Response Format
```json
{
  "error": {
    "type": "INVALID_REQUEST_MISSING_FIELDS",
    "message": "Could not find field \"xyz\" in the results. Please ensure that all field names or field IDs specified in the request exist in the table"
  }
}
```

## 🔍 Best Practices

### Performance Optimization
1. **Use batch operations** when possible (up to 10 records)
2. **Specify only needed fields** with `fields[]` parameter
3. **Use pagination** for large datasets
4. **Implement exponential backoff** for rate limit handling
5. **Cache schema information** to reduce API calls

### Data Integrity
1. **Validate data** before sending to API
2. **Handle errors gracefully** with proper retry logic
3. **Use transactions** for related operations
4. **Monitor webhook delivery** for real-time updates

### Security
1. **Rotate tokens regularly**
2. **Use minimum required scopes**
3. **Store tokens securely** (environment variables)
4. **Validate webhook signatures** (if implemented)
5. **Sanitize user input** before API calls

This comprehensive documentation provides complete context for understanding and working with the Airtable Web API.