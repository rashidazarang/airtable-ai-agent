#!/usr/bin/env python3
"""
🧪 Tests for Airtable AI Agent
Comprehensive test suite ensuring reliability and performance.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.agent import AirtableAIAgent, AgentConfig
from src.context_manager import ContextManager, DocumentChunk
from src.mcp_client import MCPClient, MCPError
from src.airtable_expert import AirtableExpert, QueryIntent, QueryAnalysis


class TestAirtableAIAgent:
    """Test cases for the main AI Agent"""
    
    @pytest.fixture
    async def agent(self):
        """Create a test agent instance"""
        config = AgentConfig(
            name="Test Agent",
            max_context_tokens=1000,
            mcp_server_url="http://localhost:8010/mcp",
            log_level="DEBUG"
        )
        
        agent = AirtableAIAgent()
        agent.config = config
        
        # Mock components
        agent.context_manager = AsyncMock(spec=ContextManager)
        agent.mcp_client = AsyncMock(spec=MCPClient)
        agent.airtable_expert = AsyncMock(spec=AirtableExpert)
        
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization"""
        agent = AirtableAIAgent()
        assert agent.config.name == "Airtable AI Agent"
        assert agent.metrics['requests_handled'] == 0
    
    @pytest.mark.asyncio
    async def test_process_simple_query(self, agent):
        """Test processing a simple query"""
        # Setup mocks
        analysis = QueryAnalysis(
            intent=QueryIntent.DATA_QUERY,
            confidence=0.8,
            entities={'table_names': ['Tasks']},
            required_tools=['list_records'],
            context_categories=['api'],
            complexity='simple'
        )
        
        agent.airtable_expert.analyze_query.return_value = analysis
        agent.airtable_expert.plan_operations.return_value = []
        agent.airtable_expert.generate_response.return_value = {
            'success': True,
            'answer': 'Query processed successfully',
            'intent': 'data_query'
        }
        
        agent.context_manager.get_relevant_context.return_value = []
        
        # Test
        query = "List all tasks"
        response = await agent.process_query(query)
        
        # Assertions
        assert response['success'] is True
        assert 'answer' in response
        assert 'metadata' in response
        assert agent.metrics['requests_handled'] == 1
    
    @pytest.mark.asyncio
    async def test_process_query_with_mcp_operations(self, agent):
        """Test query processing with MCP operations"""
        from src.airtable_expert import AirtableOperation
        
        # Setup mocks
        analysis = QueryAnalysis(
            intent=QueryIntent.DATA_CREATE,
            confidence=0.9,
            entities={'table_names': ['Tasks']},
            required_tools=['create_record'],
            context_categories=['api', 'mcp'],
            complexity='medium'
        )
        
        operation = AirtableOperation(
            tool_name='create_record',
            parameters={'table': 'Tasks', 'fields': {'Name': 'New Task'}},
            description='Create new task'
        )
        
        agent.airtable_expert.analyze_query.return_value = analysis
        agent.airtable_expert.plan_operations.return_value = [operation]
        agent.context_manager.get_relevant_context.return_value = []
        agent.mcp_client.execute_tool.return_value = {
            'success': True,
            'result': {'record_id': 'rec123'}
        }
        agent.airtable_expert.generate_response.return_value = {
            'success': True,
            'answer': 'Record created successfully'
        }
        
        # Test
        query = "Create a new task named 'Test Task'"
        response = await agent.process_query(query)
        
        # Assertions
        assert response['success'] is True
        assert agent.metrics['mcp_calls_made'] == 1
        agent.mcp_client.execute_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_with_error(self, agent):
        """Test error handling in query processing"""
        # Setup mock to raise exception
        agent.airtable_expert.analyze_query.side_effect = Exception("Test error")
        
        # Test
        query = "Test query"
        response = await agent.process_query(query)
        
        # Assertions
        assert response['success'] is False
        assert 'error' in response
        assert agent.metrics['errors_handled'] == 1
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, agent):
        """Test batch query processing"""
        # Setup mocks for successful processing
        agent.airtable_expert.analyze_query.return_value = QueryAnalysis(
            intent=QueryIntent.DATA_QUERY,
            confidence=0.8,
            entities={},
            required_tools=[],
            context_categories=['api'],
            complexity='simple'
        )
        agent.airtable_expert.plan_operations.return_value = []
        agent.airtable_expert.generate_response.return_value = {
            'success': True,
            'answer': 'Query processed'
        }
        agent.context_manager.get_relevant_context.return_value = []
        
        # Test
        queries = ["Query 1", "Query 2", "Query 3"]
        responses = await agent.batch_process(queries)
        
        # Assertions
        assert len(responses) == 3
        assert all(r.get('success', True) for r in responses)
    
    @pytest.mark.asyncio
    async def test_get_capabilities(self, agent):
        """Test capabilities retrieval"""
        agent.mcp_client.list_available_tools.return_value = [
            MagicMock(name='list_records'),
            MagicMock(name='create_record')
        ]
        agent.context_manager.get_stats.return_value = {
            'total_chunks': 100,
            'total_tokens': 50000
        }
        
        capabilities = await agent.get_capabilities()
        
        assert 'agent_info' in capabilities
        assert 'airtable_knowledge' in capabilities
        assert 'mcp_integration' in capabilities
        assert capabilities['agent_info']['name'] == agent.config.name
    
    @pytest.mark.asyncio
    async def test_health_check(self, agent):
        """Test health check functionality"""
        # Setup successful health checks
        agent.mcp_client.test_connection.return_value = {'status': 'healthy'}
        agent.context_manager.health_check.return_value = {'status': 'healthy'}
        
        health = await agent.health_check()
        
        assert health['overall_status'] == 'healthy'
        assert 'checks' in health
        assert 'uptime' in health


class TestContextManager:
    """Test cases for Context Manager"""
    
    @pytest.fixture
    def context_manager(self):
        """Create test context manager"""
        return ContextManager(max_tokens=1000)
    
    def test_smart_chunking(self, context_manager):
        """Test intelligent content chunking"""
        content = """
# Title
Content here

## Section 1
Section 1 content

### Subsection 1.1
Subsection content

## Section 2
Section 2 content
"""
        
        chunks = context_manager._smart_chunking(content, "test")
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, tuple) for chunk in chunks)
        assert all(len(chunk) == 2 for chunk in chunks)  # (content, title)
    
    def test_truncate_content(self, context_manager):
        """Test content truncation"""
        content = "This is a test content that is quite long. " * 100
        max_tokens = 50
        
        truncated = context_manager._truncate_content(content, max_tokens)
        
        assert len(truncated) < len(content)
        assert "[Content truncated...]" in truncated
    
    @pytest.mark.asyncio
    async def test_get_relevant_context(self, context_manager):
        """Test context retrieval"""
        # Mock embedder
        context_manager.embedder = MagicMock()
        context_manager.embedder.encode.return_value = [0.1, 0.2, 0.3]
        
        # Add test chunks
        chunk = DocumentChunk(
            id="test1",
            content="Test content about Airtable API",
            title="API Guide",
            category="api",
            tokens=50,
            embedding=[0.1, 0.2, 0.3]
        )
        context_manager.chunks = [chunk]
        
        # Test
        relevant_chunks = await context_manager.get_relevant_context("Airtable API")
        
        assert len(relevant_chunks) >= 0
        assert isinstance(relevant_chunks, list)


class TestMCPClient:
    """Test cases for MCP Client"""
    
    @pytest.fixture
    def mcp_client(self):
        """Create test MCP client"""
        return MCPClient("http://localhost:8010/mcp")
    
    @pytest.mark.asyncio
    async def test_connection_test(self, mcp_client):
        """Test MCP connection testing"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"tools": []}
            }
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await mcp_client.test_connection()
            
            assert result['status'] == 'healthy'
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, mcp_client):
        """Test successful tool execution"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"content": [{"type": "text", "text": "Success"}]}
            }
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await mcp_client.execute_tool("list_tables", {})
            
            assert result['success'] is True
            assert result['tool'] == 'list_tables'
    
    @pytest.mark.asyncio
    async def test_execute_tool_error(self, mcp_client):
        """Test tool execution error handling"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock error response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {"code": -32603, "message": "Test error"}
            }
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await mcp_client.execute_tool("invalid_tool", {})
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_tool_categorization(self, mcp_client):
        """Test tool category mapping"""
        assert mcp_client.tool_categories['list_records'] == 'data'
        assert mcp_client.tool_categories['create_webhook'] == 'webhooks'
        assert mcp_client.tool_categories['get_base_schema'] == 'schema'


class TestAirtableExpert:
    """Test cases for Airtable Expert"""
    
    @pytest.fixture
    def expert(self):
        """Create test Airtable expert"""
        return AirtableExpert()
    
    def test_intent_detection(self, expert):
        """Test query intent detection"""
        # Test data query intent
        intent, confidence = expert._detect_intent("List all records in the Tasks table")
        assert intent == QueryIntent.DATA_QUERY
        assert confidence > 0.5
        
        # Test create intent
        intent, confidence = expert._detect_intent("Create a new record in Projects")
        assert intent == QueryIntent.DATA_CREATE
        assert confidence > 0.5
        
        # Test schema query intent
        intent, confidence = expert._detect_intent("What fields are in the Users table?")
        assert intent == QueryIntent.SCHEMA_QUERY
        assert confidence > 0.5
    
    def test_entity_extraction(self, expert):
        """Test entity extraction from queries"""
        query = "List records from the Tasks table where Status is Active"
        entities = expert._extract_entities(query)
        
        # Should extract table name
        assert 'table_names' in entities
        assert len(entities['table_names']) > 0
    
    def test_complexity_assessment(self, expert):
        """Test query complexity assessment"""
        simple_query = "List tasks"
        complex_query = "Create a new project with multiple tasks and set up webhooks for notifications when tasks are completed and also update the status field"
        
        simple_complexity = expert._assess_complexity(simple_query, {}, QueryIntent.DATA_QUERY)
        complex_complexity = expert._assess_complexity(complex_query, {}, QueryIntent.SCHEMA_MODIFY)
        
        assert simple_complexity == "simple"
        assert complex_complexity in ["medium", "complex"]
    
    @pytest.mark.asyncio
    async def test_analyze_query(self, expert):
        """Test comprehensive query analysis"""
        await expert.initialize()
        
        query = "Show me all active tasks from the Projects table"
        analysis = await expert.analyze_query(query)
        
        assert isinstance(analysis, QueryAnalysis)
        assert analysis.intent in [QueryIntent.DATA_QUERY, QueryIntent.GENERAL_INFO]
        assert analysis.confidence >= 0.0
        assert analysis.complexity in ["simple", "medium", "complex"]
    
    @pytest.mark.asyncio
    async def test_operation_planning(self, expert):
        """Test operation planning"""
        analysis = QueryAnalysis(
            intent=QueryIntent.DATA_QUERY,
            confidence=0.8,
            entities={'table_names': ['Tasks']},
            required_tools=['list_records'],
            context_categories=['api'],
            complexity='simple'
        )
        
        operations = await expert.plan_operations("List tasks", analysis)
        
        assert len(operations) > 0
        assert all(hasattr(op, 'tool_name') for op in operations)
        assert all(hasattr(op, 'parameters') for op in operations)
    
    @pytest.mark.asyncio
    async def test_response_generation(self, expert):
        """Test response generation"""
        analysis = QueryAnalysis(
            intent=QueryIntent.DATA_QUERY,
            confidence=0.8,
            entities={},
            required_tools=[],
            context_categories=['api'],
            complexity='simple'
        )
        
        mcp_results = [{
            'success': True,
            'tool': 'list_records',
            'result': {'content': [{'text': 'Found 5 records'}]}
        }]
        
        response = await expert.generate_response("List tasks", analysis, [], mcp_results)
        
        assert 'success' in response
        assert 'answer' in response
        assert 'intent' in response
    
    @pytest.mark.asyncio
    async def test_error_suggestions(self, expert):
        """Test error suggestion generation"""
        suggestions = await expert.get_error_suggestions("Permission denied")
        
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)
        assert any("permission" in s.lower() for s in suggestions)


# Performance and Integration Tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling multiple concurrent queries"""
        agent = AirtableAIAgent()
        
        # Mock components for performance testing
        agent.context_manager = AsyncMock()
        agent.mcp_client = AsyncMock()
        agent.airtable_expert = AsyncMock()
        
        # Setup fast mock responses
        agent.airtable_expert.analyze_query.return_value = QueryAnalysis(
            intent=QueryIntent.DATA_QUERY,
            confidence=0.8,
            entities={},
            required_tools=[],
            context_categories=['api'],
            complexity='simple'
        )
        agent.airtable_expert.plan_operations.return_value = []
        agent.airtable_expert.generate_response.return_value = {
            'success': True,
            'answer': 'Test response'
        }
        agent.context_manager.get_relevant_context.return_value = []
        
        # Test concurrent processing
        queries = [f"Query {i}" for i in range(10)]
        start_time = datetime.now()
        
        responses = await agent.batch_process(queries)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Assertions
        assert len(responses) == 10
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert agent.metrics['requests_handled'] == 10
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage with large context"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create agent with large context
        agent = AirtableAIAgent()
        
        # Simulate processing with large context
        large_chunks = []
        for i in range(100):
            chunk = DocumentChunk(
                id=f"chunk_{i}",
                content="Large content " * 1000,  # 1000 words per chunk
                title=f"Chunk {i}",
                category="test",
                tokens=1000
            )
            large_chunks.append(chunk)
        
        # Mock context manager to return large chunks
        agent.context_manager = AsyncMock()
        agent.context_manager.get_relevant_context.return_value = large_chunks
        agent.mcp_client = AsyncMock()
        agent.airtable_expert = AsyncMock()
        
        # Process query
        await agent.process_query("Test query")
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory increase should be reasonable
        assert memory_increase < 500  # Less than 500MB increase


if __name__ == "__main__":
    pytest.main([__file__, "-v"])