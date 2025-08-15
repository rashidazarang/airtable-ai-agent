# Complete Airtable.js Documentation

This comprehensive guide covers the official Airtable.js JavaScript library for AI agents.

## 📦 Installation and Setup

### Node.js Installation
```bash
npm install airtable
```
- **Compatibility**: Node.js 10 and above
- **Latest Version**: v0.12.2 (as of 2024)

### Browser Usage
```html
<script src="build/airtable.browser.js"></script>
```

## 🔧 Configuration

### Global Configuration
```javascript
const Airtable = require('airtable');

// Configure globally
Airtable.configure({
  endpointUrl: 'https://api.airtable.com',
  apiKey: 'YOUR_PERSONAL_ACCESS_TOKEN'
});
```

### Instance Configuration
```javascript
const airtable = new Airtable({
  apiKey: 'YOUR_PERSONAL_ACCESS_TOKEN'
});

const base = airtable.base('YOUR_BASE_ID');
```

### Configuration Options
```javascript
{
  apiKey: 'YOUR_TOKEN',           // Personal Access Token
  endpointUrl: 'https://api.airtable.com',  // API endpoint
  requestTimeout: 300000          // Request timeout (5 minutes default)
}
```

## 🏗️ Basic Usage Patterns

### Connect to Base
```javascript
const Airtable = require('airtable');
const base = new Airtable({apiKey: 'YOUR_TOKEN'}).base('YOUR_BASE_ID');
const table = base('Table Name');
```

### Using Environment Variables
```javascript
// Set AIRTABLE_API_KEY environment variable
const base = new Airtable().base('YOUR_BASE_ID');
```

## 📊 Data Operations

### Select Records
```javascript
// Basic select
table.select().eachPage((records, fetchNextPage) => {
  records.forEach(record => {
    console.log('Retrieved', record.get('Name'));
  });
  fetchNextPage();
}, err => {
  if (err) console.error(err);
});

// With options
table.select({
  maxRecords: 10,
  view: "Main View",
  filterByFormula: "Status = 'Active'",
  sort: [{field: "Name", direction: "asc"}]
}).eachPage((records, fetchNextPage) => {
  // Process records
  fetchNextPage();
});
```

### Promise-Based Selection
```javascript
// Get first page
const records = await table.select({
  maxRecords: 10,
  view: "Grid view"
}).firstPage();

// Get all records
const allRecords = await table.select().all();

records.forEach(record => {
  console.log('ID:', record.id);
  console.log('Name:', record.get('Name'));
  console.log('All fields:', record.fields);
});
```

### Create Records
```javascript
// Single record
const createdRecord = await table.create({
  "Name": "New Record",
  "Status": "Active",
  "Notes": "Created via API"
});

console.log('Created record:', createdRecord.id);

// Multiple records (up to 10)
const createdRecords = await table.create([
  {"Name": "Record 1", "Status": "Active"},
  {"Name": "Record 2", "Status": "Draft"},
  {"Name": "Record 3", "Status": "Review"}
]);

createdRecords.forEach(record => {
  console.log('Created:', record.id);
});
```

### Update Records
```javascript
// Single record update
const updatedRecord = await table.update('recXXXXXXXXXXXXXX', {
  "Status": "Completed",
  "Notes": "Updated via API"
});

// Multiple records update (up to 10)
const updatedRecords = await table.update([
  {
    "id": "recXXXXXXXXXXXXXX",
    "fields": {
      "Status": "Completed"
    }
  },
  {
    "id": "recYYYYYYYYYYYYYY", 
    "fields": {
      "Status": "In Progress"
    }
  }
]);
```

### Replace Records (Full Update)
```javascript
// Replace completely overwrites record
const replacedRecord = await table.replace('recXXXXXXXXXXXXXX', {
  "Name": "Completely New Data",
  "Status": "Active"
  // All other fields will be cleared
});
```

### Delete Records
```javascript
// Single record
const deletedRecord = await table.destroy('recXXXXXXXXXXXXXX');

// Multiple records (up to 10)
const deletedRecords = await table.destroy([
  'recXXXXXXXXXXXXXX',
  'recYYYYYYYYYYYYYY',
  'recZZZZZZZZZZZZZZ'
]);
```

## 🔍 Query Options

### Filtering
```javascript
table.select({
  // Airtable formula for filtering
  filterByFormula: "AND({Status} = 'Active', {Priority} = 'High')",
  
  // Maximum records to return
  maxRecords: 50,
  
  // Page size (max 100)
  pageSize: 20,
  
  // Specific view
  view: "Active Tasks",
  
  // Specific fields only
  fields: ["Name", "Status", "Due Date"],
  
  // Sorting
  sort: [
    {field: "Priority", direction: "desc"},
    {field: "Name", direction: "asc"}
  ],
  
  // Cell format
  cellFormat: "json", // or "string"
  
  // Timezone
  timeZone: "America/New_York",
  
  // User locale
  userLocale: "en-us"
})
```

### Formula Examples
```javascript
// Status filtering
filterByFormula: "{Status} = 'Active'"

// Date filtering
filterByFormula: "IS_AFTER({Due Date}, TODAY())"

// Text search
filterByFormula: "SEARCH('keyword', {Description})"

// Numeric comparison
filterByFormula: "{Priority Score} > 5"

// Complex conditions
filterByFormula: "AND({Status} = 'Active', OR({Priority} = 'High', {Due Date} < TODAY()))"

// Empty field check
filterByFormula: "{Assignee} = BLANK()"

// Not empty check
filterByFormula: "{Notes} != ''"
```

## 📎 Working with Attachments

### Attachment Field Structure
```javascript
// Attachment field contains array of attachment objects
const record = await table.find('recXXXXXXXXXXXXXX');
const attachments = record.get('Attachments');

attachments.forEach(attachment => {
  console.log('Filename:', attachment.filename);
  console.log('URL:', attachment.url);
  console.log('Type:', attachment.type);
  console.log('Size:', attachment.size);
  console.log('Thumbnails:', attachment.thumbnails);
});
```

### Adding Attachments
```javascript
// Add attachment from URL
await table.update('recXXXXXXXXXXXXXX', {
  "Attachments": [
    {
      "url": "https://example.com/document.pdf",
      "filename": "document.pdf"
    }
  ]
});

// Multiple attachments
await table.update('recXXXXXXXXXXXXXX', {
  "Attachments": [
    {"url": "https://example.com/doc1.pdf"},
    {"url": "https://example.com/image.jpg", "filename": "photo.jpg"}
  ]
});
```

## 🔗 Linked Records

### Working with Linked Records
```javascript
// Link to other records
await table.create({
  "Name": "New Task",
  "Assigned To": ["recUSERXXXXXXXXXX"], // Array of record IDs
  "Project": ["recPROJECTXXXXXXX"]
});

// Get linked record data
const record = await table.find('recXXXXXXXXXXXXXX');
const linkedProjects = record.get('Project'); // Array of linked record IDs

// To get full linked record data, you need separate queries
if (linkedProjects && linkedProjects.length > 0) {
  const projectTable = base('Projects');
  const projectRecord = await projectTable.find(linkedProjects[0]);
  console.log('Project name:', projectRecord.get('Name'));
}
```

## ⚠️ Error Handling

### Try-Catch Pattern
```javascript
try {
  const record = await table.create({
    "Name": "Test Record",
    "Required Field": "Value"
  });
  console.log('Success:', record.id);
} catch (error) {
  console.error('Error:', error.message);
  console.error('Status:', error.statusCode);
  console.error('Details:', error.error);
}
```

### Common Error Types
```javascript
// Rate limiting (429)
if (error.statusCode === 429) {
  console.log('Rate limited, wait and retry');
}

// Invalid field (422)
if (error.statusCode === 422) {
  console.log('Validation error:', error.message);
}

// Permission denied (403)
if (error.statusCode === 403) {
  console.log('Insufficient permissions');
}

// Not found (404)
if (error.statusCode === 404) {
  console.log('Record or table not found');
}
```

## 🔄 Pagination

### Manual Pagination
```javascript
let offset = null;

do {
  const page = await table.select({
    pageSize: 100,
    offset: offset
  }).firstPage();
  
  // Process records
  page.forEach(record => {
    console.log('Processing:', record.get('Name'));
  });
  
  // Get offset for next page
  offset = page.offset;
} while (offset);
```

### EachPage Helper
```javascript
await new Promise((resolve, reject) => {
  table.select().eachPage(
    (records, fetchNextPage) => {
      // Process current page
      records.forEach(record => {
        console.log('Record:', record.get('Name'));
      });
      
      // Fetch next page
      fetchNextPage();
    },
    (err) => {
      if (err) reject(err);
      else resolve();
    }
  );
});
```

## 🎯 Best Practices

### Performance Optimization
```javascript
// 1. Fetch only needed fields
table.select({
  fields: ['Name', 'Status', 'Due Date']
});

// 2. Use appropriate page sizes
table.select({
  pageSize: 100 // Maximum page size
});

// 3. Batch operations when possible
await table.create([record1, record2, record3]); // Better than 3 separate calls

// 4. Cache frequently accessed data
const schema = await base.table('Table Name').select({maxRecords: 1}).firstPage();
```

### Error Handling Best Practices
```javascript
async function safeAirtableOperation(operation) {
  const maxRetries = 3;
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      return await operation();
    } catch (error) {
      if (error.statusCode === 429 && retries < maxRetries - 1) {
        // Rate limited, wait and retry
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retries)));
        retries++;
      } else {
        throw error;
      }
    }
  }
}
```

### Data Validation
```javascript
function validateRecord(fields) {
  const required = ['Name', 'Status'];
  const missing = required.filter(field => !fields[field]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required fields: ${missing.join(', ')}`);
  }
  
  return true;
}

// Use before creating records
const newRecord = {
  "Name": "Task Name",
  "Status": "Active"
};

validateRecord(newRecord);
await table.create(newRecord);
```

## 🔒 Authentication Methods

### Personal Access Token (Recommended)
```javascript
const Airtable = require('airtable');
const base = new Airtable({
  apiKey: 'patXXXXXXXXXXXXXXXXX' // Personal Access Token
}).base('appXXXXXXXXXXXXXXXX');
```

### Environment Variable
```bash
export AIRTABLE_API_KEY=patXXXXXXXXXXXXXXXXX
```

```javascript
// Automatically uses AIRTABLE_API_KEY
const base = new Airtable().base('appXXXXXXXXXXXXXXXX');
```

## 📚 Complete Example

```javascript
const Airtable = require('airtable');

// Configure
const base = new Airtable({
  apiKey: process.env.AIRTABLE_API_KEY
}).base('appXXXXXXXXXXXXXXXX');

const tasksTable = base('Tasks');

async function exampleWorkflow() {
  try {
    // 1. Get active tasks
    const activeTasks = await tasksTable.select({
      filterByFormula: "{Status} = 'Active'",
      sort: [{field: "Priority", direction: "desc"}],
      maxRecords: 10
    }).all();
    
    console.log(`Found ${activeTasks.length} active tasks`);
    
    // 2. Create new task
    const newTask = await tasksTable.create({
      "Name": "Review API Documentation",
      "Status": "Active",
      "Priority": "High",
      "Due Date": "2024-08-20"
    });
    
    console.log('Created task:', newTask.id);
    
    // 3. Update task status
    const updatedTask = await tasksTable.update(newTask.id, {
      "Status": "In Progress",
      "Notes": "Started working on this task"
    });
    
    console.log('Updated task status');
    
    // 4. Get task details
    const taskDetails = await tasksTable.find(newTask.id);
    console.log('Task name:', taskDetails.get('Name'));
    console.log('Current status:', taskDetails.get('Status'));
    
  } catch (error) {
    console.error('Workflow error:', error.message);
  }
}

exampleWorkflow();
```

This comprehensive documentation provides AI agents with complete knowledge of the Airtable.js library and optimal usage patterns.