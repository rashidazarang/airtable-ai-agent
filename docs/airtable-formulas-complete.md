# Complete Airtable Formula Reference

This comprehensive guide covers all Airtable formula functions and patterns for AI agents.

## 🧮 Formula Basics

### Formula Syntax
- Formulas start with an equals sign: `=`
- Field references use curly braces: `{Field Name}`
- Functions use parentheses: `FUNCTION(arguments)`
- Text literals use quotes: `"Hello World"`
- Numbers are written directly: `42`, `3.14`

### Data Types
- **Text**: `"Hello"`, `"123"`
- **Number**: `42`, `3.14`, `-10`
- **Date**: `DATE(2024, 8, 15)`
- **Boolean**: `TRUE`, `FALSE`
- **Array**: `[1, 2, 3]` or `["A", "B", "C"]`

## 📊 Numeric Functions

### Mathematical Operations
```javascript
// Basic arithmetic
{Price} + {Tax}
{Total} - {Discount}
{Quantity} * {Price}
{Total} / {Quantity}
{Base} ^ {Exponent}

// Advanced math
ABS(-5)                    // Absolute value: 5
CEILING(4.2)               // Round up: 5
FLOOR(4.8)                 // Round down: 4
ROUND(4.567, 2)            // Round to 2 decimals: 4.57
INT(4.8)                   // Integer part: 4
MOD(10, 3)                 // Modulo: 1
SQRT(16)                   // Square root: 4
POWER(2, 3)                // Power: 8
EXP(2)                     // e^x: 7.389...
LOG(100)                   // Natural log
LOG10(100)                 // Base 10 log: 2
```

### Statistical Functions
```javascript
// Basic stats
SUM([1, 2, 3, 4])          // Sum: 10
AVERAGE([1, 2, 3, 4])      // Average: 2.5
MAX([1, 5, 3])             // Maximum: 5
MIN([1, 5, 3])             // Minimum: 1
COUNT([1, 2, "", 4])       // Count non-empty: 3
COUNTA([1, 2, "", 4])      // Count all: 4

// Advanced stats
MEDIAN([1, 2, 3, 4, 5])    // Median: 3
MODE([1, 2, 2, 3])         // Most frequent: 2
STDEV([1, 2, 3, 4])        // Standard deviation
VAR([1, 2, 3, 4])          // Variance
```

## 📝 Text Functions

### String Manipulation
```javascript
// Basic text operations
CONCATENATE("Hello", " ", "World")  // "Hello World"
"Hello" & " " & "World"             // Same as above
LEN("Hello")                        // Length: 5
UPPER("hello")                      // "HELLO"
LOWER("WORLD")                      // "world"
PROPER("hello world")               // "Hello World"

// String extraction
LEFT("Hello", 2)                    // "He"
RIGHT("World", 2)                   // "ld"  
MID("Hello", 2, 3)                  // "ell"
FIND("o", "Hello")                  // Position: 5
SEARCH("LO", "Hello")               // Case-insensitive: 3
```

### Advanced Text Functions
```javascript
// String replacement and manipulation
SUBSTITUTE("Hello World", "o", "0") // "Hell0 W0rld"
REPLACE("Hello", 2, 2, "ay")        // "Haylo"
TRIM("  Hello  ")                   // "Hello"
REPT("Hi", 3)                       // "HiHiHi"

// Text validation
EXACT("Hello", "hello")             // FALSE (case sensitive)
ISBLANK("")                         // TRUE
ISERROR(1/0)                        // TRUE
ISNUMBER("123")                     // FALSE (it's text)
ISTEXT("Hello")                     // TRUE

// Regular expressions
REGEX_MATCH("abc123", "\d+")        // TRUE
REGEX_EXTRACT("Price: $45.99", "\d+\.\d+") // "45.99"
REGEX_REPLACE("Hello123", "\d+", "")        // "Hello"
```

## 📅 Date and Time Functions

### Date Creation
```javascript
// Date construction
DATE(2024, 8, 15)                   // August 15, 2024
DATETIME_PARSE("2024-08-15")        // Parse ISO date
DATETIME_PARSE("Aug 15, 2024", "MMM DD, YYYY") // Custom format
TODAY()                             // Current date
NOW()                               // Current date and time
```

### Date Manipulation
```javascript
// Date arithmetic
DATEADD({Start Date}, 30, 'days')   // Add 30 days
DATEADD({Date}, 2, 'months')        // Add 2 months
DATEADD({DateTime}, -3, 'hours')    // Subtract 3 hours

// Date difference
DATETIME_DIFF({End Date}, {Start Date}, 'days')    // Days between
DATETIME_DIFF({End}, {Start}, 'hours')             // Hours between
DATETIME_DIFF({End}, {Start}, 'months')            // Months between
```

### Date Formatting
```javascript
// Format dates
DATETIME_FORMAT({Date}, 'YYYY-MM-DD')      // "2024-08-15"
DATETIME_FORMAT({Date}, 'MMM D, YYYY')     // "Aug 15, 2024"
DATETIME_FORMAT({Date}, 'dddd')            // "Thursday"

// Extract date parts
YEAR({Date})                        // 2024
MONTH({Date})                       // 8
DAY({Date})                         // 15
WEEKDAY({Date})                     // 1-7 (Sunday = 1)
WEEKNUM({Date})                     // Week of year
HOUR({DateTime})                    // Hour (0-23)
MINUTE({DateTime})                  // Minute (0-59)
SECOND({DateTime})                  // Second (0-59)
```

### Date Conditionals
```javascript
// Date comparisons
IS_AFTER({Date}, TODAY())           // TRUE if date is future
IS_BEFORE({Date}, TODAY())          // TRUE if date is past
IS_SAME({Date1}, {Date2}, 'day')    // Same day?
IS_SAME({Date1}, {Date2}, 'month')  // Same month?

// Business date functions
WORKDAY({Start}, 10)                // 10 workdays after start
WORKDAY_DIFF({Start}, {End})        // Workdays between dates
```

## 🔗 Lookup and Reference Functions

### Linked Record Functions
```javascript
// Single linked record
{Linked Field}                      // First linked record
ARRAYUNIQUE({Linked Field})         // Remove duplicates

// Multiple linked records
ARRAYJOIN({Linked Records}, ", ")   // Join with comma
ARRAYCOMPACT({Linked Records})      // Remove empty values
ARRAYSLICE({Linked Records}, 0, 3)  // First 3 records
```

### Rollup Operations
```javascript
// Rollup from linked records
ROLLUP({Linked Records}, values, MAX(values))        // Maximum
ROLLUP({Linked Records}, values, SUM(values))        // Sum
ROLLUP({Linked Records}, values, AVERAGE(values))    // Average
ROLLUP({Linked Records}, values, CONCATENATE(values)) // Join text

// Complex rollups
ROLLUP({Projects}, values, 
  SUM(IF({Status} = "Active", {Budget}, 0))
)  // Sum budget for active projects only
```

## 🔍 Logical Functions

### Conditional Logic
```javascript
// Basic conditionals
IF({Score} > 90, "A", "F")          // Grade based on score
IF({Status} = "Complete", "✅", "⏳") // Status icons

// Nested conditions
IF({Score} >= 90, "A",
  IF({Score} >= 80, "B", 
    IF({Score} >= 70, "C", "F")
  )
)

// Multiple conditions
AND({Score} > 80, {Attendance} > 0.9)  // Both must be true
OR({VIP}, {Spending} > 1000)            // Either condition
NOT({Cancelled})                        // Opposite of boolean
```

### Advanced Logic
```javascript
// Switch-like logic
SWITCH({Grade},
  "A", "Excellent",
  "B", "Good", 
  "C", "Average",
  "Default"
)

// Blank handling
IF(ISBLANK({Field}), "Not provided", {Field})
BLANK()                             // Return blank value
```

## 🎨 Formatting Functions

### Number Formatting
```javascript
// Currency and numbers
"$" & {Price}                       // Add currency symbol
ROUND({Price}, 2)                   // Round to cents
IF({Price} > 0, 
  "$" & ROUND({Price}, 2), 
  "Free"
)

// Percentages
{Complete} / {Total} * 100 & "%"    // Calculate percentage
```

### Text Formatting
```javascript
// Dynamic text
"Hello " & {Name} & "!"             // Personalized greeting
{First Name} & " " & {Last Name}    // Full name
UPPER(LEFT({Name}, 1)) & LOWER(RIGHT({Name}, LEN({Name})-1)) // Capitalize

// Conditional formatting
IF({Priority} = "High", "🔴 " & {Task}, {Task})  // Add emoji for high priority
```

## 🔢 Array Functions

### Array Operations
```javascript
// Basic array functions
ARRAYUNIQUE([1, 1, 2, 3])          // [1, 2, 3]
ARRAYCOMPACT([1, "", 2, "", 3])    // [1, 2, 3]
ARRAYJOIN([1, 2, 3], "-")          // "1-2-3"
ARRAYSLICE([1, 2, 3, 4], 1, 3)     // [2, 3]

// Array aggregation
SUM([1, 2, 3])                     // 6
MAX([1, 5, 3])                     // 5
MIN([1, 5, 3])                     // 1
AVERAGE([1, 2, 3, 4])              // 2.5
```

### Complex Array Operations
```javascript
// Filter arrays
ARRAYCOMPACT(
  IF({Status} = "Active", {Project Name}, BLANK())
)  // Only active project names

// Transform arrays
ARRAYJOIN(
  ARRAYUNIQUE({Tags}), 
  " | "
)  // Unique tags joined with pipes
```

## 🎯 Practical Formula Patterns

### Status and Progress Tracking
```javascript
// Progress calculation
ROUND({Completed Tasks} / {Total Tasks} * 100, 0) & "% Complete"

// Status determination
IF(
  {End Date} < TODAY(), "Overdue",
  IF(
    {End Date} = TODAY(), "Due Today", 
    IF(
      DATETIME_DIFF({End Date}, TODAY(), 'days') <= 3, 
      "Due Soon", 
      "On Track"
    )
  )
)

// Health score
IF(
  AND({Budget Remaining} > 0, {End Date} > TODAY()), 
  "Green",
  IF(
    OR({Budget Remaining} < 0, {End Date} < TODAY()),
    "Red", 
    "Yellow"
  )
)
```

### Financial Calculations
```javascript
// Revenue calculations
{Quantity} * {Unit Price} * (1 - {Discount Rate})

// Tax calculations  
{Subtotal} * (1 + {Tax Rate})

// Commission calculations
IF({Sales} > {Quota}, 
  {Base Commission} + ({Sales} - {Quota}) * {Bonus Rate},
  {Base Commission}
)
```

### Data Validation
```javascript
// Email validation
REGEX_MATCH({Email}, "^[^\s@]+@[^\s@]+\.[^\s@]+$")

// Phone validation
REGEX_MATCH({Phone}, "^\d{3}-\d{3}-\d{4}$")

// Required field validation
IF(
  OR(
    ISBLANK({Name}),
    ISBLANK({Email}),
    ISBLANK({Phone})
  ),
  "❌ Missing required fields",
  "✅ Complete"
)
```

### Dynamic Content
```javascript
// Personalized messages
"Hi " & {First Name} & "! Your order #" & {Order ID} & " is " & LOWER({Status}) & "."

// Dynamic URLs
"https://example.com/orders/" & {Order ID}

// Conditional content
IF({VIP Status}, 
  "🌟 VIP Customer: " & {Name},
  {Name}
)
```

## 🔧 Filter Formulas

### Record Filtering
```javascript
// Status filtering
{Status} = "Active"
{Status} != "Cancelled"
OR({Status} = "Active", {Status} = "Pending")

// Date filtering
IS_AFTER({Due Date}, TODAY())               // Future dates
IS_BEFORE({Created Date}, DATEADD(TODAY(), -30, 'days'))  // Last 30 days
AND(
  IS_AFTER({Date}, DATE(2024, 1, 1)),
  IS_BEFORE({Date}, DATE(2024, 12, 31))
)  // Date range

// Numeric filtering
{Price} > 100
{Score} >= 80
AND({Price} > 50, {Price} < 200)           // Price range
```

### Text Filtering
```javascript
// Text matching
SEARCH("urgent", LOWER({Notes})) > 0       // Contains "urgent"
LEFT({Project Code}, 3) = "PRJ"            // Starts with "PRJ"
RIGHT({File Name}, 4) = ".pdf"             // Ends with ".pdf"
LEN({Description}) > 100                   // Long descriptions

// Pattern matching
REGEX_MATCH({SKU}, "^[A-Z]{3}-\d{4}$")     // SKU format validation
```

### Complex Filters
```javascript
// Multi-condition filters
AND(
  {Status} = "Active",
  {Priority} = "High",
  IS_AFTER({Due Date}, TODAY())
)

// Exclusion filters
NOT(
  OR(
    {Status} = "Cancelled",
    {Status} = "Completed"
  )
)

// Linked record filters
{Assigned To} != BLANK()                    // Has assignee
ARRAYJOIN({Tags}) != ""                     // Has tags
```

This comprehensive formula reference provides AI agents with complete knowledge of Airtable's formula capabilities and common usage patterns.