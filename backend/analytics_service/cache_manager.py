"""
Phase 10: Caching & Async Jobs
Implements caching system and background job processing for fast subsequent loads.

Features:
- Cache analytics outputs by analysis_id
- Background queue for heavy tasks
- Cache invalidation with TTL
- Failure modes and error handling
- Comprehensive error handling
- Advanced observability
"""

import json
import sqlite3
import os
import hashlib
import time
import threading
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pickle
import base64
from pathlib import Path
import uuid

# Import existing configuration
from config_manager import get_config

@dataclass
class CacheEntry:
    """Represents a cache entry."""
    analysis_id: str
    cache_key: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    expires_at: str
    access_count: int
    last_accessed: str
    size_bytes: int

@dataclass
class BackgroundJob:
    """Represents a background job."""
    job_id: str
    job_type: str  # 'full_file_rerun', 'kb_reconciliation', 'gpt_reevaluation'
    analysis_id: str
    parameters: Dict[str, Any]
    priority: int  # 1=high, 2=medium, 3=low
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    retry_count: int
    max_retries: int

@dataclass
class CacheResult:
    """Represents a cache operation result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    cache_hit: bool = False
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None

@dataclass
class JobResult:
    """Represents a background job result."""
    success: bool
    job_id: str
    result_data: Optional[Dict[str, Any]] = None
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None

class CacheManager:
    """
    Phase 10: Cache manager for analytics outputs and background job processing.
    
    Features:
    - Cache analytics outputs by analysis_id
    - Background queue for heavy tasks
    - Cache invalidation with TTL
    - Failure modes and error handling
    - Comprehensive error handling
    - Advanced observability
    """
    
    def __init__(self, config=None, cache_db_path: str = "tanaw_cache.db"):
        """Initialize cache manager with configuration."""
        self.config = config or get_config()
        self.cache_manager_version = "10.0.0"
        self.cache_db_path = cache_db_path
        
        # Configuration
        self.cache_ttl_hours = getattr(self.config, 'cache_ttl_hours', 24)
        self.max_cache_size_mb = getattr(self.config, 'max_cache_size_mb', 100)
        self.max_cache_entries = getattr(self.config, 'max_cache_entries', 1000)
        self.background_workers = getattr(self.config, 'background_workers', 2)
        self.job_timeout_seconds = getattr(self.config, 'job_timeout_seconds', 300)
        
        # Threading
        self.lock = threading.Lock()
        self.job_queue = []
        self.workers = []
        self.stop_workers = False
        
        # Metrics tracking
        self.metrics = {
            'cache_hit_rate': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_evictions': 0,
            'queue_length': 0,
            'worker_errors': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'cache_size_bytes': 0,
            'processing_time_ms': 0.0
        }
        
        # Initialize cache database
        self._initialize_cache_database()
        
        # Start background workers
        self._start_background_workers()
    
    def _initialize_cache_database(self):
        """Initialize the cache database."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Create cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        analysis_id TEXT NOT NULL,
                        cache_key TEXT NOT NULL,
                        data TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        access_count INTEGER NOT NULL,
                        last_accessed TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        PRIMARY KEY (analysis_id, cache_key)
                    )
                ''')
                
                # Create background jobs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS background_jobs (
                        job_id TEXT PRIMARY KEY,
                        job_type TEXT NOT NULL,
                        analysis_id TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        completed_at TEXT,
                        error_message TEXT,
                        retry_count INTEGER NOT NULL,
                        max_retries INTEGER NOT NULL
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_id ON cache_entries(analysis_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_status ON background_jobs(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_priority ON background_jobs(priority)')
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error initializing cache database: {e}")
            raise
    
    def _start_background_workers(self):
        """Start background workers for job processing."""
        try:
            for i in range(self.background_workers):
                worker = threading.Thread(target=self._worker_loop, daemon=True, name=f"Worker-{i}")
                worker.start()
                self.workers.append(worker)
        except Exception as e:
            print(f"⚠️ Error starting background workers: {e}")
    
    def _worker_loop(self):
        """Background worker loop for processing jobs."""
        while not self.stop_workers:
            try:
                job = None
                with self.lock:
                    if self.job_queue:
                        # Get highest priority job
                        self.job_queue.sort(key=lambda x: x.priority)
                        job = self.job_queue.pop(0)
                        self.metrics['queue_length'] = len(self.job_queue)
                
                if job:
                    self._process_job(job)
                else:
                    time.sleep(1)  # Wait for jobs
                    
            except Exception as e:
                print(f"⚠️ Error in worker loop: {e}")
                self.metrics['worker_errors'] += 1
                time.sleep(5)  # Wait longer on error
    
    def _process_job(self, job: BackgroundJob):
        """Process a background job."""
        try:
            # Update job status
            job.status = 'processing'
            job.started_at = datetime.now().isoformat()
            self._update_job_status(job)
            
            # Process based on job type
            if job.job_type == 'full_file_rerun':
                result = self._process_full_file_rerun(job)
            elif job.job_type == 'kb_reconciliation':
                result = self._process_kb_reconciliation(job)
            elif job.job_type == 'gpt_reevaluation':
                result = self._process_gpt_reevaluation(job)
            else:
                raise Exception(f"Unknown job type: {job.job_type}")
            
            # Update job status
            if result.success:
                job.status = 'completed'
                job.completed_at = datetime.now().isoformat()
                self.metrics['jobs_completed'] += 1
            else:
                job.status = 'failed'
                job.error_message = result.error_message
                job.retry_count += 1
                self.metrics['jobs_failed'] += 1
                
                # Retry if not exceeded max retries
                if job.retry_count < job.max_retries:
                    job.status = 'pending'
                    job.started_at = None
                    with self.lock:
                        self.job_queue.append(job)
                        self.metrics['queue_length'] = len(self.job_queue)
            
            self._update_job_status(job)
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.now().isoformat()
            self.metrics['jobs_failed'] += 1
            self.metrics['worker_errors'] += 1
            self._update_job_status(job)
    
    def _process_full_file_rerun(self, job: BackgroundJob) -> JobResult:
        """Process full file rerun job."""
        start_time = datetime.now()
        
        try:
            # This would trigger a full re-run of the analysis
            # For now, return a placeholder result
            result_data = {
                'job_type': 'full_file_rerun',
                'analysis_id': job.analysis_id,
                'status': 'completed'
            }
            
            return JobResult(
                success=True,
                job_id=job.job_id,
                result_data=result_data,
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=job.job_id,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _process_kb_reconciliation(self, job: BackgroundJob) -> JobResult:
        """Process KB reconciliation job."""
        start_time = datetime.now()
        
        try:
            # This would reconcile the knowledge base
            # For now, return a placeholder result
            result_data = {
                'job_type': 'kb_reconciliation',
                'analysis_id': job.analysis_id,
                'status': 'completed'
            }
            
            return JobResult(
                success=True,
                job_id=job.job_id,
                result_data=result_data,
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=job.job_id,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _process_gpt_reevaluation(self, job: BackgroundJob) -> JobResult:
        """Process GPT re-evaluation job."""
        start_time = datetime.now()
        
        try:
            # This would re-evaluate low-confidence mappings with GPT
            # For now, return a placeholder result
            result_data = {
                'job_type': 'gpt_reevaluation',
                'analysis_id': job.analysis_id,
                'status': 'completed'
            }
            
            return JobResult(
                success=True,
                job_id=job.job_id,
                result_data=result_data,
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=job.job_id,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def cache_analytics_output(self, analysis_id: str, data: Dict[str, Any], 
                             metadata: Dict[str, Any]) -> CacheResult:
        """Cache analytics output by analysis_id."""
        start_time = datetime.now()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(analysis_id, data)
            
            # Check if cache is full
            if self._is_cache_full():
                self._evict_lru_entries()
            
            # Create cache entry
            cache_entry = CacheEntry(
                analysis_id=analysis_id,
                cache_key=cache_key,
                data=data,
                metadata=metadata,
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(hours=self.cache_ttl_hours)).isoformat(),
                access_count=0,
                last_accessed=datetime.now().isoformat(),
                size_bytes=self._calculate_size(data)
            )
            
            # Store in database
            self._store_cache_entry(cache_entry)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            
            return CacheResult(
                success=True,
                data=data,
                cache_hit=False,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            return CacheResult(
                success=False,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_cached_analytics(self, analysis_id: str, cache_key: Optional[str] = None) -> CacheResult:
        """Get cached analytics output."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                if cache_key:
                    cursor.execute('''
                        SELECT data, metadata, access_count, last_accessed, expires_at
                        FROM cache_entries
                        WHERE analysis_id = ? AND cache_key = ?
                    ''', (analysis_id, cache_key))
                else:
                    cursor.execute('''
                        SELECT data, metadata, access_count, last_accessed, expires_at
                        FROM cache_entries
                        WHERE analysis_id = ?
                        ORDER BY last_accessed DESC
                        LIMIT 1
                    ''', (analysis_id,))
                
                row = cursor.fetchone()
                
                if row:
                    # Check if expired
                    expires_at = datetime.fromisoformat(row[4])
                    if datetime.now() > expires_at:
                        # Remove expired entry
                        self._remove_cache_entry(analysis_id, cache_key)
                        self.metrics['cache_misses'] += 1
                        return CacheResult(
                            success=True,
                            cache_hit=False,
                            processing_time_seconds=(datetime.now() - start_time).total_seconds()
                        )
                    
                    # Update access count and last accessed
                    access_count = row[2] + 1
                    last_accessed = datetime.now().isoformat()
                    
                    cursor.execute('''
                        UPDATE cache_entries
                        SET access_count = ?, last_accessed = ?
                        WHERE analysis_id = ? AND cache_key = ?
                    ''', (access_count, last_accessed, analysis_id, cache_key or ''))
                    conn.commit()
                    
                    # Parse data
                    data = json.loads(row[0])
                    metadata = json.loads(row[1])
                    
                    self.metrics['cache_hits'] += 1
                    self._update_cache_hit_rate()
                    
                    return CacheResult(
                        success=True,
                        data=data,
                        cache_hit=True,
                        processing_time_seconds=(datetime.now() - start_time).total_seconds()
                    )
                else:
                    self.metrics['cache_misses'] += 1
                    self._update_cache_hit_rate()
                    
                    return CacheResult(
                        success=True,
                        cache_hit=False,
                        processing_time_seconds=(datetime.now() - start_time).total_seconds()
                    )
                    
        except Exception as e:
            return CacheResult(
                success=False,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def invalidate_cache(self, analysis_id: str, cache_key: Optional[str] = None) -> CacheResult:
        """Invalidate cache entries."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                if cache_key:
                    cursor.execute('''
                        DELETE FROM cache_entries
                        WHERE analysis_id = ? AND cache_key = ?
                    ''', (analysis_id, cache_key))
                else:
                    cursor.execute('''
                        DELETE FROM cache_entries
                        WHERE analysis_id = ?
                    ''', (analysis_id,))
                
                conn.commit()
                
                return CacheResult(
                    success=True,
                    processing_time_seconds=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            return CacheResult(
                success=False,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def queue_background_job(self, job_type: str, analysis_id: str, 
                           parameters: Dict[str, Any], priority: int = 2) -> JobResult:
        """Queue a background job."""
        start_time = datetime.now()
        
        try:
            job_id = str(uuid.uuid4())
            job = BackgroundJob(
                job_id=job_id,
                job_type=job_type,
                analysis_id=analysis_id,
                parameters=parameters,
                priority=priority,
                status='pending',
                created_at=datetime.now().isoformat(),
                started_at=None,
                completed_at=None,
                error_message=None,
                retry_count=0,
                max_retries=3
            )
            
            # Add to queue
            with self.lock:
                self.job_queue.append(job)
                self.metrics['queue_length'] = len(self.job_queue)
            
            # Store in database
            self._store_job(job)
            
            return JobResult(
                success=True,
                job_id=job_id,
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def get_job_status(self, job_id: str) -> JobResult:
        """Get job status."""
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT status, error_message, completed_at
                    FROM background_jobs
                    WHERE job_id = ?
                ''', (job_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return JobResult(
                        success=True,
                        job_id=job_id,
                        result_data={
                            'status': row[0],
                            'error_message': row[1],
                            'completed_at': row[2]
                        },
                        processing_time_seconds=(datetime.now() - start_time).total_seconds()
                    )
                else:
                    return JobResult(
                        success=False,
                        job_id=job_id,
                        processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                        error_message="Job not found"
                    )
                    
        except Exception as e:
            return JobResult(
                success=False,
                job_id=job_id,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _generate_cache_key(self, analysis_id: str, data: Dict[str, Any]) -> str:
        """Generate cache key for data."""
        try:
            # Create hash of data for cache key
            data_str = json.dumps(data, sort_keys=True)
            hash_obj = hashlib.md5(data_str.encode())
            return hash_obj.hexdigest()
        except Exception as e:
            return str(uuid.uuid4())
    
    def _calculate_size(self, data: Dict[str, Any]) -> int:
        """Calculate size of data in bytes."""
        try:
            data_str = json.dumps(data)
            return len(data_str.encode('utf-8'))
        except Exception:
            return 0
    
    def _is_cache_full(self) -> bool:
        """Check if cache is full."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Check entry count
                cursor.execute('SELECT COUNT(*) FROM cache_entries')
                entry_count = cursor.fetchone()[0]
                
                if entry_count >= self.max_cache_entries:
                    return True
                
                # Check size
                cursor.execute('SELECT SUM(size_bytes) FROM cache_entries')
                total_size = cursor.fetchone()[0] or 0
                
                if total_size >= self.max_cache_size_mb * 1024 * 1024:
                    return True
                
                return False
                
        except Exception:
            return True
    
    def _evict_lru_entries(self):
        """Evict least recently used entries."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Get LRU entries to evict
                cursor.execute('''
                    SELECT analysis_id, cache_key
                    FROM cache_entries
                    ORDER BY last_accessed ASC
                    LIMIT 10
                ''')
                
                entries_to_evict = cursor.fetchall()
                
                for analysis_id, cache_key in entries_to_evict:
                    cursor.execute('''
                        DELETE FROM cache_entries
                        WHERE analysis_id = ? AND cache_key = ?
                    ''', (analysis_id, cache_key))
                    self.metrics['cache_evictions'] += 1
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error evicting LRU entries: {e}")
    
    def _store_cache_entry(self, entry: CacheEntry):
        """Store cache entry in database."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_entries
                    (analysis_id, cache_key, data, metadata, created_at, expires_at,
                     access_count, last_accessed, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.analysis_id, entry.cache_key, json.dumps(entry.data),
                    json.dumps(entry.metadata), entry.created_at, entry.expires_at,
                    entry.access_count, entry.last_accessed, entry.size_bytes
                ))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error storing cache entry: {e}")
    
    def _remove_cache_entry(self, analysis_id: str, cache_key: str):
        """Remove cache entry from database."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM cache_entries
                    WHERE analysis_id = ? AND cache_key = ?
                ''', (analysis_id, cache_key))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error removing cache entry: {e}")
    
    def _store_job(self, job: BackgroundJob):
        """Store job in database."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO background_jobs
                    (job_id, job_type, analysis_id, parameters, priority, status,
                     created_at, started_at, completed_at, error_message, retry_count, max_retries)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.job_id, job.job_type, job.analysis_id, json.dumps(job.parameters),
                    job.priority, job.status, job.created_at, job.started_at,
                    job.completed_at, job.error_message, job.retry_count, job.max_retries
                ))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error storing job: {e}")
    
    def _update_job_status(self, job: BackgroundJob):
        """Update job status in database."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE background_jobs
                    SET status = ?, started_at = ?, completed_at = ?, error_message = ?, retry_count = ?
                    WHERE job_id = ?
                ''', (
                    job.status, job.started_at, job.completed_at, job.error_message,
                    job.retry_count, job.job_id
                ))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Error updating job status: {e}")
    
    def _update_cache_hit_rate(self):
        """Update cache hit rate metric."""
        try:
            total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
            if total_requests > 0:
                self.metrics['cache_hit_rate'] = (self.metrics['cache_hits'] / total_requests) * 100
        except Exception:
            pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'cache_hit_rate': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_evictions': 0,
            'queue_length': 0,
            'worker_errors': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'cache_size_bytes': 0,
            'processing_time_ms': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "cache.hit_rate": self.metrics['cache_hit_rate'],
                "cache.hits": self.metrics['cache_hits'],
                "cache.misses": self.metrics['cache_misses'],
                "cache.evictions": self.metrics['cache_evictions'],
                "queue.length": self.metrics['queue_length'],
                "worker.errors": self.metrics['worker_errors'],
                "jobs.completed": self.metrics['jobs_completed'],
                "jobs.failed": self.metrics['jobs_failed'],
                "cache.size_bytes": self.metrics['cache_size_bytes'],
                "cache.processing_time_ms": self.metrics['processing_time_ms']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Cache manager metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting cache manager metrics: {e}")
            return {"cache.metrics_error": str(e)}
    
    def close(self):
        """Close cache manager and stop workers."""
        try:
            self.stop_workers = True
            for worker in self.workers:
                worker.join(timeout=5)
        except Exception as e:
            print(f"⚠️ Error closing cache manager: {e}")

# Global cache manager instance
cache_manager = CacheManager()

def cache_analytics_output(analysis_id: str, data: Dict[str, Any], metadata: Dict[str, Any]) -> CacheResult:
    """Convenience function to cache analytics output."""
    return cache_manager.cache_analytics_output(analysis_id, data, metadata)

def get_cached_analytics(analysis_id: str, cache_key: Optional[str] = None) -> CacheResult:
    """Convenience function to get cached analytics."""
    return cache_manager.get_cached_analytics(analysis_id, cache_key)

def queue_background_job(job_type: str, analysis_id: str, parameters: Dict[str, Any], priority: int = 2) -> JobResult:
    """Convenience function to queue background job."""
    return cache_manager.queue_background_job(job_type, analysis_id, parameters, priority)

if __name__ == "__main__":
    # Test the cache manager
    print("🧪 Testing Cache Manager")
    print("=" * 50)
    
    # Test caching
    test_data = {
        'charts': {'sales': {'type': 'bar', 'data': [1, 2, 3]}},
        'narratives': {'sales': 'Sales are performing well'},
        'analytics': {'total_sales': 1000}
    }
    
    test_metadata = {
        'file_name': 'test.csv',
        'file_size': 1024,
        'processing_time': 1.5
    }
    
    result = cache_analytics_output("test_analysis", test_data, test_metadata)
    
    if result.success:
        print(f"✅ Successfully cached analytics output")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
    else:
        print(f"❌ Error: {result.error_message}")
    
    # Test retrieval
    cached_result = get_cached_analytics("test_analysis")
    
    if cached_result.success and cached_result.cache_hit:
        print(f"✅ Successfully retrieved cached analytics")
        print(f"📊 Data keys: {list(cached_result.data.keys())}")
    else:
        print(f"❌ Cache miss or error: {cached_result.error_message}")
    
    # Test background job
    job_result = queue_background_job("full_file_rerun", "test_analysis", {"file_path": "test.csv"})
    
    if job_result.success:
        print(f"✅ Successfully queued background job: {job_result.job_id}")
    else:
        print(f"❌ Error queuing job: {job_result.error_message}")
