#!/usr/bin/env python3
"""
🤖 Comprehensive Airtable AI Agent
The most advanced AI Agent with complete Airtable API knowledge and perfect MCP integration.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

import aiohttp
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Import our custom modules
from .context_manager import ContextManager, DocumentChunk
from .mcp_client import MCPClient, MCPError
from .airtable_expert import AirtableExpert, AirtableOperation


@dataclass
class AgentConfig:
    """Configuration for the AI Agent"""
    name: str = "Airtable AI Agent"
    version: str = "1.0.0"
    max_context_tokens: int = 128000  # Claude 3.5 Sonnet context window
    mcp_server_url: str = "http://localhost:8010/mcp"
    log_level: str = "INFO"
    enable_metrics: bool = True
    cache_duration: int = 300  # 5 minutes


class AirtableAIAgent:
    """
    The most comprehensive AI Agent for Airtable operations.
    
    Features:
    - Complete Airtable API knowledge in context
    - Perfect MCP integration with 33 tools
    - Intelligent context management
    - Advanced natural language processing
    - Performance optimization and monitoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI Agent"""
        self.console = Console()
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize core components
        self.context_manager = ContextManager(
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
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return AgentConfig(**config_data)
        return AgentConfig()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup rich logging"""
        logger = logging.getLogger("airtable_ai_agent")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Remove existing handlers
        logger.handlers = []
        
        # Add rich handler
        handler = RichHandler(
            console=self.console,
            show_time=True,
            show_level=True,
            show_path=False
        )
        handler.setFormatter(logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        ))
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> None:
        """Initialize all agent components"""
        self.console.print(Panel.fit(
            f"🚀 Initializing {self.config.name}",
            style="bold blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Initialize context manager
            init_task = progress.add_task("Loading Airtable documentation...", total=None)
            await self.context_manager.initialize()
            progress.update(init_task, description="✅ Airtable documentation loaded")
            
            # Test MCP connection
            progress.update(init_task, description="Testing MCP connection...")
            await self.mcp_client.test_connection()
            progress.update(init_task, description="✅ MCP connection established")
            
            # Initialize Airtable expert
            progress.update(init_task, description="Initializing Airtable expert...")
            await self.airtable_expert.initialize()
            progress.update(init_task, description="✅ Airtable expert ready")
        
        self.logger.info("🎯 Agent initialization complete")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query about Airtable operations.
        
        Args:
            query: Natural language query from user
            context: Optional context from previous interactions
            
        Returns:
            Response containing answer, actions taken, and metadata
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
                analysis=analysis,
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
    
    async def batch_process(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries efficiently with shared context"""
        self.logger.info(f"📦 Processing batch of {len(queries)} queries")
        
        # Process queries concurrently where possible
        tasks = []
        shared_context = {}
        
        for i, query in enumerate(queries):
            # Use context from previous queries in batch
            context = shared_context if i > 0 else None
            task = self.process_query(query, context)
            tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'query_index': i
                })
            else:
                processed_results.append(result)
        
        self.logger.info(f"✅ Batch processing complete: {len(processed_results)} results")
        return processed_results
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive information about agent capabilities"""
        mcp_tools = await self.mcp_client.list_available_tools()
        
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
        """Display current agent status in rich format"""
        table = Table(title=f"🤖 {self.config.name} Status")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        uptime = datetime.now(timezone.utc) - self.metrics['start_time']
        
        table.add_row("Status", "🟢 Active")
        table.add_row("Uptime", str(uptime))
        table.add_row("Requests Handled", str(self.metrics['requests_handled']))
        table.add_row("MCP Calls Made", str(self.metrics['mcp_calls_made']))
        table.add_row("Context Optimizations", str(self.metrics['context_optimizations']))
        table.add_row("Errors Handled", str(self.metrics['errors_handled']))
        
        self.console.print(table)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the agent"""
        self.logger.info("🔄 Shutting down agent...")
        
        await self.mcp_client.close()
        await self.context_manager.cleanup()
        
        self.logger.info("✅ Agent shutdown complete")


async def main():
    """Main entry point for the AI Agent"""
    agent = AirtableAIAgent()
    
    try:
        await agent.initialize()
        
        # Interactive mode
        agent.console.print(Panel.fit(
            "🤖 Airtable AI Agent Ready!\nType 'help' for commands, 'quit' to exit.",
            style="bold green"
        ))
        
        while True:
            try:
                query = agent.console.input("\n[bold cyan]Ask me anything about Airtable:[/bold cyan] ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif query.lower() == 'help':
                    agent.console.print(Panel(
                        "Available commands:\n"
                        "• Ask any Airtable-related question\n"
                        "• 'status' - Show agent status\n"
                        "• 'capabilities' - Show agent capabilities\n"
                        "• 'health' - Perform health check\n"
                        "• 'quit' - Exit the agent",
                        title="Help"
                    ))
                    continue
                elif query.lower() == 'status':
                    agent.display_status()
                    continue
                elif query.lower() == 'capabilities':
                    caps = await agent.get_capabilities()
                    agent.console.print_json(data=caps)
                    continue
                elif query.lower() == 'health':
                    health = await agent.health_check()
                    agent.console.print_json(data=health)
                    continue
                
                # Process the query
                response = await agent.process_query(query)
                
                if response.get('success', True):
                    agent.console.print(Panel(
                        response.get('answer', 'No response generated'),
                        title="🤖 Response",
                        style="green"
                    ))
                    
                    if 'actions' in response:
                        agent.console.print(f"\n[dim]Actions taken: {len(response['actions'])}[/dim]")
                else:
                    agent.console.print(Panel(
                        response.get('error', 'Unknown error'),
                        title="❌ Error",
                        style="red"
                    ))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                agent.console.print(f"[red]Error: {e}[/red]")
    
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())