"""
Copper Sun Brass Scheduler - Intelligent scheduling with adaptive timing

Features:
- APScheduler for reliable scheduling
- Adaptive intervals based on activity
- Resource-aware execution
- Integration with system events
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import platform

# APScheduler for production-ready scheduling
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.job import Job
    HAS_APSCHEDULER = True
except ImportError:
    HAS_APSCHEDULER = False
    AsyncIOScheduler = None

from .config import BrassConfig
from .runner import BrassRunner
from .core.storage import BrassStorage

logger = logging.getLogger(__name__)


class AdaptiveScheduler:
    """Intelligent scheduler that adapts to project activity.
    
    Features:
    - Morning briefings at configurable time
    - Adaptive intervals based on activity
    - Resource-aware scheduling
    - Integration with CI/CD events
    """
    
    def __init__(self, config: BrassConfig):
        """Initialize scheduler with configuration.
        
        Args:
            config: Copper Sun Brass configuration
        """
        self.config = config
        self.runner = BrassRunner(config)
        self.storage = BrassStorage(config.db_path)
        
        # Shutdown event for graceful termination
        self.shutdown_event = asyncio.Event()
        
        # Scheduler instance
        self.scheduler = None
        if HAS_APSCHEDULER:
            self._init_scheduler()
        else:
            logger.warning(
                "APScheduler not available. Install with: pip install apscheduler\n"
                "Falling back to simple interval scheduling."
            )
        
        # Adaptive scheduling state
        self.base_interval = getattr(config, 'base_interval', 300)  # 5 minutes
        self.current_interval = self.base_interval
        self.min_interval = 60  # 1 minute minimum
        self.max_interval = 3600  # 1 hour maximum
        
        # Activity tracking
        self.last_activity_time = datetime.utcnow()
        self.activity_level = 0.5  # 0.0 (quiet) to 1.0 (busy)
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        
        # Error recovery with exponential backoff
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.base_error_delay = 60  # 1 minute base delay
    
    def _init_scheduler(self):
        """Initialize APScheduler."""
        self.scheduler = AsyncIOScheduler(
            timezone='UTC',
            job_defaults={
                'coalesce': True,  # Skip missed jobs
                'max_instances': 1,  # Only one instance at a time
                'misfire_grace_time': 30  # 30 second grace period
            }
        )
    
    async def start(self, mode: str = 'adaptive'):
        """Start scheduler in specified mode.
        
        Args:
            mode: Scheduling mode - 'adaptive', 'continuous', 'periodic', 'manual'
        """
        logger.info(f"Starting Copper Sun Brass scheduler in {mode} mode")
        
        # Initialize runner
        await self.runner.initialize_agents()
        
        if mode == 'manual':
            # Single run
            await self.runner.run_once()
            
        elif mode == 'continuous':
            # Continuous monitoring with Watch
            await self.runner.run_continuous()
            
        elif mode == 'periodic':
            # Fixed interval scheduling
            await self._start_periodic_scheduling()
            
        elif mode == 'adaptive':
            # Adaptive scheduling (default)
            await self._start_adaptive_scheduling()
            
        else:
            raise ValueError(f"Unknown scheduling mode: {mode}")
    
    async def _start_periodic_scheduling(self):
        """Start fixed interval scheduling."""
        if self.scheduler:
            # Use APScheduler
            self.scheduler.add_job(
                self._run_and_track,
                IntervalTrigger(seconds=self.base_interval),
                id='periodic_analysis',
                name='Periodic Copper Sun Brass Analysis'
            )
            
            # Add morning briefing with safe time parsing
            briefing_time = getattr(self.config, 'morning_briefing_time', '09:00')
            try:
                time_parts = briefing_time.split(':')
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    # Validate ranges
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError("Hour/minute out of range")
                else:
                    raise ValueError("Invalid time format")
            except (ValueError, IndexError) as e:
                logger.warning(f"Invalid morning_briefing_time '{briefing_time}': {e}. Using default 09:00")
                hour, minute = 9, 0
            
            self.scheduler.add_job(
                self._morning_briefing,
                CronTrigger(
                    hour=hour,
                    minute=minute
                ),
                id='morning_briefing',
                name='Morning Copper Sun Brass Briefing'
            )
            
            self.scheduler.start()
            
            # Keep running until shutdown signal
            try:
                while not self.shutdown_event.is_set():
                    await asyncio.wait_for(asyncio.sleep(60), timeout=5.0)
            except (KeyboardInterrupt, asyncio.TimeoutError):
                pass
            finally:
                if self.scheduler:
                    self.scheduler.shutdown()
        else:
            # Simple interval loop with shutdown check
            try:
                while not self.shutdown_event.is_set():
                    await self._run_and_track()
                    # Wait for interval or shutdown signal
                    try:
                        await asyncio.wait_for(
                            asyncio.sleep(self.base_interval), 
                            timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        continue  # Check shutdown again
            except asyncio.CancelledError:
                pass
    
    async def _start_adaptive_scheduling(self):
        """Start adaptive scheduling that adjusts to activity."""
        logger.info("Starting adaptive scheduling")
        
        # Start with base interval
        next_run = datetime.utcnow() + timedelta(seconds=self.current_interval)
        
        while not self.shutdown_event.is_set():
            try:
                # Check if it's time to run
                now = datetime.utcnow()
                if now >= next_run:
                    # Check resource availability with timeout protection
                    try:
                        should_run = await asyncio.wait_for(
                            asyncio.to_thread(self.resource_monitor.should_run),
                            timeout=5.0
                        )
                        if should_run:
                            await self._run_and_track()
                            
                            # Adapt interval based on results
                            self._adapt_interval()
                            
                            # Schedule next run
                            next_run = now + timedelta(seconds=self.current_interval)
                        else:
                            logger.info("Skipping run due to high resource usage")
                            # Try again in a minute
                            next_run = now + timedelta(seconds=60)
                    except asyncio.TimeoutError:
                        logger.warning("Resource monitor check timed out, skipping this run")
                        next_run = now + timedelta(seconds=60)
                
                # Check for external triggers with timeout protection
                try:
                    has_trigger = await asyncio.wait_for(
                        self._check_external_triggers(),
                        timeout=5.0
                    )
                    if has_trigger:
                        logger.info("External trigger detected, running analysis")
                        await self._run_and_track()
                        self._boost_activity()
                except asyncio.TimeoutError:
                    logger.warning("External trigger check timed out, continuing normal scheduling")
                
                # Sleep briefly
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.consecutive_errors += 1
                logger.error(f"Adaptive scheduling error ({self.consecutive_errors}/{self.max_consecutive_errors}): {e}")
                
                # Check if we've exceeded maximum consecutive errors
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.critical(f"Maximum consecutive errors ({self.max_consecutive_errors}) reached. Stopping scheduler.")
                    break
                
                # Exponential backoff: base_delay * 2^(consecutive_errors-1)
                backoff_delay = min(
                    self.base_error_delay * (2 ** (self.consecutive_errors - 1)),
                    900  # Cap at 15 minutes maximum delay
                )
                logger.info(f"Backing off for {backoff_delay} seconds due to consecutive errors")
                await asyncio.sleep(backoff_delay)
    
    async def _run_and_track(self):
        """Run analysis and track results."""
        start_time = datetime.utcnow()
        
        try:
            # Run analysis
            await self.runner.run_once()
            
            # Get statistics
            stats = self.runner.get_stats()
            observations = stats.get('total_observations', 0)
            
            # Track activity
            if observations > 0:
                self.last_activity_time = start_time
                self._update_activity_level(observations)
            
            # Reset error counter on successful run
            if self.consecutive_errors > 0:
                logger.info(f"Successful run after {self.consecutive_errors} consecutive errors. Resetting error counter.")
                self.consecutive_errors = 0
            
        except Exception as e:
            logger.error(f"Scheduled run failed: {e}")
    
    def _adapt_interval(self):
        """Adapt scheduling interval based on activity."""
        # Get recent activity stats
        stats = self.storage.get_activity_stats()
        
        total_observations = stats.get('total_observations', 0)
        critical_count = stats.get('critical_count', 0)
        
        # Calculate new interval
        if critical_count > 0:
            # Critical issues - run more frequently
            self.current_interval = max(
                self.min_interval,
                self.current_interval * 0.5
            )
            logger.info(f"Critical issues found, decreasing interval to {self.current_interval}s")
            
        elif total_observations > 10:
            # High activity - run more frequently
            self.current_interval = max(
                self.min_interval,
                self.current_interval * 0.8
            )
            
        elif total_observations == 0:
            # No activity - run less frequently
            self.current_interval = min(
                self.max_interval,
                self.current_interval * 1.2
            )
        
        # Apply activity multiplier
        self.current_interval = int(
            self.current_interval * (2.0 - self.activity_level)
        )
        
        # Ensure bounds
        self.current_interval = max(
            self.min_interval,
            min(self.max_interval, self.current_interval)
        )
    
    def _update_activity_level(self, observations: int):
        """Update activity level based on observations."""
        # Simple exponential moving average
        alpha = 0.3
        normalized_obs = min(1.0, observations / 20.0)  # Normalize to 0-1
        
        self.activity_level = (
            alpha * normalized_obs + 
            (1 - alpha) * self.activity_level
        )
    
    def _boost_activity(self):
        """Boost activity level for external triggers."""
        self.activity_level = min(1.0, self.activity_level + 0.3)
        self.current_interval = self.min_interval
    
    async def _check_external_triggers(self) -> bool:
        """Check for external triggers (git hooks, CI events)."""
        trigger_file = self.config.project_root / '.brass' / 'trigger'
        
        if trigger_file.exists():
            # Read and remove trigger
            try:
                trigger_file.unlink()
                return True
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning(f"Failed to remove trigger file {trigger_file}: {e}")
                pass
        
        return False
    
    async def _morning_briefing(self):
        """Generate morning briefing report."""
        logger.info("Generating morning briefing...")
        
        try:
            # Get overnight activity
            since = datetime.utcnow() - timedelta(hours=12)
            stats = self.storage.get_activity_stats()
            
            # Get critical issues
            critical = self.storage.get_observations(
                priority_min=80,
                since=since
            )
            
            # Generate report
            report = self._format_briefing(stats, critical)
            
            # Save to file for Claude Code to read
            briefing_path = self.config.project_root / '.brass' / 'morning_briefing.md'
            briefing_path.parent.mkdir(exist_ok=True)
            
            with open(briefing_path, 'w') as f:
                f.write(report)
            
            logger.info(f"Morning briefing saved to {briefing_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate morning briefing: {e}")
    
    def _format_briefing(self, stats: Dict[str, Any], critical_issues: list) -> str:
        """Format morning briefing report."""
        now = datetime.utcnow()
        
        report = f"""# Copper Sun Brass Morning Briefing
Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}

## Overnight Activity Summary
- Total observations: {stats.get('total_observations', 0)}
- Critical issues: {stats.get('critical_count', 0)}
- Files analyzed: {stats.get('files_analyzed', 0)}

"""
        
        if critical_issues:
            report += "## Critical Issues Requiring Attention\n\n"
            for issue in critical_issues[:5]:  # Top 5
                data = issue.get('data', {})
                report += f"### {data.get('file_path', data.get('file', 'Unknown file'))}\n"
                report += f"- **Type**: {issue.get('type', 'unknown')}\n"
                report += f"- **Priority**: {issue.get('priority', 0)}\n"
                report += f"- **Description**: {data.get('description', 'No description')}\n"
                report += f"- **Time**: {issue.get('timestamp', 'Unknown')}\n\n"
        else:
            report += "## ✅ No critical issues found\n\n"
        
        # Add recommendations
        if stats.get('critical_count', 0) > 0:
            report += "## Recommendations\n"
            report += "1. Review and address critical security issues immediately\n"
            report += "2. Update tests for modified code\n"
            report += "3. Consider running a full security audit\n"
        
        return report
    
    async def stop(self):
        """Stop scheduler gracefully."""
        logger.info("Stopping scheduler...")
        
        # Signal shutdown to break infinite loops
        self.shutdown_event.set()
        
        if self.scheduler:
            self.scheduler.shutdown(wait=True)
        
        await self.runner.shutdown()


class ResourceMonitor:
    """Monitor system resources to avoid overload."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.cpu_threshold = 80.0  # Don't run if CPU > 80%
        self.memory_threshold = 80.0  # Don't run if memory > 80%
    
    def should_run(self) -> bool:
        """Check if resources allow running analysis."""
        try:
            # Check CPU usage
            if platform.system() != 'Windows':
                load_avg = os.getloadavg()[0]  # 1-minute average
                cpu_count = os.cpu_count()
                if not cpu_count or cpu_count <= 0:
                    logger.warning("Unable to determine CPU count, defaulting to 1")
                    cpu_count = 1
                cpu_percent = (load_avg / cpu_count) * 100
                
                if cpu_percent > self.cpu_threshold:
                    logger.info(f"CPU usage too high: {cpu_percent:.1f}%")
                    return False
            
            # Check memory usage (simplified)
            # In production, use psutil for accurate measurement
            
            return True
            
        except Exception as e:
            logger.error(f"Resource check failed: {e}")
            return True  # Run anyway if check fails


async def main():
    """CLI entry point for scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Copper Sun Brass Scheduler')
    parser.add_argument(
        '--mode',
        choices=['adaptive', 'continuous', 'periodic', 'manual'],
        default='adaptive',
        help='Scheduling mode'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Base interval in seconds (for periodic mode)'
    )
    parser.add_argument(
        '--project',
        type=str,
        default='.',
        help='Project root directory'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create config
    config = BrassConfig(project_root=args.project)
    config.data['base_interval'] = args.interval
    
    # Create and run scheduler
    scheduler = AdaptiveScheduler(config)
    
    try:
        await scheduler.start(mode=args.mode)
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
    finally:
        await scheduler.stop()


if __name__ == '__main__':
    asyncio.run(main())