#!/usr/bin/env python3
"""
📚 Context Manager for Airtable AI Agent
Intelligent context window management for optimal performance.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import tiktoken


@dataclass
class DocumentChunk:
    """Represents a chunk of documentation with metadata"""
    id: str
    content: str
    title: str
    category: str  # 'api', 'formulas', 'apps', 'mcp', etc.
    tokens: int
    embedding: Optional[List[float]] = None
    relevance_score: float = 0.0
    last_accessed: Optional[datetime] = None


class ContextManager:
    """
    Intelligent context management system for the Airtable AI Agent.
    
    Features:
    - Semantic search through documentation
    - Token-aware context optimization
    - Caching and performance optimization
    - Dynamic context adaptation based on query type
    """
    
    def __init__(self, max_tokens: int = 128000, cache_dir: str = ".cache"):
        self.max_tokens = max_tokens
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Claude tokenizer
        self.embedder = None  # Lazy load
        self.logger = logging.getLogger("context_manager")
        
        # Document storage
        self.chunks: List[DocumentChunk] = []
        self.chunk_index: Dict[str, DocumentChunk] = {}
        
        # Database for persistent storage
        self.db_path = self.cache_dir / "context.db"
        self._init_database()
        
        # Performance tracking
        self.stats = {
            'total_chunks': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'embeddings_computed': 0,
            'context_optimizations': 0
        }
    
    def _init_database(self) -> None:
        """Initialize SQLite database for chunk storage"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                embedding BLOB,
                relevance_score REAL DEFAULT 0.0,
                last_accessed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON chunks (category)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevance ON chunks (relevance_score DESC)
        """)
        conn.commit()
        conn.close()
    
    async def initialize(self) -> None:
        """Initialize the context manager with all documentation"""
        self.logger.info("🔄 Initializing context manager...")
        
        # Load embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.logger.info("✅ Embedding model loaded")
        
        # Load existing chunks from database
        await self._load_chunks_from_db()
        
        # Process documentation files if not in cache
        if not self.chunks:
            await self._process_documentation()
        
        self.logger.info(f"✅ Context manager initialized with {len(self.chunks)} chunks")
    
    async def _load_chunks_from_db(self) -> None:
        """Load chunks from persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, content, title, category, tokens, embedding, relevance_score, last_accessed
            FROM chunks
        """)
        
        for row in cursor.fetchall():
            embedding = pickle.loads(row[5]) if row[5] else None
            last_accessed = datetime.fromisoformat(row[7]) if row[7] else None
            
            chunk = DocumentChunk(
                id=row[0],
                content=row[1],
                title=row[2],
                category=row[3],
                tokens=row[4],
                embedding=embedding,
                relevance_score=row[6],
                last_accessed=last_accessed
            )
            
            self.chunks.append(chunk)
            self.chunk_index[chunk.id] = chunk
        
        conn.close()
        self.stats['total_chunks'] = len(self.chunks)
        
        if self.chunks:
            self.logger.info(f"📚 Loaded {len(self.chunks)} chunks from cache")
    
    async def _process_documentation(self) -> None:
        """Process all documentation files into chunks"""
        docs_dir = Path(__file__).parent.parent / "docs"
        
        # Documentation files to process
        doc_files = [
            ("airtable-web-api-complete.md", "api"),
            ("airtable-js-complete.md", "javascript"),
            ("mcp-integration-complete.md", "mcp"),
            ("airtable-formulas-complete.md", "formulas"),
            ("airtable-apps-extensions.md", "apps")
        ]
        
        for filename, category in doc_files:
            file_path = docs_dir / filename
            if file_path.exists():
                await self._process_file(file_path, category)
    
    async def _process_file(self, file_path: Path, category: str) -> None:
        """Process a single documentation file into chunks"""
        self.logger.info(f"📄 Processing {file_path.name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into logical chunks (sections, subsections)
        chunks = self._smart_chunking(content, file_path.stem)
        
        # Process each chunk
        for chunk_content, title in chunks:
            chunk_id = hashlib.sha256(
                (chunk_content + title + category).encode()
            ).hexdigest()[:16]
            
            tokens = len(self.tokenizer.encode(chunk_content))
            
            # Generate embedding
            embedding = self.embedder.encode(chunk_content).tolist()
            self.stats['embeddings_computed'] += 1
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_content,
                title=title,
                category=category,
                tokens=tokens,
                embedding=embedding
            )
            
            # Save to database
            await self._save_chunk(chunk)
            
            self.chunks.append(chunk)
            self.chunk_index[chunk_id] = chunk
        
        self.stats['total_chunks'] = len(self.chunks)
        self.logger.info(f"✅ Processed {file_path.name}: {len(chunks)} chunks")
    
    def _smart_chunking(self, content: str, title_prefix: str) -> List[Tuple[str, str]]:
        """Intelligently split content into meaningful chunks"""
        chunks = []
        
        # Split by major sections (##)
        sections = content.split('\n## ')
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Add back the ## if not the first section
            if i > 0:
                section = '## ' + section
            
            lines = section.split('\n')
            section_title = lines[0].replace('## ', '').replace('# ', '').strip()
            
            # For large sections, split further by subsections (###)
            if len(section) > 8000:  # ~2000 tokens
                subsections = section.split('\n### ')
                for j, subsection in enumerate(subsections):
                    if not subsection.strip():
                        continue
                    
                    if j > 0:
                        subsection = '### ' + subsection
                    
                    subsection_lines = subsection.split('\n')
                    subsection_title = subsection_lines[0].replace('### ', '').strip()
                    full_title = f"{title_prefix}: {section_title} - {subsection_title}"
                    
                    chunks.append((subsection, full_title))
            else:
                full_title = f"{title_prefix}: {section_title}"
                chunks.append((section, full_title))
        
        return chunks
    
    async def _save_chunk(self, chunk: DocumentChunk) -> None:
        """Save chunk to persistent storage"""
        conn = sqlite3.connect(self.db_path)
        
        embedding_blob = pickle.dumps(chunk.embedding) if chunk.embedding else None
        
        conn.execute("""
            INSERT OR REPLACE INTO chunks
            (id, content, title, category, tokens, embedding, relevance_score, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk.id,
            chunk.content,
            chunk.title,
            chunk.category,
            chunk.tokens,
            embedding_blob,
            chunk.relevance_score,
            chunk.last_accessed.isoformat() if chunk.last_accessed else None
        ))
        
        conn.commit()
        conn.close()
    
    async def get_relevant_context(
        self,
        query: str,
        analysis: Optional[Dict[str, Any]] = None,
        previous_context: Optional[Dict[str, Any]] = None,
        max_chunks: int = 10
    ) -> List[DocumentChunk]:
        """Get the most relevant context chunks for a query"""
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query)
        
        # Calculate relevance scores for all chunks
        relevant_chunks = []
        
        for chunk in self.chunks:
            if chunk.embedding is None:
                continue
            
            # Semantic similarity
            semantic_score = np.dot(query_embedding, chunk.embedding)
            
            # Category boost based on analysis
            category_boost = self._get_category_boost(chunk.category, analysis)
            
            # Recency boost for recently accessed chunks
            recency_boost = self._get_recency_boost(chunk)
            
            # Combined relevance score
            relevance_score = semantic_score + category_boost + recency_boost
            
            chunk.relevance_score = relevance_score
            chunk.last_accessed = datetime.now()
            
            relevant_chunks.append(chunk)
        
        # Sort by relevance and select top chunks
        relevant_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        selected_chunks = relevant_chunks[:max_chunks]
        
        # Optimize for token limit
        optimized_chunks = await self._optimize_for_tokens(selected_chunks)
        
        # Update access times in database
        await self._update_access_times(optimized_chunks)
        
        self.stats['context_optimizations'] += 1
        
        self.logger.debug(f"🎯 Selected {len(optimized_chunks)} context chunks for query")
        return optimized_chunks
    
    def _get_category_boost(self, category: str, analysis: Optional[Dict[str, Any]]) -> float:
        """Calculate category relevance boost based on query analysis"""
        if not analysis:
            return 0.0
        
        # Category priority mapping based on analysis
        category_priorities = {
            'api': 0.3,
            'javascript': 0.2,
            'mcp': 0.4,
            'formulas': 0.1,
            'apps': 0.1
        }
        
        # Adjust based on analysis
        intent = analysis.get('intent', '')
        if 'formula' in intent.lower():
            category_priorities['formulas'] = 0.4
        elif 'app' in intent.lower() or 'extension' in intent.lower():
            category_priorities['apps'] = 0.4
        elif 'mcp' in intent.lower() or 'tool' in intent.lower():
            category_priorities['mcp'] = 0.5
        
        return category_priorities.get(category, 0.0)
    
    def _get_recency_boost(self, chunk: DocumentChunk) -> float:
        """Calculate recency boost for recently accessed chunks"""
        if not chunk.last_accessed:
            return 0.0
        
        time_diff = datetime.now() - chunk.last_accessed
        if time_diff < timedelta(hours=1):
            return 0.2
        elif time_diff < timedelta(days=1):
            return 0.1
        else:
            return 0.0
    
    async def _optimize_for_tokens(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Optimize chunk selection to fit within token limits"""
        # Reserve tokens for response generation
        available_tokens = int(self.max_tokens * 0.7)  # 70% for context
        current_tokens = 0
        optimized_chunks = []
        
        for chunk in chunks:
            if current_tokens + chunk.tokens <= available_tokens:
                optimized_chunks.append(chunk)
                current_tokens += chunk.tokens
            else:
                # Try to fit partial chunk if beneficial
                remaining_tokens = available_tokens - current_tokens
                if remaining_tokens > 500:  # Minimum useful chunk size
                    # Create truncated chunk
                    truncated_content = self._truncate_content(
                        chunk.content, 
                        remaining_tokens
                    )
                    
                    truncated_chunk = DocumentChunk(
                        id=f"{chunk.id}_truncated",
                        content=truncated_content,
                        title=f"{chunk.title} (partial)",
                        category=chunk.category,
                        tokens=remaining_tokens,
                        relevance_score=chunk.relevance_score * 0.8  # Slight penalty
                    )
                    
                    optimized_chunks.append(truncated_chunk)
                break
        
        return optimized_chunks
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Intelligently truncate content to fit token limit"""
        tokens = self.tokenizer.encode(content)
        if len(tokens) <= max_tokens:
            return content
        
        # Truncate and decode
        truncated_tokens = tokens[:max_tokens]
        truncated_content = self.tokenizer.decode(truncated_tokens)
        
        # Try to end at a natural break point
        natural_breaks = ['\n\n', '\n### ', '\n## ', '. ', '.\n']
        for break_point in natural_breaks:
            if break_point in truncated_content:
                last_break = truncated_content.rfind(break_point)
                if last_break > len(truncated_content) * 0.8:  # Don't cut too much
                    truncated_content = truncated_content[:last_break + len(break_point)]
                    break
        
        return truncated_content + "\n\n[Content truncated...]"
    
    async def _update_access_times(self, chunks: List[DocumentChunk]) -> None:
        """Update last accessed times in database"""
        if not chunks:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for chunk in chunks:
            if chunk.last_accessed:
                conn.execute("""
                    UPDATE chunks 
                    SET last_accessed = ?, relevance_score = ?
                    WHERE id = ?
                """, (
                    chunk.last_accessed.isoformat(),
                    chunk.relevance_score,
                    chunk.id.replace('_truncated', '')  # Handle truncated chunks
                ))
        
        conn.commit()
        conn.close()
    
    async def search_chunks(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[DocumentChunk]:
        """Search for specific chunks by content"""
        query_embedding = self.embedder.encode(query)
        
        candidates = self.chunks
        if category:
            candidates = [c for c in self.chunks if c.category == category]
        
        scored_chunks = []
        for chunk in candidates:
            if chunk.embedding is None:
                continue
            
            score = np.dot(query_embedding, chunk.embedding)
            scored_chunks.append((score, chunk))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:limit]]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        categories = {}
        total_tokens = 0
        
        for chunk in self.chunks:
            categories[chunk.category] = categories.get(chunk.category, 0) + 1
            total_tokens += chunk.tokens
        
        return {
            'total_chunks': self.stats['total_chunks'],
            'total_tokens': total_tokens,
            'categories': categories,
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'embeddings_computed': self.stats['embeddings_computed'],
            'context_optimizations': self.stats['context_optimizations']
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on context manager"""
        try:
            # Test database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cursor.fetchone()[0]
            conn.close()
            
            # Test embedding model
            test_embedding = self.embedder.encode("test")
            
            return {
                'status': 'healthy',
                'chunks_in_db': chunk_count,
                'chunks_in_memory': len(self.chunks),
                'embedding_model_loaded': test_embedding is not None
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Save any pending changes
        if self.chunks:
            for chunk in self.chunks:
                if chunk.last_accessed:
                    await self._save_chunk(chunk)
        
        self.logger.info("🧹 Context manager cleanup complete")