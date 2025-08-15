#!/usr/bin/env python3
"""
🤖 Basic Airtable AI Agent
Simplified version for testing without ML dependencies.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import our basic modules
from .context_manager_basic import ContextManagerBasic, DocumentChunk
from .mcp_client import MCPClient, MCPError
from .airtable_expert import AirtableExpert, AirtableOperation


@dataclass
class AgentConfig:
    """Configuration for the AI Agent"""
    name: str = "Airtable AI Agent"
    version: str = "1.0.0"
    max_context_tokens: int = 128000
    mcp_server_url: str = "http://localhost:8010/mcp"
    log_level: str = "INFO"
    enable_metrics: bool = True
    cache_duration: int = 300


class AirtableAIAgentBasic:
    """
    Basic Airtable AI Agent for testing without ML dependencies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI Agent"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize core components
        self.context_manager = ContextManagerBasic(
            max_tokens=self.config.max_context_tokens
        )
        self.mcp_client = MCPClient(self.config.mcp_server_url)
        self.airtable_expert = AirtableExpert()
        
        # Performance tracking
        self.metrics = {
            'requests_handled': 0,
            'mcp_calls_made': 0,
            'context_optimizations': 0,
            'errors_handled': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        self.logger.info(f"🤖 {self.config.name} v{self.config.version} initialized")
    
    def _load_config(self, config_path: Optional[str]) -> AgentConfig:
        """Load agent configuration"""
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return AgentConfig(**config_data)
        return AgentConfig()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("airtable_ai_agent_basic")
        logger.setLevel(getattr(logging, self.config.log_level))
        return logger
    
    async def initialize(self) -> None:
        """Initialize all agent components"""
        print(f"🚀 Initializing {self.config.name}")
        
        # Initialize context manager
        print("Loading Airtable documentation...")
        await self.context_manager.initialize()
        print("✅ Airtable documentation loaded")
        
        # Test MCP connection
        print("Testing MCP connection...")
        connection_result = await self.mcp_client.test_connection()
        if connection_result.get('status') == 'healthy':
            print("✅ MCP connection established")
        else:
            print(f"⚠️ MCP connection issue: {connection_result}")
        
        # Initialize Airtable expert
        print("Initializing Airtable expert...")
        await self.airtable_expert.initialize()
        print("✅ Airtable expert ready")
        
        print("🎯 Agent initialization complete")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query about Airtable operations.
        """
        self.metrics['requests_handled'] += 1
        start_time = datetime.now()
        
        try:
            self.logger.info(f"📝 Processing query: {query[:100]}...")
            
            # Analyze query to determine intent and required context
            analysis = await self.airtable_expert.analyze_query(query)
            self.logger.debug(f"Query analysis: {analysis}")
            
            # Prepare optimal context for the query
            context_chunks = await self.context_manager.get_relevant_context(
                query=query,
                analysis=analysis.__dict__ if hasattr(analysis, '__dict__') else None,
                previous_context=context
            )
            
            # Determine required MCP operations
            operations = await self.airtable_expert.plan_operations(query, analysis)
            self.logger.debug(f"Planned operations: {len(operations)}")
            
            # Execute MCP operations
            mcp_results = []
            for operation in operations:
                try:
                    result = await self.mcp_client.execute_tool(
                        operation.tool_name,
                        operation.parameters
                    )
                    mcp_results.append({
                        'operation': operation.tool_name,
                        'success': True,
                        'result': result
                    })
                    self.metrics['mcp_calls_made'] += 1
                except MCPError as e:
                    self.logger.error(f"MCP operation failed: {e}")
                    mcp_results.append({
                        'operation': operation.tool_name,
                        'success': False,
                        'error': str(e)
                    })
                    self.metrics['errors_handled'] += 1
            
            # Generate comprehensive response
            response = await self.airtable_expert.generate_response(
                query=query,
                analysis=analysis,
                context_chunks=context_chunks,
                mcp_results=mcp_results
            )
            
            # Add metadata
            response.update({
                'metadata': {
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'context_chunks_used': len(context_chunks),
                    'mcp_operations_executed': len(operations),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            })
            
            self.logger.info(f"✅ Query processed successfully in {response['metadata']['processing_time']:.2f}s")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error processing query: {e}")
            self.metrics['errors_handled'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'suggestions': await self.airtable_expert.get_error_suggestions(str(e)),
                'metadata': {
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive information about agent capabilities"""
        try:
            mcp_tools = await self.mcp_client.list_available_tools()
        except Exception as e:
            mcp_tools = []
            self.logger.warning(f"Could not list MCP tools: {e}")
        
        return {
            'agent_info': {
                'name': self.config.name,
                'version': self.config.version,
                'status': 'active'
            },
            'airtable_knowledge': {
                'documentation_chunks': await self.context_manager.get_stats(),
                'api_coverage': '100%',
                'supported_operations': 'All Airtable Web API endpoints'
            },
            'mcp_integration': {
                'server_url': self.config.mcp_server_url,
                'available_tools': len(mcp_tools),
                'tool_categories': [
                    'Data Operations',
                    'Webhook Management', 
                    'Schema Discovery',
                    'Table Management',
                    'Field Management',
                    'Batch Operations',
                    'Attachment Management',
                    'Advanced Views',
                    'Base Management'
                ]
            },
            'performance_metrics': self.metrics,
            'context_management': {
                'max_tokens': self.config.max_context_tokens,
                'optimization_enabled': True,
                'caching_enabled': True
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        checks = {}
        
        try:
            # Test MCP connection
            checks['mcp_connection'] = await self.mcp_client.test_connection()
        except Exception as e:
            checks['mcp_connection'] = {'status': 'error', 'error': str(e)}
        
        try:
            # Test context manager
            checks['context_manager'] = await self.context_manager.health_check()
        except Exception as e:
            checks['context_manager'] = {'status': 'error', 'error': str(e)}
        
        # Overall health
        all_healthy = all(
            check.get('status') == 'healthy' 
            for check in checks.values()
        )
        
        return {
            'overall_status': 'healthy' if all_healthy else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': checks,
            'uptime': (datetime.now(timezone.utc) - self.metrics['start_time']).total_seconds(),
            'metrics': self.metrics
        }
    
    def display_status(self) -> None:
        """Display current agent status"""
        uptime = datetime.now(timezone.utc) - self.metrics['start_time']
        
        print(f"\n🤖 {self.config.name} Status")
        print("-" * 40)
        print(f"Status: 🟢 Active")
        print(f"Uptime: {uptime}")
        print(f"Requests Handled: {self.metrics['requests_handled']}")
        print(f"MCP Calls Made: {self.metrics['mcp_calls_made']}")
        print(f"Context Optimizations: {self.metrics['context_optimizations']}")
        print(f"Errors Handled: {self.metrics['errors_handled']}")
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the agent"""
        self.logger.info("🔄 Shutting down agent...")
        
        await self.mcp_client.close()
        await self.context_manager.cleanup()
        
        self.logger.info("✅ Agent shutdown complete")


async def main():
    """Main entry point for testing"""
    agent = AirtableAIAgentBasic()
    
    try:
        await agent.initialize()
        
        print("\n" + "="*50)
        print("🤖 Airtable AI Agent Ready!")
        print("Type 'help' for commands, 'quit' to exit.")
        print("="*50)
        
        while True:
            try:
                query = input("\nAsk me anything about Airtable: ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif query.lower() == 'help':
                    print("\nAvailable commands:")
                    print("• Ask any Airtable-related question")
                    print("• 'status' - Show agent status")
                    print("• 'capabilities' - Show agent capabilities")
                    print("• 'health' - Perform health check")
                    print("• 'quit' - Exit the agent")
                    continue
                elif query.lower() == 'status':
                    agent.display_status()
                    continue
                elif query.lower() == 'capabilities':
                    caps = await agent.get_capabilities()
                    print(json.dumps(caps, indent=2))
                    continue
                elif query.lower() == 'health':
                    health = await agent.health_check()
                    print(json.dumps(health, indent=2))
                    continue
                
                # Process the query
                print("Processing...")
                response = await agent.process_query(query)
                
                if response.get('success', True):
                    print(f"\n🤖 Response:")
                    print(response.get('answer', 'No response generated'))
                    
                    if 'actions' in response:
                        print(f"\nActions taken: {len(response['actions'])}")
                else:
                    print(f"\n❌ Error: {response.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())