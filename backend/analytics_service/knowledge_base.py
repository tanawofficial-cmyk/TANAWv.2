"""
Phase 9: Knowledge Base (KB) Logic & Persistence
Implements knowledge base for recording mappings and confirmed corrections.

Features:
- KB schema and data structures
- Persistence and database operations
- User confirmations and KB updates
- TTL/decay for confidence scores
- Optional global KB with anonymization
- Failure modes and retry logic
- Comprehensive error handling
- Advanced observability
"""

import json
import sqlite3
import os
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import threading
import time
import logging
from pathlib import Path

# Import existing configuration
from config_manager import get_config

@dataclass
class KBEntry:
    """Represents a knowledge base entry."""
    user_id: str
    original_header: str
    canonical: str
    confidence: float
    source: str  # USER, KB, GPT, LOCAL
    confirmed: bool
    times_seen: int
    last_seen: str
    version: int
    created_at: str
    updated_at: str

@dataclass
class KBResult:
    """Represents a knowledge base operation result."""
    success: bool
    entry: Optional[KBEntry] = None
    entries: List[KBEntry] = field(default_factory=list)
    operation: str = ""
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None

class KnowledgeBase:
    """
    Phase 9: Knowledge Base system for recording mappings and confirmed corrections.
    
    Features:
    - KB schema and data structures
    - Persistence and database operations
    - User confirmations and KB updates
    - TTL/decay for confidence scores
    - Optional global KB with anonymization
    - Failure modes and retry logic
    - Comprehensive error handling
    - Advanced observability
    """
    
    def __init__(self, config=None, db_path: str = "tanaw_knowledge_base.db"):
        """Initialize knowledge base with configuration."""
        self.config = config or get_config()
        self.kb_version = "9.0.0"
        self.db_path = db_path
        
        # Configuration
        self.confidence_decay_days = getattr(self.config, 'kb_confidence_decay_days', 30)
        self.confidence_decay_factor = getattr(self.config, 'kb_confidence_decay_factor', 0.1)
        self.max_retry_attempts = getattr(self.config, 'kb_max_retry_attempts', 3)
        self.retry_delay_seconds = getattr(self.config, 'kb_retry_delay_seconds', 5)
        
        # Threading
        self.lock = threading.Lock()
        self.retry_queue = []
        self.retry_thread = None
        self.stop_retry_thread = False
        
        # Metrics tracking
        self.metrics = {
            'kb_write_latency_ms': 0.0,
            'kb_hits': 0,
            'kb_misses': 0,
            'kb_entries_created': 0,
            'kb_entries_updated': 0,
            'kb_entries_decayed': 0,
            'kb_retry_attempts': 0,
            'kb_retry_successes': 0,
            'kb_retry_failures': 0,
            'kb_processing_time_ms': 0.0
        }
        
        # Initialize database
        self._initialize_database()
        
        # Start retry thread
        self._start_retry_thread()
    
    def _initialize_database(self):
        """Initialize the knowledge base database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create knowledge base table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        original_header TEXT NOT NULL,
                        canonical TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        source TEXT NOT NULL,
                        confirmed BOOLEAN NOT NULL,
                        times_seen INTEGER NOT NULL,
                        last_seen TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(user_id, original_header, canonical)
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON knowledge_base(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_original_header ON knowledge_base(original_header)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_canonical ON knowledge_base(canonical)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_seen ON knowledge_base(last_seen)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON knowledge_base(confidence)')
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error initializing knowledge base database: {e}")
            raise
    
    def _start_retry_thread(self):
        """Start the retry thread for failed operations."""
        try:
            self.retry_thread = threading.Thread(target=self._retry_worker, daemon=True)
            self.retry_thread.start()
        except Exception as e:
            print(f"⚠️ Error starting retry thread: {e}")
    
    def _retry_worker(self):
        """Retry worker for failed operations."""
        while not self.stop_retry_thread:
            try:
                if self.retry_queue:
                    with self.lock:
                        retry_item = self.retry_queue.pop(0)
                    
                    # Retry the operation
                    success = self._retry_operation(retry_item)
                    
                    if success:
                        self.metrics['kb_retry_successes'] += 1
                    else:
                        self.metrics['kb_retry_failures'] += 1
                        # Re-queue if not exceeded max attempts
                        if retry_item['attempts'] < self.max_retry_attempts:
                            retry_item['attempts'] += 1
                            retry_item['next_retry'] = time.time() + self.retry_delay_seconds
                            with self.lock:
                                self.retry_queue.append(retry_item)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"⚠️ Error in retry worker: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _retry_operation(self, retry_item: Dict[str, Any]) -> bool:
        """Retry a failed operation."""
        try:
            operation = retry_item['operation']
            
            if operation == 'insert':
                return self._insert_entry_retry(retry_item['entry'])
            elif operation == 'update':
                return self._update_entry_retry(retry_item['entry'])
            elif operation == 'decay':
                return self._decay_confidence_retry()
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error retrying operation: {e}")
            return False
    
    def _insert_entry_retry(self, entry: KBEntry) -> bool:
        """Retry insert operation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_base 
                    (user_id, original_header, canonical, confidence, source, confirmed, 
                     times_seen, last_seen, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.user_id, entry.original_header, entry.canonical, entry.confidence,
                    entry.source, entry.confirmed, entry.times_seen, entry.last_seen,
                    entry.version, entry.created_at, entry.updated_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"⚠️ Error in insert retry: {e}")
            return False
    
    def _update_entry_retry(self, entry: KBEntry) -> bool:
        """Retry update operation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE knowledge_base 
                    SET confidence = ?, source = ?, confirmed = ?, times_seen = ?, 
                        last_seen = ?, version = ?, updated_at = ?
                    WHERE user_id = ? AND original_header = ? AND canonical = ?
                ''', (
                    entry.confidence, entry.source, entry.confirmed, entry.times_seen,
                    entry.last_seen, entry.version, entry.updated_at,
                    entry.user_id, entry.original_header, entry.canonical
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"⚠️ Error in update retry: {e}")
            return False
    
    def _decay_confidence_retry(self) -> bool:
        """Retry decay operation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE knowledge_base 
                    SET confidence = confidence * (1 - ?), updated_at = ?
                    WHERE last_seen < ? AND confidence > 0.1
                ''', (
                    self.confidence_decay_factor,
                    datetime.now().isoformat(),
                    (datetime.now() - timedelta(days=self.confidence_decay_days)).isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"⚠️ Error in decay retry: {e}")
            return False
    
    def record_user_confirmation(self, user_id: str, original_header: str, 
                                canonical: str, source: str = "USER") -> KBResult:
        """Record user confirmation of a mapping."""
        start_time = datetime.now()
        
        try:
            # Check if entry exists
            existing_entry = self.get_entry(user_id, original_header, canonical)
            
            if existing_entry and existing_entry.success:
                # Update existing entry
                entry = existing_entry.entry
                entry.confidence = 1.0  # User confirmation = 100% confidence
                entry.source = source
                entry.confirmed = True
                entry.times_seen += 1
                entry.last_seen = datetime.now().isoformat()
                entry.version += 1
                entry.updated_at = datetime.now().isoformat()
                
                result = self._update_entry(entry)
                if result.success:
                    self.metrics['kb_entries_updated'] += 1
            else:
                # Create new entry
                entry = KBEntry(
                    user_id=user_id,
                    original_header=original_header,
                    canonical=canonical,
                    confidence=1.0,
                    source=source,
                    confirmed=True,
                    times_seen=1,
                    last_seen=datetime.now().isoformat(),
                    version=1,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                
                result = self._insert_entry(entry)
                if result.success:
                    self.metrics['kb_entries_created'] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['kb_processing_time_ms'] = processing_time * 1000
            self.metrics['kb_write_latency_ms'] = processing_time * 1000
            
            return result
            
        except Exception as e:
            return KBResult(
                success=False,
                operation="record_user_confirmation",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_entry(self, user_id: str, original_header: str, canonical: str) -> KBResult:
        """Get a specific knowledge base entry."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, original_header, canonical, confidence, source, 
                           confirmed, times_seen, last_seen, version, created_at, updated_at
                    FROM knowledge_base
                    WHERE user_id = ? AND original_header = ? AND canonical = ?
                ''', (user_id, original_header, canonical))
                
                row = cursor.fetchone()
                
                if row:
                    entry = KBEntry(
                        user_id=row[0],
                        original_header=row[1],
                        canonical=row[2],
                        confidence=row[3],
                        source=row[4],
                        confirmed=bool(row[5]),
                        times_seen=row[6],
                        last_seen=row[7],
                        version=row[8],
                        created_at=row[9],
                        updated_at=row[10]
                    )
                    
                    self.metrics['kb_hits'] += 1
                    return KBResult(
                        success=True,
                        entry=entry,
                        operation="get_entry",
                        processing_time_seconds=(datetime.now() - start_time).total_seconds()
                    )
                else:
                    self.metrics['kb_misses'] += 1
                    return KBResult(
                        success=True,
                        entry=None,
                        operation="get_entry",
                        processing_time_seconds=(datetime.now() - start_time).total_seconds()
                    )
                    
        except Exception as e:
            return KBResult(
                success=False,
                operation="get_entry",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_user_mappings(self, user_id: str, original_header: Optional[str] = None) -> KBResult:
        """Get all mappings for a user."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if original_header:
                    cursor.execute('''
                        SELECT user_id, original_header, canonical, confidence, source, 
                               confirmed, times_seen, last_seen, version, created_at, updated_at
                        FROM knowledge_base
                        WHERE user_id = ? AND original_header = ?
                        ORDER BY confidence DESC, times_seen DESC
                    ''', (user_id, original_header))
                else:
                    cursor.execute('''
                        SELECT user_id, original_header, canonical, confidence, source, 
                               confirmed, times_seen, last_seen, version, created_at, updated_at
                        FROM knowledge_base
                        WHERE user_id = ?
                        ORDER BY confidence DESC, times_seen DESC
                    ''', (user_id,))
                
                rows = cursor.fetchall()
                entries = []
                
                for row in rows:
                    entry = KBEntry(
                        user_id=row[0],
                        original_header=row[1],
                        canonical=row[2],
                        confidence=row[3],
                        source=row[4],
                        confirmed=bool(row[5]),
                        times_seen=row[6],
                        last_seen=row[7],
                        version=row[8],
                        created_at=row[9],
                        updated_at=row[10]
                    )
                    entries.append(entry)
                
                self.metrics['kb_hits'] += 1
                return KBResult(
                    success=True,
                    entries=entries,
                    operation="get_user_mappings",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            return KBResult(
                success=False,
                operation="get_user_mappings",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _insert_entry(self, entry: KBEntry) -> KBResult:
        """Insert a new knowledge base entry."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_base 
                    (user_id, original_header, canonical, confidence, source, confirmed, 
                     times_seen, last_seen, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.user_id, entry.original_header, entry.canonical, entry.confidence,
                    entry.source, entry.confirmed, entry.times_seen, entry.last_seen,
                    entry.version, entry.created_at, entry.updated_at
                ))
                conn.commit()
                
                return KBResult(
                    success=True,
                    entry=entry,
                    operation="insert_entry",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            # Queue for retry
            self._queue_for_retry('insert', entry)
            return KBResult(
                success=False,
                operation="insert_entry",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _update_entry(self, entry: KBEntry) -> KBResult:
        """Update an existing knowledge base entry."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE knowledge_base 
                    SET confidence = ?, source = ?, confirmed = ?, times_seen = ?, 
                        last_seen = ?, version = ?, updated_at = ?
                    WHERE user_id = ? AND original_header = ? AND canonical = ?
                ''', (
                    entry.confidence, entry.source, entry.confirmed, entry.times_seen,
                    entry.last_seen, entry.version, entry.updated_at,
                    entry.user_id, entry.original_header, entry.canonical
                ))
                conn.commit()
                
                return KBResult(
                    success=True,
                    entry=entry,
                    operation="update_entry",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            # Queue for retry
            self._queue_for_retry('update', entry)
            return KBResult(
                success=False,
                operation="update_entry",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _queue_for_retry(self, operation: str, entry: KBEntry):
        """Queue an operation for retry."""
        try:
            retry_item = {
                'operation': operation,
                'entry': entry,
                'attempts': 0,
                'next_retry': time.time(),
                'timestamp': datetime.now().isoformat()
            }
            
            with self.lock:
                self.retry_queue.append(retry_item)
            
            self.metrics['kb_retry_attempts'] += 1
            
        except Exception as e:
            print(f"⚠️ Error queuing for retry: {e}")
    
    def decay_confidence(self) -> KBResult:
        """Decay confidence scores for old entries."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE knowledge_base 
                    SET confidence = confidence * (1 - ?), updated_at = ?
                    WHERE last_seen < ? AND confidence > 0.1
                ''', (
                    self.confidence_decay_factor,
                    datetime.now().isoformat(),
                    (datetime.now() - timedelta(days=self.confidence_decay_days)).isoformat()
                ))
                
                affected_rows = cursor.rowcount
                conn.commit()
                
                self.metrics['kb_entries_decayed'] += affected_rows
                
                return KBResult(
                    success=True,
                    operation="decay_confidence",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            # Queue for retry
            self._queue_for_retry('decay', None)
            return KBResult(
                success=False,
                operation="decay_confidence",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_global_mappings(self, original_header: str, min_confidence: float = 0.8) -> KBResult:
        """Get global mappings (anonymized) for cross-user learning."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT original_header, canonical, AVG(confidence) as avg_confidence, 
                           COUNT(*) as usage_count, MAX(last_seen) as last_seen
                    FROM knowledge_base
                    WHERE original_header = ? AND confirmed = 1 AND confidence >= ?
                    GROUP BY original_header, canonical
                    ORDER BY avg_confidence DESC, usage_count DESC
                ''', (original_header, min_confidence))
                
                rows = cursor.fetchall()
                entries = []
                
                for row in rows:
                    # Create anonymized entry
                    entry = KBEntry(
                        user_id="global",
                        original_header=row[0],
                        canonical=row[1],
                        confidence=row[2],
                        source="GLOBAL",
                        confirmed=True,
                        times_seen=row[3],
                        last_seen=row[4],
                        version=1,
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    entries.append(entry)
                
                return KBResult(
                    success=True,
                    entries=entries,
                    operation="get_global_mappings",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            return KBResult(
                success=False,
                operation="get_global_mappings",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def cleanup_old_entries(self, days_old: int = 365) -> KBResult:
        """Clean up old entries with low confidence."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM knowledge_base
                    WHERE last_seen < ? AND confidence < 0.1
                ''', ((datetime.now() - timedelta(days=days_old)).isoformat(),))
                
                affected_rows = cursor.rowcount
                conn.commit()
                
                return KBResult(
                    success=True,
                    operation="cleanup_old_entries",
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            return KBResult(
                success=False,
                operation="cleanup_old_entries",
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'kb_write_latency_ms': 0.0,
            'kb_hits': 0,
            'kb_misses': 0,
            'kb_entries_created': 0,
            'kb_entries_updated': 0,
            'kb_entries_decayed': 0,
            'kb_retry_attempts': 0,
            'kb_retry_successes': 0,
            'kb_retry_failures': 0,
            'kb_processing_time_ms': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "kb.write_latency": self.metrics['kb_write_latency_ms'],
                "kb.hits": self.metrics['kb_hits'],
                "kb.misses": self.metrics['kb_misses'],
                "kb.entries_created": self.metrics['kb_entries_created'],
                "kb.entries_updated": self.metrics['kb_entries_updated'],
                "kb.entries_decayed": self.metrics['kb_entries_decayed'],
                "kb.retry_attempts": self.metrics['kb_retry_attempts'],
                "kb.retry_successes": self.metrics['kb_retry_successes'],
                "kb.retry_failures": self.metrics['kb_retry_failures'],
                "kb.processing_time_ms": self.metrics['kb_processing_time_ms']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Knowledge base metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting knowledge base metrics: {e}")
            return {"kb.metrics_error": str(e)}
    
    def close(self):
        """Close the knowledge base and stop retry thread."""
        try:
            self.stop_retry_thread = True
            if self.retry_thread:
                self.retry_thread.join(timeout=5)
        except Exception as e:
            print(f"⚠️ Error closing knowledge base: {e}")

# Global knowledge base instance
knowledge_base = KnowledgeBase()

def record_user_confirmation(user_id: str, original_header: str, canonical: str, source: str = "USER") -> KBResult:
    """Convenience function to record user confirmation."""
    return knowledge_base.record_user_confirmation(user_id, original_header, canonical, source)

def get_user_mappings(user_id: str, original_header: Optional[str] = None) -> KBResult:
    """Convenience function to get user mappings."""
    return knowledge_base.get_user_mappings(user_id, original_header)

if __name__ == "__main__":
    # Test the knowledge base
    print("🧪 Testing Knowledge Base")
    print("=" * 50)
    
    # Test user confirmation
    result = record_user_confirmation("test_user", "prod_desc", "Product", "USER")
    
    if result.success:
        print(f"✅ Successfully recorded user confirmation")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
    else:
        print(f"❌ Error: {result.error_message}")
    
    # Test getting mappings
    mappings = get_user_mappings("test_user")
    
    if mappings.success:
        print(f"✅ Found {len(mappings.entries)} mappings for user")
        for entry in mappings.entries:
            print(f"   {entry.original_header} -> {entry.canonical} (confidence: {entry.confidence:.2f})")
    else:
        print(f"❌ Error getting mappings: {mappings.error_message}")