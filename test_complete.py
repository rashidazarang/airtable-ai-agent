#!/usr/bin/env python3
"""
🧪 Complete Test Suite for Airtable AI Agent
Validates all components work correctly before deployment.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

# Test results
test_results: List[Dict[str, Any]] = []


def log_test_result(test_name: str, passed: bool, details: str = "", duration: float = 0.0):
    """Log a test result"""
    result = {
        'test': test_name,
        'passed': passed,
        'details': details,
        'duration': duration
    }
    test_results.append(result)
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name} ({duration:.2f}s)")
    if details and not passed:
        print(f"   Details: {details}")


async def test_imports():
    """Test all imports work correctly"""
    start_time = time.time()
    
    try:
        from src.context_manager_basic import ContextManagerBasic, DocumentChunk
        from src.mcp_client import MCPClient, MCPError
        from src.airtable_expert import AirtableExpert, QueryIntent
        from src.agent_basic import AirtableAIAgentBasic
        
        log_test_result("Import all modules", True, "All imports successful", time.time() - start_time)
        return True
        
    except ImportError as e:
        log_test_result("Import all modules", False, f"Import failed: {e}", time.time() - start_time)
        return False


async def test_context_manager():
    """Test context manager functionality"""
    start_time = time.time()
    
    try:
        from src.context_manager_basic import ContextManagerBasic
        
        # Create context manager
        cm = ContextManagerBasic(max_tokens=1000)
        
        # Test initialization
        await cm.initialize()
        
        # Check if chunks were loaded
        stats = await cm.get_stats()
        chunks_loaded = stats.get('total_chunks', 0)
        
        if chunks_loaded > 0:
            log_test_result("Context Manager", True, 
                          f"Loaded {chunks_loaded} documentation chunks", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("Context Manager", False, 
                          "No documentation chunks loaded", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("Context Manager", False, f"Error: {e}", time.time() - start_time)
        return False


async def test_mcp_client():
    """Test MCP client functionality"""
    start_time = time.time()
    
    try:
        from src.mcp_client import MCPClient
        
        # Create MCP client
        client = MCPClient("http://localhost:8010/mcp")
        
        # Test connection (will likely fail without server, but should handle gracefully)
        connection_result = await client.test_connection()
        
        # Test basic functionality
        tools = await client.list_available_tools()
        
        if isinstance(connection_result, dict) and isinstance(tools, list):
            log_test_result("MCP Client", True, 
                          f"Connection test completed, {len(tools)} tools available", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("MCP Client", False, 
                          "Unexpected response format", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("MCP Client", False, f"Error: {e}", time.time() - start_time)
        return False


async def test_airtable_expert():
    """Test Airtable expert functionality"""
    start_time = time.time()
    
    try:
        from src.airtable_expert import AirtableExpert
        
        # Create expert
        expert = AirtableExpert()
        await expert.initialize()
        
        # Test query analysis
        test_queries = [
            "List all records in the Tasks table",
            "Create a new project",
            "What fields are in the Users table?",
            "Delete completed tasks"
        ]
        
        successful_analyses = 0
        for query in test_queries:
            try:
                analysis = await expert.analyze_query(query)
                if hasattr(analysis, 'intent') and hasattr(analysis, 'confidence'):
                    successful_analyses += 1
            except Exception:
                pass
        
        if successful_analyses >= len(test_queries) // 2:
            log_test_result("Airtable Expert", True, 
                          f"Successfully analyzed {successful_analyses}/{len(test_queries)} queries", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("Airtable Expert", False, 
                          f"Only analyzed {successful_analyses}/{len(test_queries)} queries", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("Airtable Expert", False, f"Error: {e}", time.time() - start_time)
        return False


async def test_agent_initialization():
    """Test complete agent initialization"""
    start_time = time.time()
    
    try:
        from src.agent_basic import AirtableAIAgentBasic
        
        # Create and initialize agent
        agent = AirtableAIAgentBasic()
        await agent.initialize()
        
        # Test capabilities
        capabilities = await agent.get_capabilities()
        
        # Test health check
        health = await agent.health_check()
        
        # Clean shutdown
        await agent.shutdown()
        
        # Validate results
        if (capabilities.get('agent_info', {}).get('name') and 
            health.get('overall_status') in ['healthy', 'degraded']):
            
            log_test_result("Agent Initialization", True, 
                          f"Status: {health.get('overall_status')}", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("Agent Initialization", False, 
                          "Invalid capabilities or health check", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("Agent Initialization", False, f"Error: {e}", time.time() - start_time)
        return False


async def test_query_processing():
    """Test end-to-end query processing"""
    start_time = time.time()
    
    try:
        from src.agent_basic import AirtableAIAgentBasic
        
        # Create and initialize agent
        agent = AirtableAIAgentBasic()
        await agent.initialize()
        
        # Test different types of queries
        test_queries = [
            "Show me all tables",
            "What can you help me with?",
            "How do I create a record?"
        ]
        
        successful_queries = 0
        total_processing_time = 0
        
        for query in test_queries:
            try:
                response = await agent.process_query(query)
                processing_time = response.get('metadata', {}).get('processing_time', 0)
                total_processing_time += processing_time
                
                if response.get('answer') and processing_time > 0:
                    successful_queries += 1
            except Exception:
                pass
        
        await agent.shutdown()
        
        avg_processing_time = total_processing_time / max(successful_queries, 1)
        
        if successful_queries >= len(test_queries) // 2:
            log_test_result("Query Processing", True, 
                          f"Processed {successful_queries}/{len(test_queries)} queries, avg {avg_processing_time:.2f}s", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("Query Processing", False, 
                          f"Only processed {successful_queries}/{len(test_queries)} queries", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("Query Processing", False, f"Error: {e}", time.time() - start_time)
        return False


async def test_performance():
    """Test basic performance metrics"""
    start_time = time.time()
    
    try:
        from src.agent_basic import AirtableAIAgentBasic
        
        # Create agent
        agent = AirtableAIAgentBasic()
        await agent.initialize()
        
        # Test concurrent queries
        queries = ["What is Airtable?" for _ in range(3)]
        
        concurrent_start = time.time()
        responses = await asyncio.gather(
            *[agent.process_query(q) for q in queries],
            return_exceptions=True
        )
        concurrent_time = time.time() - concurrent_start
        
        await agent.shutdown()
        
        # Count successful responses
        successful = sum(1 for r in responses if isinstance(r, dict) and r.get('answer'))
        
        if successful >= 2 and concurrent_time < 10.0:  # Should complete within 10 seconds
            log_test_result("Performance Test", True, 
                          f"Processed {successful}/3 concurrent queries in {concurrent_time:.2f}s", 
                          time.time() - start_time)
            return True
        else:
            log_test_result("Performance Test", False, 
                          f"Only {successful}/3 queries succeeded, took {concurrent_time:.2f}s", 
                          time.time() - start_time)
            return False
            
    except Exception as e:
        log_test_result("Performance Test", False, f"Error: {e}", time.time() - start_time)
        return False


async def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Starting Comprehensive Test Suite for Airtable AI Agent")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_imports(),
        test_context_manager(),
        test_mcp_client(),
        test_airtable_expert(),
        test_agent_initialization(),
        test_query_processing(),
        test_performance()
    ]
    
    await asyncio.gather(*tests)
    
    # Report results
    print("\n" + "=" * 60)
    print("🔍 Test Results Summary")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results if result['passed'])
    total_tests = len(test_results)
    
    for result in test_results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['test']:<30} {result['duration']:.2f}s")
    
    print("-" * 60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    # Overall assessment
    success_rate = passed_tests / total_tests
    if success_rate >= 0.8:
        print("🎉 OVERALL STATUS: READY FOR DEPLOYMENT")
    elif success_rate >= 0.6:
        print("⚠️  OVERALL STATUS: NEEDS MINOR FIXES")
    else:
        print("❌ OVERALL STATUS: NEEDS MAJOR FIXES")
    
    return success_rate >= 0.8


if __name__ == "__main__":
    # Suppress some logging for cleaner output
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)