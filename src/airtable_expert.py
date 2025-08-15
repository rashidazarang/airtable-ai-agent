#!/usr/bin/env python3
"""
🧠 Airtable Domain Expert for AI Agent
Advanced Airtable knowledge and operation planning.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
from enum import Enum


class QueryIntent(Enum):
    """Types of query intents"""
    DATA_QUERY = "data_query"           # List, search, filter records
    DATA_CREATE = "data_create"         # Create new records
    DATA_UPDATE = "data_update"         # Update existing records  
    DATA_DELETE = "data_delete"         # Delete records
    SCHEMA_QUERY = "schema_query"       # Get schema information
    SCHEMA_MODIFY = "schema_modify"     # Create/modify tables, fields
    WEBHOOK_MANAGE = "webhook_manage"   # Webhook operations
    BATCH_OPERATION = "batch_operation" # Bulk operations
    FORMULA_HELP = "formula_help"       # Formula assistance
    APP_GUIDANCE = "app_guidance"       # Apps and extensions help
    TROUBLESHOOTING = "troubleshooting" # Error resolution
    GENERAL_INFO = "general_info"       # General questions


@dataclass
class AirtableOperation:
    """Represents a planned Airtable operation"""
    tool_name: str
    parameters: Dict[str, Any]
    priority: int = 1
    description: str = ""
    dependencies: List[str] = None  # Other operations this depends on


@dataclass
class QueryAnalysis:
    """Analysis of a user query"""
    intent: QueryIntent
    confidence: float
    entities: Dict[str, List[str]]  # table names, field names, etc.
    required_tools: List[str]
    context_categories: List[str]
    complexity: str  # "simple", "medium", "complex"


class AirtableExpert:
    """
    Domain expert for Airtable operations and knowledge.
    
    Provides intelligent query analysis, operation planning,
    and response generation with deep Airtable expertise.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("airtable_expert")
        
        # Intent detection patterns
        self.intent_patterns = {
            QueryIntent.DATA_QUERY: [
                r'(?i)\b(list|show|get|find|search|query|retrieve|fetch|view)\b.*\b(records?|data|entries|items|rows)\b',
                r'(?i)\b(what|which|how many)\b.*\b(records?|tasks?|projects?|entries|items)\b',
                r'(?i)\bfilter\b.*\bby\b',
                r'(?i)\bwhere\b.*\b(is|are|equals?|contains?)\b'
            ],
            QueryIntent.DATA_CREATE: [
                r'(?i)\b(create|add|insert|new|make)\b.*\b(record|entry|item|task|project)\b',
                r'(?i)\badd\b.*\bto\b.*\btable\b',
                r'(?i)\bcreate a (new )?record\b'
            ],
            QueryIntent.DATA_UPDATE: [
                r'(?i)\b(update|modify|edit|change|set)\b.*\b(record|entry|field|value)\b',
                r'(?i)\bchange\b.*\bto\b',
                r'(?i)\bupdate\b.*\bwhere\b'
            ],
            QueryIntent.DATA_DELETE: [
                r'(?i)\b(delete|remove|destroy|eliminate)\b.*\b(record|entry|item)\b',
                r'(?i)\bdelete\b.*\bwhere\b'
            ],
            QueryIntent.SCHEMA_QUERY: [
                r'(?i)\b(schema|structure|fields?|columns?|tables?)\b',
                r'(?i)\b(what fields?|table structure|base schema)\b',
                r'(?i)\b(describe|explain).*\btable\b'
            ],
            QueryIntent.SCHEMA_MODIFY: [
                r'(?i)\b(create|add|make).*\b(table|field|column|view)\b',
                r'(?i)\b(modify|change).*\b(table|field|schema)\b',
                r'(?i)\bnew table\b'
            ],
            QueryIntent.WEBHOOK_MANAGE: [
                r'(?i)\b(webhook|notification|trigger|automation)\b',
                r'(?i)\b(notify|alert).*\bwhen\b',
                r'(?i)\breal.?time\b.*\bupdates?\b'
            ],
            QueryIntent.BATCH_OPERATION: [
                r'(?i)\b(batch|bulk|multiple|many|several)\b.*\b(records?|operations?)\b',
                r'(?i)\ball\b.*\brecords?\b.*\b(update|delete|create)\b',
                r'(?i)\b(import|export|migrate)\b.*\bdata\b'
            ],
            QueryIntent.FORMULA_HELP: [
                r'(?i)\b(formula|calculate|computation?|math)\b',
                r'(?i)\bhow to\b.*\bcalculate\b',
                r'(?i)\b(sum|average|count|concatenate|if|lookup|rollup)\b'
            ],
            QueryIntent.APP_GUIDANCE: [
                r'(?i)\b(app|extension|integration|workflow)\b',
                r'(?i)\bhow to\b.*\b(integrate|connect|automate)\b',
                r'(?i)\b(zapier|slack|api)\b'
            ],
            QueryIntent.TROUBLESHOOTING: [
                r'(?i)\b(error|problem|issue|trouble|fix|broken|not working)\b',
                r'(?i)\bwhy\b.*\b(not|isn\'t|won\'t|can\'t|doesn\'t)\b.*\b(work|working)\b',
                r'(?i)\bhow to\b.*\b(fix|resolve|solve)\b'
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'table_names': [
                r'(?i)\btable\s+["\']?([a-zA-Z][\w\s]+?)["\']?(?:\s|$|,|\.|!|\?)',
                r'(?i)(?:in|from|to)\s+["\']?([A-Z][\w\s]+?)["\']?(?:\s+table)?(?:\s|$|,|\.|!|\?)'
            ],
            'field_names': [
                r'(?i)\bfield\s+["\']?([a-zA-Z][\w\s]+?)["\']?(?:\s|$|,|\.|!|\?)',
                r'(?i)(?:field|column)\s+["\']?([A-Z][a-zA-Z\s]+?)["\']?(?:\s|$|,|\.|!|\?)'
            ],
            'record_ids': [
                r'\brec[a-zA-Z0-9]{14}\b'
            ],
            'view_names': [
                r'(?i)\bview\s+["\']?([a-zA-Z][\w\s]+?)["\']?(?:\s|$|,|\.|!|\?)'
            ]
        }
        
        # Tool mapping for different operations
        self.intent_tool_mapping = {
            QueryIntent.DATA_QUERY: ['list_records', 'search_records', 'get_record'],
            QueryIntent.DATA_CREATE: ['create_record', 'batch_create_records'],
            QueryIntent.DATA_UPDATE: ['update_record', 'batch_update_records'],
            QueryIntent.DATA_DELETE: ['delete_record', 'batch_delete_records'],
            QueryIntent.SCHEMA_QUERY: ['list_tables', 'get_base_schema', 'describe_table'],
            QueryIntent.SCHEMA_MODIFY: ['create_table', 'create_field', 'create_view'],
            QueryIntent.WEBHOOK_MANAGE: ['create_webhook', 'list_webhooks', 'delete_webhook'],
            QueryIntent.BATCH_OPERATION: ['batch_create_records', 'batch_update_records', 'batch_delete_records']
        }
        
        # Context categories for different query types
        self.intent_context_mapping = {
            QueryIntent.DATA_QUERY: ['api', 'mcp'],
            QueryIntent.DATA_CREATE: ['api', 'mcp'],
            QueryIntent.DATA_UPDATE: ['api', 'mcp'],
            QueryIntent.DATA_DELETE: ['api', 'mcp'],
            QueryIntent.SCHEMA_QUERY: ['api', 'mcp', 'schema'],
            QueryIntent.SCHEMA_MODIFY: ['api', 'mcp', 'schema'],
            QueryIntent.WEBHOOK_MANAGE: ['api', 'mcp', 'webhooks'],
            QueryIntent.BATCH_OPERATION: ['api', 'mcp', 'batch'],
            QueryIntent.FORMULA_HELP: ['formulas', 'api'],
            QueryIntent.APP_GUIDANCE: ['apps', 'api'],
            QueryIntent.TROUBLESHOOTING: ['api', 'mcp', 'troubleshooting'],
            QueryIntent.GENERAL_INFO: ['api', 'general']
        }
        
        self.logger.info("🧠 Airtable Expert initialized")
    
    async def initialize(self) -> None:
        """Initialize the expert system"""
        # Could load additional models, knowledge bases, etc.
        self.logger.info("✅ Airtable Expert ready")
    
    async def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a user query to determine intent and extract entities"""
        
        # Detect intent
        intent, confidence = self._detect_intent(query)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Determine required tools
        required_tools = self.intent_tool_mapping.get(intent, [])
        
        # Determine context categories
        context_categories = self.intent_context_mapping.get(intent, ['api'])
        
        # Assess complexity
        complexity = self._assess_complexity(query, entities, intent)
        
        analysis = QueryAnalysis(
            intent=intent,
            confidence=confidence,
            entities=entities,
            required_tools=required_tools,
            context_categories=context_categories,
            complexity=complexity
        )
        
        self.logger.debug(f"Query analysis: {intent.value} (confidence: {confidence:.2f})")
        return analysis
    
    def _detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Detect the primary intent of a query"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query)
                score += len(matches) * 1.0
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return QueryIntent.GENERAL_INFO, 0.5
        
        # Find highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        
        # Calculate confidence (normalize to 0-1)
        confidence = min(1.0, max_score / 3.0)  # 3+ matches = high confidence
        
        return best_intent, confidence
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract relevant entities from the query"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, query)
                matches.extend(found)
            
            # Clean and deduplicate matches
            cleaned_matches = []
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]  # Take first group if tuple
                
                match = match.strip().strip('"\',')
                if match and match not in cleaned_matches:
                    cleaned_matches.append(match)
            
            if cleaned_matches:
                entities[entity_type] = cleaned_matches
        
        return entities
    
    def _assess_complexity(self, query: str, entities: Dict, intent: QueryIntent) -> str:
        """Assess the complexity of a query"""
        complexity_score = 0
        
        # Base complexity by intent
        complex_intents = [
            QueryIntent.SCHEMA_MODIFY,
            QueryIntent.BATCH_OPERATION, 
            QueryIntent.WEBHOOK_MANAGE
        ]
        if intent in complex_intents:
            complexity_score += 2
        
        # Add complexity for multiple entities
        total_entities = sum(len(entities.get(k, [])) for k in entities)
        complexity_score += min(total_entities / 3, 2)  # Cap entity contribution
        
        # Add complexity for query length (longer = more complex)
        if len(query.split()) > 20:
            complexity_score += 1
        elif len(query.split()) > 10:
            complexity_score += 0.5
        
        # Add complexity for conditional words
        conditional_words = ['if', 'when', 'where', 'unless', 'provided', 'given']
        for word in conditional_words:
            if word.lower() in query.lower():
                complexity_score += 0.5
        
        # Classify complexity
        if complexity_score < 1:
            return "simple"
        elif complexity_score < 2.5:
            return "medium"
        else:
            return "complex"
    
    async def plan_operations(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan the sequence of operations needed to fulfill a query"""
        operations = []
        
        # Handle different intent types
        if analysis.intent == QueryIntent.DATA_QUERY:
            operations.extend(await self._plan_data_query(query, analysis))
        
        elif analysis.intent == QueryIntent.DATA_CREATE:
            operations.extend(await self._plan_data_create(query, analysis))
        
        elif analysis.intent == QueryIntent.DATA_UPDATE:
            operations.extend(await self._plan_data_update(query, analysis))
        
        elif analysis.intent == QueryIntent.DATA_DELETE:
            operations.extend(await self._plan_data_delete(query, analysis))
        
        elif analysis.intent == QueryIntent.SCHEMA_QUERY:
            operations.extend(await self._plan_schema_query(query, analysis))
        
        elif analysis.intent == QueryIntent.SCHEMA_MODIFY:
            operations.extend(await self._plan_schema_modify(query, analysis))
        
        elif analysis.intent == QueryIntent.WEBHOOK_MANAGE:
            operations.extend(await self._plan_webhook_manage(query, analysis))
        
        elif analysis.intent == QueryIntent.BATCH_OPERATION:
            operations.extend(await self._plan_batch_operation(query, analysis))
        
        # If no specific operations planned, add a default schema query
        if not operations and analysis.intent != QueryIntent.GENERAL_INFO:
            operations.append(AirtableOperation(
                tool_name="list_tables",
                parameters={},
                description="Get base structure for context"
            ))
        
        return operations
    
    async def _plan_data_query(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for data queries"""
        operations = []
        
        table_names = analysis.entities.get('table_names', [])
        
        if table_names:
            # Query specific table
            for table_name in table_names:
                # Check for filtering conditions
                params = {"table": table_name}
                
                # Add basic filtering if detected
                if re.search(r'(?i)\bwhere\b|\bfilter\b', query):
                    # This would need more sophisticated parsing in a real implementation
                    params["maxRecords"] = 100
                
                operations.append(AirtableOperation(
                    tool_name="list_records",
                    parameters=params,
                    description=f"List records from {table_name}"
                ))
        else:
            # No specific table mentioned, get schema first
            operations.append(AirtableOperation(
                tool_name="list_tables",
                parameters={},
                description="Get available tables",
                priority=1
            ))
        
        return operations
    
    async def _plan_data_create(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for data creation"""
        operations = []
        
        table_names = analysis.entities.get('table_names', [])
        
        if table_names:
            # We would need to parse field values from the query
            # For now, create a placeholder operation
            operations.append(AirtableOperation(
                tool_name="create_record",
                parameters={
                    "table": table_names[0],
                    "fields": {}  # This would be populated from query parsing
                },
                description=f"Create record in {table_names[0]}"
            ))
        else:
            # Need to know which table to create in
            operations.append(AirtableOperation(
                tool_name="list_tables",
                parameters={},
                description="Get available tables for record creation"
            ))
        
        return operations
    
    async def _plan_data_update(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for data updates"""
        operations = []
        
        record_ids = analysis.entities.get('record_ids', [])
        table_names = analysis.entities.get('table_names', [])
        
        if record_ids and table_names:
            # Direct record update
            operations.append(AirtableOperation(
                tool_name="update_record",
                parameters={
                    "table": table_names[0],
                    "recordId": record_ids[0],
                    "fields": {}  # Would be populated from query parsing
                },
                description=f"Update record {record_ids[0]}"
            ))
        else:
            # Need to search for records first
            if table_names:
                operations.append(AirtableOperation(
                    tool_name="list_records",
                    parameters={"table": table_names[0]},
                    description=f"Find records to update in {table_names[0]}"
                ))
        
        return operations
    
    async def _plan_data_delete(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for data deletion"""
        operations = []
        
        record_ids = analysis.entities.get('record_ids', [])
        table_names = analysis.entities.get('table_names', [])
        
        if record_ids and table_names:
            operations.append(AirtableOperation(
                tool_name="delete_record",
                parameters={
                    "table": table_names[0],
                    "recordId": record_ids[0]
                },
                description=f"Delete record {record_ids[0]}"
            ))
        
        return operations
    
    async def _plan_schema_query(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for schema queries"""
        operations = []
        
        table_names = analysis.entities.get('table_names', [])
        
        if table_names:
            # Describe specific table
            for table_name in table_names:
                operations.append(AirtableOperation(
                    tool_name="describe_table",
                    parameters={"table": table_name},
                    description=f"Describe table {table_name}"
                ))
        else:
            # Get full base schema
            operations.append(AirtableOperation(
                tool_name="get_base_schema",
                parameters={},
                description="Get complete base schema"
            ))
        
        return operations
    
    async def _plan_schema_modify(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan operations for schema modifications"""
        operations = []
        
        if re.search(r'(?i)\bcreate.*table\b', query):
            # Extract table name and fields from query
            operations.append(AirtableOperation(
                tool_name="create_table",
                parameters={
                    "name": "New Table",  # Would be parsed from query
                    "fields": [
                        {"name": "Name", "type": "singleLineText"}
                    ]
                },
                description="Create new table"
            ))
        
        return operations
    
    async def _plan_webhook_manage(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan webhook management operations"""
        operations = []
        
        if re.search(r'(?i)\bcreate.*webhook\b', query):
            operations.append(AirtableOperation(
                tool_name="create_webhook",
                parameters={
                    "notificationUrl": "https://example.com/webhook"  # Would be parsed from query
                },
                description="Create webhook"
            ))
        else:
            operations.append(AirtableOperation(
                tool_name="list_webhooks",
                parameters={},
                description="List existing webhooks"
            ))
        
        return operations
    
    async def _plan_batch_operation(self, query: str, analysis: QueryAnalysis) -> List[AirtableOperation]:
        """Plan batch operations"""
        operations = []
        
        table_names = analysis.entities.get('table_names', [])
        
        if table_names:
            # Determine batch operation type from query
            if re.search(r'(?i)\bcreate|add\b', query):
                operations.append(AirtableOperation(
                    tool_name="batch_create_records",
                    parameters={
                        "table": table_names[0],
                        "records": []  # Would be populated from query parsing
                    },
                    description=f"Batch create records in {table_names[0]}"
                ))
            elif re.search(r'(?i)\bupdate|modify\b', query):
                operations.append(AirtableOperation(
                    tool_name="batch_update_records",
                    parameters={
                        "table": table_names[0],
                        "records": []
                    },
                    description=f"Batch update records in {table_names[0]}"
                ))
        
        return operations
    
    async def generate_response(
        self,
        query: str,
        analysis: QueryAnalysis,
        context_chunks: List[Any],
        mcp_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a comprehensive response based on query analysis and results"""
        
        # Analyze MCP results
        successful_operations = [r for r in mcp_results if r.get('success')]
        failed_operations = [r for r in mcp_results if not r.get('success')]
        
        # Generate main response
        if analysis.intent == QueryIntent.GENERAL_INFO:
            answer = await self._generate_general_response(query, context_chunks)
        else:
            answer = await self._generate_operation_response(
                query, analysis, successful_operations, failed_operations
            )
        
        # Add helpful suggestions
        suggestions = await self._generate_suggestions(query, analysis, mcp_results)
        
        # Format response
        response = {
            'success': len(failed_operations) == 0,
            'answer': answer,
            'intent': analysis.intent.value,
            'confidence': analysis.confidence,
            'operations_executed': len(mcp_results),
            'successful_operations': len(successful_operations),
            'failed_operations': len(failed_operations)
        }
        
        if suggestions:
            response['suggestions'] = suggestions
        
        if failed_operations:
            response['errors'] = [op.get('error', 'Unknown error') for op in failed_operations]
        
        # Include relevant data from successful operations
        if successful_operations:
            response['data'] = [op.get('result') for op in successful_operations]
        
        return response
    
    async def _generate_general_response(self, query: str, context_chunks: List[Any]) -> str:
        """Generate response for general information queries"""
        
        # For general queries, provide information from context
        relevant_info = []
        
        for chunk in context_chunks[:3]:  # Use top 3 most relevant chunks
            relevant_info.append(f"**{chunk.title}**\n{chunk.content[:500]}...")
        
        if relevant_info:
            return f"Based on the Airtable documentation:\n\n" + "\n\n---\n\n".join(relevant_info)
        else:
            return "I can help you with Airtable operations including data management, schema design, formulas, apps, and more. What specific aspect would you like to know about?"
    
    async def _generate_operation_response(
        self,
        query: str,
        analysis: QueryAnalysis,
        successful_operations: List[Dict],
        failed_operations: List[Dict]
    ) -> str:
        """Generate response based on operation results"""
        
        response_parts = []
        
        if successful_operations:
            response_parts.append(f"✅ Successfully executed {len(successful_operations)} operation(s):")
            
            for operation in successful_operations:
                tool_name = operation.get('tool', 'unknown')
                result = operation.get('result', {})
                
                if tool_name == 'list_records':
                    records = result.get('content', [{}])[0].get('text', '')
                    if 'Found' in records:
                        response_parts.append(f"• {records}")
                elif tool_name == 'create_record':
                    response_parts.append("• Record created successfully")
                elif tool_name == 'list_tables':
                    response_parts.append("• Retrieved table information")
                else:
                    response_parts.append(f"• {tool_name} completed")
        
        if failed_operations:
            response_parts.append(f"\n❌ {len(failed_operations)} operation(s) failed:")
            for operation in failed_operations:
                error = operation.get('error', 'Unknown error')
                response_parts.append(f"• {error}")
        
        if not response_parts:
            response_parts.append("No operations were executed. This might be a general information query.")
        
        return "\n".join(response_parts)
    
    async def _generate_suggestions(
        self,
        query: str,
        analysis: QueryAnalysis,
        mcp_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate helpful suggestions for the user"""
        
        suggestions = []
        
        # Suggest improvements based on complexity
        if analysis.complexity == "complex":
            suggestions.append("Consider breaking this into multiple simpler requests for better results")
        
        # Suggest related operations
        if analysis.intent == QueryIntent.DATA_QUERY:
            suggestions.append("You can also create, update, or delete records in this table")
            suggestions.append("Try using filters to narrow down your search")
        
        elif analysis.intent == QueryIntent.DATA_CREATE:
            suggestions.append("You can create multiple records at once using batch operations")
            suggestions.append("Consider setting up webhooks for notifications when records are created")
        
        elif analysis.intent == QueryIntent.SCHEMA_QUERY:
            suggestions.append("You can also create new tables and fields to extend your base")
            suggestions.append("Check out field types reference for advanced field configurations")
        
        # Suggest based on failed operations
        failed_operations = [r for r in mcp_results if not r.get('success')]
        if failed_operations:
            suggestions.append("Some operations failed. Try checking your table and field names")
            suggestions.append("Make sure you have the necessary permissions for these operations")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    async def get_error_suggestions(self, error_message: str) -> List[str]:
        """Get suggestions for handling specific errors"""
        suggestions = []
        
        error_lower = error_message.lower()
        
        if "not found" in error_lower:
            suggestions.extend([
                "Check that the table name is spelled correctly",
                "Verify the record ID is valid",
                "Make sure you have access to this base"
            ])
        
        elif "permission" in error_lower or "forbidden" in error_lower:
            suggestions.extend([
                "Check your Airtable permissions for this base",
                "Verify your API token has the required scopes",
                "Contact the base owner for additional access"
            ])
        
        elif "rate limit" in error_lower:
            suggestions.extend([
                "Wait a few seconds before retrying",
                "Consider using batch operations to reduce API calls",
                "Implement exponential backoff for retries"
            ])
        
        elif "validation" in error_lower or "invalid" in error_lower:
            suggestions.extend([
                "Check that field values match the expected format",
                "Verify required fields are provided",
                "Review field types and constraints"
            ])
        
        else:
            suggestions.extend([
                "Check the Airtable API documentation for this endpoint",
                "Verify your request parameters are correct",
                "Try a simpler version of the operation first"
            ])
        
        return suggestions[:3]