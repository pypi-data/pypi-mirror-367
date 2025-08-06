"""
Copper Sun Brass Storage - SQLite-based storage with proper concurrency handling

Replaces the broken DCP JSON file approach with a robust SQLite database
that handles locking, transactions, and concurrent access properly.
"""
import sqlite3
import json
import time
import hashlib
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BrassStorage:
    """SQLite-based storage for all Copper Sun Brass data.
    
    Provides transactional storage for observations, file state, patterns,
    and ML usage tracking. Handles concurrent access safely.
    """
    
    def __init__(self, db_path: Path):
        """Initialize storage with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._local = threading.local()
        self._db_lock = threading.RLock()
        self._init_db()
        
    def _init_db(self):
        """Create database schema if not exists."""
        with self.transaction() as conn:
            # Create all tables first
            # Observations table - replaces DCP observations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    source_agent TEXT NOT NULL,
                    priority INTEGER DEFAULT 50,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # File state tracking for incremental analysis
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_state (
                    file_path TEXT PRIMARY KEY,
                    last_hash TEXT,
                    last_analyzed TIMESTAMP,
                    complexity INTEGER DEFAULT 0,
                    todo_count INTEGER DEFAULT 0,
                    line_count INTEGER DEFAULT 0,
                    issues JSON
                )
            """)
            
            # Pattern tracking for learning
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data JSON NOT NULL,
                    file_path TEXT,
                    confidence REAL DEFAULT 0.5,
                    occurrences INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # ML usage tracking for cost monitoring
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_size INTEGER NOT NULL,
                    model_version TEXT NOT NULL,
                    processing_time_ms INTEGER,
                    cache_hits INTEGER DEFAULT 0,
                    cache_misses INTEGER DEFAULT 0
                )
            """)
            
            # Context snapshots for session continuity
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_type TEXT NOT NULL,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate existing databases to add any missing columns (after all tables exist)
            self._migrate_schema(conn)
    
    @contextmanager
    def transaction(self):
        """Thread-safe database transaction context manager.
        
        Supports nested transactions using savepoints for thread safety.
        
        Yields:
            sqlite3.Connection: Database connection with Row factory
        """
        with self._db_lock:
            # Initialize transaction depth tracking for proper nested cleanup
            if not hasattr(self._local, 'transaction_depth'):
                self._local.transaction_depth = 0
            
            # Check if we already have a connection in this thread
            if hasattr(self._local, 'conn') and self._local.conn:
                # Nested transaction - use savepoint
                conn = self._local.conn
                self._local.transaction_depth += 1
                # Generate collision-resistant savepoint ID using thread ID and atomic counter
                if not hasattr(self._local, 'savepoint_counter'):
                    self._local.savepoint_counter = 0
                self._local.savepoint_counter += 1
                # Use bounded timestamp to prevent long-term overflow in extended runtime scenarios
                timestamp_bounded = int(time.time()) % 1000000  # Last 6 digits of timestamp
                savepoint_id = f"sp_{id(threading.current_thread())}_{self._local.savepoint_counter}_{timestamp_bounded}"
                conn.execute(f"SAVEPOINT {savepoint_id}")
                try:
                    yield conn
                    conn.execute(f"RELEASE SAVEPOINT {savepoint_id}")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Database operational error in nested transaction: {e}")
                    conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_id}")
                    raise
                except sqlite3.IntegrityError as e:
                    logger.error(f"Data integrity error in nested transaction: {e}")
                    conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_id}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in nested transaction: {e}")
                    conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint_id}")
                    raise
                finally:
                    self._local.transaction_depth -= 1
            else:
                # New transaction - create connection
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                
                self._local.conn = conn
                self._local.transaction_depth = 1
                try:
                    yield conn
                    conn.commit()
                except sqlite3.OperationalError as e:
                    logger.warning(f"Database operational error in main transaction: {e}")
                    conn.rollback()
                    raise
                except sqlite3.IntegrityError as e:
                    logger.error(f"Data integrity error in main transaction: {e}")
                    conn.rollback()
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in main transaction: {e}")
                    conn.rollback()
                    raise
                finally:
                    # Only clean up if this is the outermost transaction
                    self._local.transaction_depth -= 1
                    if self._local.transaction_depth <= 0:
                        conn.close()
                        self._local.conn = None
                        self._local.transaction_depth = 0
    
    def add_observation(self, obs_type: str, data: Dict[str, Any],
                       source_agent: str, priority: int = 50) -> int:
        """Add an observation to the database.
        
        Args:
            obs_type: Type of observation (e.g., 'code_finding', 'file_modified')
            data: Observation data as dictionary
            source_agent: Agent that created the observation
            priority: Priority level (0-100, higher is more important)
            
        Returns:
            ID of created observation
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        # Timeout-aware retry with exponential backoff
        max_wait_time = 30.0  # 30 second total timeout
        start_time = time.time()
        
        for attempt in range(10):  # More attempts with better backoff
            try:
                with self.transaction() as conn:
                    cursor = conn.execute(
                        """INSERT INTO observations 
                           (type, source_agent, priority, data)
                           VALUES (?, ?, ?, ?)""",
                        (obs_type, source_agent, priority, json.dumps(data))
                    )
                    return cursor.lastrowid
                    
            except sqlite3.OperationalError as e:
                elapsed = time.time() - start_time
                if "locked" in str(e) and elapsed < max_wait_time:
                    # Exponential backoff with jitter and overflow protection
                    backoff = min(0.1 * (2 ** min(attempt, 10)), 2.0)  # Cap exponent to prevent overflow
                    # Use efficient random jitter instead of time-based calculation
                    import random
                    jitter = backoff * 0.1 * random.random()  # More efficient than time.time() % 1
                    time.sleep(backoff + jitter)
                else:
                    if elapsed >= max_wait_time:
                        raise TimeoutError(f"Database locked for {elapsed:.1f}s, giving up")
                    else:
                        logger.error(f"Failed to add observation: {e}")
                        raise
    
    def get_observations(self, source_agent: Optional[str] = None,
                        obs_type: Optional[str] = None,
                        since: Optional[datetime] = None,
                        processed: Optional[bool] = None,
                        limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve observations with filters.
        
        Args:
            source_agent: Filter by agent
            obs_type: Filter by observation type
            since: Only observations after this time
            processed: Filter by processed status
            limit: Maximum number of results
            
        Returns:
            List of observation dictionaries
        """
        query = "SELECT * FROM observations WHERE 1=1"
        params = []
        
        if source_agent:
            query += " AND source_agent = ?"
            params.append(source_agent)
            
        if obs_type:
            query += " AND type = ?"
            params.append(obs_type)
            
        if since:
            query += " AND created_at > ?"
            params.append(since.isoformat())
            
        if processed is not None:
            query += " AND processed = ?"
            params.append(processed)
            
        query += " ORDER BY priority DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.transaction() as conn:
            rows = conn.execute(query, params).fetchall()
            
        return [self._row_to_dict(row) for row in rows]
    
    def mark_observations_processed(self, observation_ids: List[int]):
        """Mark observations as processed.
        
        Args:
            observation_ids: List of observation IDs to mark
        """
        if not observation_ids:
            return
            
        # Validate IDs are integers (paranoid but safe)
        if not all(isinstance(id, int) for id in observation_ids):
            raise ValueError("All observation IDs must be integers")
            
        placeholders = ','.join('?' * len(observation_ids))
        query = f"UPDATE observations SET processed = TRUE WHERE id IN ({placeholders})"
        
        with self.transaction() as conn:
            conn.execute(query, observation_ids)
    
    def should_analyze_file(self, file_path: Path) -> bool:
        """Check if file needs analysis based on hash.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has changed since last analysis
        """
        if not file_path.exists():
            return False
            
        # Calculate current file hash
        try:
            content = file_path.read_bytes()
            current_hash = hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return False
        
        # Check against stored hash
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT last_hash FROM file_state WHERE file_path = ?",
                (str(file_path),)
            ).fetchone()
            
            if not row or row['last_hash'] != current_hash:
                # Update or insert file state
                conn.execute(
                    """INSERT OR REPLACE INTO file_state
                       (file_path, last_hash, last_analyzed, line_count)
                       VALUES (?, ?, CURRENT_TIMESTAMP, ?)""",
                    (str(file_path), current_hash, len(content.decode('utf-8', errors='ignore').splitlines()))
                )
                return True
                
        return False
    
    def update_file_metrics(self, file_path: Path, metrics: Dict[str, Any]):
        """Update metrics for a file.
        
        Args:
            file_path: Path to file
            metrics: Dictionary with keys like 'complexity', 'todo_count', 'issues'
        """
        with self.transaction() as conn:
            # Get current state
            row = conn.execute(
                "SELECT * FROM file_state WHERE file_path = ?",
                (str(file_path),)
            ).fetchone()
            
            if row:
                # Update existing
                updates = []
                params = []
                
                for key in ['complexity', 'todo_count']:
                    if key in metrics:
                        updates.append(f"{key} = ?")
                        params.append(metrics[key])
                        
                if 'issues' in metrics:
                    updates.append("issues = ?")
                    params.append(json.dumps(metrics['issues']))
                    
                if updates:
                    params.append(str(file_path))
                    conn.execute(
                        f"UPDATE file_state SET {', '.join(updates)} WHERE file_path = ?",
                        params
                    )
            else:
                # Insert new file metrics
                conn.execute(
                    """INSERT INTO file_state 
                       (file_path, complexity, todo_count, issues, last_analyzed)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        str(file_path),
                        metrics.get('complexity', 0),
                        metrics.get('todo_count', 0),
                        json.dumps(metrics.get('issues', [])),
                        datetime.now()
                    )
                )
    
    def get_file_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics for recently analyzed files.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file metrics
        """
        with self.transaction() as conn:
            rows = conn.execute(
                """SELECT * FROM file_state 
                   ORDER BY last_analyzed DESC 
                   LIMIT ?""",
                (limit,)
            ).fetchall()
            
        return [
            {
                'file_path': row['file_path'],
                'last_analyzed': row['last_analyzed'],
                'complexity': row['complexity'],
                'todo_count': row['todo_count'],
                'line_count': row['line_count'],
                'issues': self._safe_json_loads(row['issues'], [])
            }
            for row in rows
        ]
    
    def save_pattern(self, pattern_type: str, pattern_data: Dict[str, Any],
                    file_path: Optional[str] = None, confidence: float = 0.5):
        """Save a detected pattern for learning.
        
        Args:
            pattern_type: Type of pattern (e.g., 'code_smell', 'security_issue')
            pattern_data: Pattern details
            file_path: Optional file where pattern was found
            confidence: Confidence level (0-1)
        """
        with self.transaction() as conn:
            # Check if pattern exists
            existing = conn.execute(
                """SELECT id, occurrences FROM patterns
                   WHERE pattern_type = ? AND pattern_data = ?""",
                (pattern_type, json.dumps(pattern_data))
            ).fetchone()
            
            if existing:
                # Update existing pattern
                conn.execute(
                    """UPDATE patterns 
                       SET occurrences = occurrences + 1,
                           confidence = ?,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (confidence, existing['id'])
                )
            else:
                # Insert new pattern
                conn.execute(
                    """INSERT INTO patterns
                       (pattern_type, pattern_data, file_path, confidence)
                       VALUES (?, ?, ?, ?)""",
                    (pattern_type, json.dumps(pattern_data), file_path, confidence)
                )
    
    def get_patterns(self, pattern_type: Optional[str] = None,
                    min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """Get learned patterns.
        
        Args:
            pattern_type: Filter by pattern type
            min_confidence: Minimum confidence level
            
        Returns:
            List of patterns
        """
        query = "SELECT * FROM patterns WHERE confidence >= ?"
        params = [min_confidence]
        
        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)
            
        query += " ORDER BY confidence DESC, occurrences DESC"
        
        with self.transaction() as conn:
            rows = conn.execute(query, params).fetchall()
            
        return [
            {
                'id': row['id'],
                'pattern_type': row['pattern_type'],
                'pattern_data': self._safe_json_loads(row['pattern_data'], {}),
                'file_path': row['file_path'],
                'confidence': row['confidence'],
                'occurrences': row['occurrences']
            }
            for row in rows
        ]
    
    def track_ml_usage(self, batch_size: int, model_version: str,
                      processing_time_ms: int = 0, cache_hits: int = 0,
                      cache_misses: int = 0):
        """Track ML model usage for cost analysis.
        
        Args:
            batch_size: Number of items in batch
            model_version: Model identifier
            processing_time_ms: Processing time in milliseconds
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Input validation
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if processing_time_ms < 0:
            raise ValueError("processing_time_ms cannot be negative")
        if cache_hits < 0 or cache_misses < 0:
            raise ValueError("cache_hits and cache_misses cannot be negative")
        if not model_version or not isinstance(model_version, str):
            raise ValueError("model_version must be a non-empty string")
        
        # Reasonable upper bounds to prevent extreme values
        if batch_size > 100000:
            raise ValueError("batch_size exceeds reasonable limit (100,000)")
        if processing_time_ms > 3600000:  # 1 hour max
            raise ValueError("processing_time_ms exceeds reasonable limit (1 hour)")
        if cache_hits > 1000000 or cache_misses > 1000000:
            raise ValueError("cache statistics exceed reasonable limits (1,000,000)")
        
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO ml_usage
                   (batch_size, model_version, processing_time_ms, cache_hits, cache_misses)
                   VALUES (?, ?, ?, ?, ?)""",
                (batch_size, model_version, processing_time_ms, cache_hits, cache_misses)
            )
    
    def get_ml_stats(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get ML usage statistics.
        
        Args:
            since: Only include usage after this time
            
        Returns:
            Dictionary with usage statistics
        """
        query = "SELECT * FROM ml_usage"
        params = []
        
        if since:
            query += " WHERE timestamp > ?"
            params.append(since.isoformat())
            
        with self.transaction() as conn:
            rows = conn.execute(query, params).fetchall()
            
        if not rows:
            return {
                'total_batches': 0,
                'total_items': 0,
                'avg_batch_size': 0,
                'cache_hit_rate': 0,
                'total_time_ms': 0
            }
            
        total_batches = len(rows)
        total_items = sum(row['batch_size'] for row in rows)
        total_time = sum(row['processing_time_ms'] or 0 for row in rows)
        total_hits = sum(row['cache_hits'] or 0 for row in rows)
        total_misses = sum(row['cache_misses'] or 0 for row in rows)
        
        return {
            'total_batches': total_batches,
            'total_items': total_items,
            'avg_batch_size': total_items / total_batches if total_batches > 0 else 0,
            'cache_hit_rate': total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0,
            'total_time_ms': total_time,
            'avg_time_per_item_ms': total_time / total_items if total_items > 0 else 0
        }
    
    def save_context_snapshot(self, snapshot_type: str, data: Dict[str, Any]):
        """Save a context snapshot for session continuity.
        
        Args:
            snapshot_type: Type of snapshot (e.g., 'project_state', 'session_summary')
            data: Snapshot data
        """
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO context_snapshots
                   (snapshot_type, data)
                   VALUES (?, ?)""",
                (snapshot_type, json.dumps(data))
            )
    
    def get_latest_context_snapshot(self, snapshot_type: str) -> Optional[Dict[str, Any]]:
        """Get the most recent context snapshot of a given type.
        
        Args:
            snapshot_type: Type of snapshot to retrieve
            
        Returns:
            Snapshot data or None if not found
        """
        with self.transaction() as conn:
            row = conn.execute(
                """SELECT data, created_at FROM context_snapshots
                   WHERE snapshot_type = ?
                   ORDER BY created_at DESC
                   LIMIT 1""",
                (snapshot_type,)
            ).fetchone()
            
        if row:
            data = self._safe_json_loads(row['data'], {})
            if not data.get('_corrupted'):
                data['_snapshot_time'] = row['created_at']
            return data
            
        return None
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old observations and snapshots.
        
        Args:
            days: Keep data from last N days
        """
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self.transaction() as conn:
            # Clean old processed observations
            conn.execute(
                "DELETE FROM observations WHERE processed = TRUE AND created_at < ?",
                (cutoff,)
            )
            
            # Clean old context snapshots (keep last 10 of each type)
            conn.execute("""
                DELETE FROM context_snapshots
                WHERE id NOT IN (
                    SELECT id FROM context_snapshots cs1
                    WHERE (
                        SELECT COUNT(*) FROM context_snapshots cs2
                        WHERE cs2.snapshot_type = cs1.snapshot_type
                        AND cs2.created_at >= cs1.created_at
                    ) <= 10
                )
            """)
            
            # Vacuum to reclaim space (outside transaction)
            pass  # VACUUM will be done outside the context manager
            
            # Performance indexes can be added here if needed
        
        # Run VACUUM outside transaction with explicit resource management
        vacuum_conn = None
        try:
            vacuum_conn = sqlite3.connect(self.db_path, timeout=10.0)
            vacuum_conn.execute("VACUUM")
            logger.debug("VACUUM operation completed successfully")
        except Exception as e:
            logger.warning(f"VACUUM failed: {e}")
        finally:
            if vacuum_conn:
                try:
                    vacuum_conn.close()
                    logger.debug("VACUUM connection closed successfully")
                except Exception as close_error:
                    logger.error(f"Failed to close VACUUM connection: {close_error}")
    
    def get_last_analysis_time(self) -> Optional[datetime]:
        """Get the timestamp of the last analysis run."""
        snapshot = self.get_latest_context_snapshot('last_analysis')
        if snapshot and 'timestamp' in snapshot:
            return datetime.fromisoformat(snapshot['timestamp'])
        return None
    
    def update_last_analysis_time(self):
        """Update the timestamp of the last analysis run."""
        self.save_context_snapshot('last_analysis', {
            'timestamp': datetime.now().isoformat()
        })
    
    
    def get_modified_files(self, since: datetime) -> List[str]:
        """Get list of files modified since a given time.
        
        Args:
            since: Datetime to check modifications after
            
        Returns:
            List of file paths that were modified
        """
        with self.transaction() as conn:
            rows = conn.execute("""
                SELECT file_path FROM file_state 
                WHERE last_analyzed > ?
                ORDER BY last_analyzed DESC
            """, (since.isoformat(),)).fetchall()
            
            return [row['file_path'] for row in rows]
    
    def get_observation_count(self) -> int:
        """Get total observation count."""
        with self.transaction() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM observations").fetchone()
            return row["count"] if row else 0
    
    def get_activity_stats(self) -> Dict[str, Any]:
        """Get activity statistics."""
        with self.transaction() as conn:
            # Count by priority
            critical = conn.execute(
                "SELECT COUNT(*) as count FROM observations WHERE priority >= 80"
            ).fetchone()["count"]
            
            important = conn.execute(
                "SELECT COUNT(*) as count FROM observations WHERE priority >= 50 AND priority < 80"
            ).fetchone()["count"]
            
            # Get file count
            files_analyzed = conn.execute(
                "SELECT COUNT(DISTINCT file_path) as count FROM file_state"
            ).fetchone()["count"]
            
            # Get total observations
            total_obs = conn.execute(
                "SELECT COUNT(*) as count FROM observations"
            ).fetchone()["count"]
            
            return {
                "critical_count": critical,
                "important_count": important,
                "files_analyzed": files_analyzed,
                "total_observations": total_obs
            }
    
    def get_observations_by_type(self, obs_type: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get observations of a specific type.
        
        Args:
            obs_type: Type of observation
            limit: Maximum number to return
            
        Returns:
            List of observations
        """
        with self.transaction() as conn:
            # Use priority-based ordering for security issues to show critical/high first
            if obs_type == 'security_issue':
                order_clause = """ORDER BY 
                    CASE json_extract(data, '$.severity')
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    created_at DESC"""
            else:
                # Chronological ordering for other types
                order_clause = "ORDER BY created_at DESC"
                
            query = f"""SELECT * FROM observations 
                       WHERE type = ? 
                       {order_clause}
                       LIMIT ?"""
            
            rows = conn.execute(query, (obs_type, limit)).fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_all_observations(self, limit: int = 5000) -> List[Dict[str, Any]]:
        """Get all observations.
        
        Args:
            limit: Maximum number to return (increased from 1000 to 5000 for better intelligence coverage)
            
        Returns:
            List of observations
        """
        with self.transaction() as conn:
            rows = conn.execute(
                """SELECT * FROM observations 
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,)
            ).fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_generated_tasks(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get generated tasks from storage.
        
        Args:
            limit: Maximum number of tasks to return
            status: Filter by task status (pending, in_progress, completed, etc.)
            
        Returns:
            List of task dictionaries with full task metadata
        """
        observations = self.get_observations_by_type('generated_task', limit=limit)
        
        # Extract task data from observations and optionally filter by status
        tasks = []
        for obs in observations:
            task_data = obs.get('data', {})
            if isinstance(task_data, dict):
                # Filter by status if specified
                if status is None or task_data.get('status') == status:
                    # Include observation metadata for tracking
                    task_data['_observation_id'] = obs.get('id')
                    task_data['_stored_at'] = obs.get('created_at')
                    tasks.append(task_data)
        
        return tasks
    
    def _safe_json_loads(self, json_str: str, fallback=None):
        """Safely parse JSON with proper error handling and corruption detection."""
        if not json_str:
            return fallback if fallback is not None else {}
            
        try:
            parsed_data = json.loads(json_str)
            return parsed_data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Critical: JSON data corruption: {e}")
            # Return corrupted marker for debugging
            raw_data = json_str[:100] if isinstance(json_str, str) else str(json_str)[:100]
            return {
                '_corrupted': True,
                '_error': str(e),
                '_raw_data': raw_data
            }
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        if row is None:
            return {}
        
        result = dict(row)
        # Parse JSON data field with proper error handling
        if 'data' in result and isinstance(result['data'], str):
            try:
                parsed_data = json.loads(result['data'])
                # Validate expected data structure
                if isinstance(parsed_data, dict):
                    result['data'] = parsed_data
                else:
                    raise ValueError(f"Expected dict, got {type(parsed_data).__name__}")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Critical: JSON data corruption in row {result.get('id', 'unknown')}: {e}")
                # Mark record as corrupted instead of silent fallback
                raw_data = result['data'][:100] if isinstance(result['data'], str) else str(result['data'])[:100]
                result['data'] = {
                    '_corrupted': True, 
                    '_error': str(e), 
                    '_raw_data': raw_data
                }
                result['_requires_manual_review'] = True
        
        return result
    
    def _migrate_schema(self, conn):
        """Migrate database schema if needed.
        
        Args:
            conn: Database connection
        """
        # Schema migration logic can be added here if needed in the future
        pass
    

