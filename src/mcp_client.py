#!/usr/bin/env python3
"""
🔗 MCP Client for Airtable AI Agent
Perfect integration with our comprehensive airtable-mcp server.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import aiohttp
from datetime import datetime, timezone


class MCPError(Exception):
    """Exception raised for MCP-related errors"""
    def __init__(self, message: str, code: int = -32603, data: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


@dataclass
class MCPTool:
    """Represents an MCP tool with its metadata"""
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str = "general"


class MCPClient:
    """
    Client for interacting with the Airtable MCP Server.
    
    Provides seamless integration with all 33 tools in our comprehensive MCP server.
    """
    
    def __init__(self, server_url: str = "http://localhost:8010/mcp"):
        self.server_url = server_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("mcp_client")
        self.request_id = 0
        
        # Tool categories mapping
        self.tool_categories = {
            # Data Operations
            'list_tables': 'data',
            'list_records': 'data',
            'get_record': 'data', 
            'create_record': 'data',
            'update_record': 'data',
            'delete_record': 'data',
            'search_records': 'data',
            
            # Webhook Management
            'list_webhooks': 'webhooks',
            'create_webhook': 'webhooks',
            'delete_webhook': 'webhooks', 
            'get_webhook_payloads': 'webhooks',
            'refresh_webhook': 'webhooks',
            
            # Schema Discovery
            'list_bases': 'schema',
            'get_base_schema': 'schema',
            'describe_table': 'schema',
            'list_field_types': 'schema',
            'get_table_views': 'schema',
            
            # Table Management  
            'create_table': 'tables',
            'update_table': 'tables',
            'delete_table': 'tables',
            
            # Field Management
            'create_field': 'fields',
            'update_field': 'fields', 
            'delete_field': 'fields',
            
            # Batch Operations
            'batch_create_records': 'batch',
            'batch_update_records': 'batch',
            'batch_delete_records': 'batch',
            'batch_upsert_records': 'batch',
            
            # Attachment Management
            'upload_attachment': 'attachments',
            
            # Advanced Views
            'create_view': 'views',
            'get_view_metadata': 'views',
            
            # Base Management
            'create_base': 'bases',
            'list_collaborators': 'bases',
            'list_shares': 'bases'
        }
        
        # Performance tracking
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_request_time': None
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is available"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        await self._ensure_session()
        
        self.request_id += 1
        request_start = datetime.now()
        
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        try:
            self.logger.debug(f"Making MCP request: {method} with params: {params}")
            
            async with self.session.post(
                self.server_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                response_time = (datetime.now() - request_start).total_seconds()
                self._update_stats(response_time, success=response.status == 200)
                
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPError(
                        f"HTTP {response.status}: {error_text}",
                        code=-32603
                    )
                
                response_data = await response.json()
                
                if "error" in response_data:
                    error = response_data["error"]
                    raise MCPError(
                        error.get("message", "Unknown MCP error"),
                        code=error.get("code", -32603),
                        data=error.get("data")
                    )
                
                return response_data.get("result", {})
        
        except aiohttp.ClientError as e:
            self._update_stats(0, success=False)
            raise MCPError(f"Network error: {str(e)}", code=-32603)
        
        except json.JSONDecodeError as e:
            self._update_stats(0, success=False)
            raise MCPError(f"Invalid JSON response: {str(e)}", code=-32700)
    
    def _update_stats(self, response_time: float, success: bool) -> None:
        """Update performance statistics"""
        self.stats['requests_made'] += 1
        self.stats['last_request_time'] = datetime.now(timezone.utc)
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        current_avg = self.stats['average_response_time']
        total_requests = self.stats['requests_made']
        self.stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to MCP server"""
        try:
            # Try to list available tools as a connection test
            tools = await self.list_available_tools()
            await self.close()  # Clean up session
            return {
                'status': 'healthy',
                'tools_available': len(tools),
                'server_url': self.server_url
            }
        except Exception as e:
            await self.close()  # Clean up session even on error
            return {
                'status': 'error',
                'error': str(e),
                'server_url': self.server_url
            }
    
    async def list_available_tools(self) -> List[MCPTool]:
        """Get list of all available MCP tools"""
        try:
            # Make a tools/list request
            result = await self._make_request("tools/list", {})
            
            tools = []
            for tool_data in result.get("tools", []):
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("inputSchema", {}),
                    category=self.tool_categories.get(tool_data["name"], "general")
                )
                tools.append(tool)
            
            return tools
            
        except MCPError:
            # Fallback to known tools if the server doesn't support tools/list
            return self._get_known_tools()
    
    def _get_known_tools(self) -> List[MCPTool]:
        """Return list of known tools if server doesn't provide them"""
        known_tools = []
        
        for tool_name, category in self.tool_categories.items():
            tool = MCPTool(
                name=tool_name,
                description=f"{tool_name.replace('_', ' ').title()} operation",
                parameters={},
                category=category
            )
            known_tools.append(tool)
        
        return known_tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific MCP tool"""
        if tool_name not in self.tool_categories:
            raise MCPError(f"Unknown tool: {tool_name}", code=-32601)
        
        self.logger.info(f"Executing tool: {tool_name}")
        
        try:
            result = await self._make_request("tools/call", {
                "name": tool_name,
                "arguments": parameters
            })
            
            return {
                'success': True,
                'tool': tool_name,
                'result': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except MCPError as e:
            self.logger.error(f"Tool execution failed: {e.message}")
            return {
                'success': False,
                'tool': tool_name,
                'error': e.message,
                'error_code': e.code,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    # Data Operations
    async def list_tables(self) -> Dict[str, Any]:
        """List all tables in the base"""
        return await self.execute_tool("list_tables", {})
    
    async def list_records(self, table: str, **kwargs) -> Dict[str, Any]:
        """List records from a table"""
        params = {"table": table}
        params.update(kwargs)
        return await self.execute_tool("list_records", params)
    
    async def get_record(self, table: str, record_id: str) -> Dict[str, Any]:
        """Get a specific record"""
        return await self.execute_tool("get_record", {
            "table": table,
            "recordId": record_id
        })
    
    async def create_record(self, table: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        return await self.execute_tool("create_record", {
            "table": table,
            "fields": fields
        })
    
    async def update_record(self, table: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record"""
        return await self.execute_tool("update_record", {
            "table": table,
            "recordId": record_id,
            "fields": fields
        })
    
    async def delete_record(self, table: str, record_id: str) -> Dict[str, Any]:
        """Delete a record"""
        return await self.execute_tool("delete_record", {
            "table": table,
            "recordId": record_id
        })
    
    # Batch Operations
    async def batch_create_records(self, table: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple records at once"""
        return await self.execute_tool("batch_create_records", {
            "table": table,
            "records": records
        })
    
    async def batch_update_records(self, table: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update multiple records at once"""
        return await self.execute_tool("batch_update_records", {
            "table": table,
            "records": records
        })
    
    async def batch_delete_records(self, table: str, record_ids: List[str]) -> Dict[str, Any]:
        """Delete multiple records at once"""
        return await self.execute_tool("batch_delete_records", {
            "table": table,
            "recordIds": record_ids
        })
    
    # Schema Operations
    async def get_base_schema(self) -> Dict[str, Any]:
        """Get complete base schema"""
        return await self.execute_tool("get_base_schema", {})
    
    async def describe_table(self, table: str) -> Dict[str, Any]:
        """Get detailed table information"""
        return await self.execute_tool("describe_table", {
            "table": table
        })
    
    async def create_table(self, name: str, fields: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Create a new table"""
        params = {
            "name": name,
            "fields": fields
        }
        params.update(kwargs)
        return await self.execute_tool("create_table", params)
    
    # Webhook Operations
    async def create_webhook(self, notification_url: str, **kwargs) -> Dict[str, Any]:
        """Create a new webhook"""
        params = {
            "notificationUrl": notification_url
        }
        params.update(kwargs)
        return await self.execute_tool("create_webhook", params)
    
    async def list_webhooks(self) -> Dict[str, Any]:
        """List all webhooks"""
        return await self.execute_tool("list_webhooks", {})
    
    async def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook"""
        return await self.execute_tool("delete_webhook", {
            "webhookId": webhook_id
        })
    
    # Utility methods
    async def bulk_operation(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple operations in parallel"""
        tasks = []
        
        for operation in operations:
            tool_name = operation.get("tool")
            parameters = operation.get("parameters", {})
            
            if tool_name:
                task = self.execute_tool(tool_name, parameters)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'operation_index': i,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get client performance statistics"""
        return {
            'server_url': self.server_url,
            'stats': self.stats.copy(),
            'tool_categories': len(set(self.tool_categories.values())),
            'total_tools': len(self.tool_categories)
        }
    
    async def close(self) -> None:
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        
        self.logger.info("MCP client session closed")