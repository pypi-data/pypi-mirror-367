#!/usr/bin/env python3
"""
Copper Sun Brass - Autonomous code intelligence for Claude Code

Main entry point for the Copper Sun Brass system.
"""
import asyncio
import logging
import sys
from pathlib import Path
import argparse
from typing import Optional, Dict
import click

from .config import BrassConfig
from .scheduler import AdaptiveScheduler
from .runner import BrassRunner
from .core.storage import BrassStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class BrassCLI:
    """Command-line interface for Copper Sun Brass."""
    
    def __init__(self):
        """Initialize CLI."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description='Copper Sun Brass - Autonomous code intelligence for Claude Code',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start adaptive monitoring (recommended)
  brass start
  
  # Run analysis once
  brass analyze
  
  # Start with custom interval
  brass start --interval 600
  
  # Generate morning briefing
  brass briefing
  
  # Show statistics
  brass stats
  
  # Check specific files
  brass check path/to/file.py
"""
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Start command (continuous monitoring)
        start_parser = subparsers.add_parser(
            'start',
            help='Start Copper Sun Brass monitoring'
        )
        start_parser.add_argument(
            '--mode',
            choices=['adaptive', 'continuous', 'periodic'],
            default='adaptive',
            help='Monitoring mode (default: adaptive)'
        )
        start_parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Base interval in seconds (default: 300)'
        )
        start_parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run in daemon mode (for service integration)'
        )
        start_parser.add_argument(
            '--project',
            type=str,
            default='.',
            help='Project root directory'
        )
        
        # Analyze command (single run)
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='Run analysis once'
        )
        analyze_parser.add_argument(
            'paths',
            nargs='*',
            help='Specific paths to analyze (optional)'
        )
        
        # Briefing command
        subparsers.add_parser(
            'briefing',
            help='Generate analysis briefing'
        )
        
        # Stats command
        subparsers.add_parser(
            'stats',
            help='Show Copper Sun Brass statistics'
        )
        
        # Check command (analyze specific files)
        check_parser = subparsers.add_parser(
            'check',
            help='Check specific files'
        )
        check_parser.add_argument(
            'files',
            nargs='+',
            help='Files to check'
        )
        
        # Init command (setup project)
        init_parser = subparsers.add_parser(
            'init',
            help='Initialize Copper Sun Brass for project'
        )
        init_parser.add_argument(
            '--force',
            action='store_true',
            help='Force reinitialization'
        )
        
        # Global options
        parser.add_argument(
            '--project',
            type=str,
            default='.',
            help='Project root directory (default: current directory)'
        )
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--quiet',
            '-q',
            action='store_true',
            help='Suppress non-error output'
        )
        
        return parser
    
    async def run(self, args: Optional[list] = None):
        """Run CLI with given arguments."""
        args = self.parser.parse_args(args)
        
        # Configure logging level
        if args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        elif args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Create config
        project_root = Path(args.project).resolve()
        config = BrassConfig(project_root)
        
        # Handle commands
        if args.command == 'start':
            await self._cmd_start(config, args)
            
        elif args.command == 'analyze':
            await self._cmd_analyze(config, args)
            
        elif args.command == 'briefing':
            await self._cmd_briefing(config)
            
        elif args.command == 'stats':
            await self._cmd_stats(config)
            
        elif args.command == 'check':
            await self._cmd_check(config, args)
            
        elif args.command == 'init':
            await self._cmd_init(config, args)
            
        else:
            self.parser.print_help()
            sys.exit(1)
    
    async def _cmd_start(self, config: BrassConfig, args):
        """Start continuous monitoring."""
        
        # Handle daemon mode
        if getattr(args, 'daemon', False):
            self._enable_daemon_mode()
            # In daemon mode, run in background and exit parent process
            await self._run_daemon_mode(config, args)
            return
        
        logger.info(f"Starting Copper Sun Brass monitoring for {config.project_root}")
        
        # Update config with CLI args
        # Note: BrassConfig doesn't have a data dict, interval handled via scheduler
        logger.info(f"Using interval: {args.interval} seconds")
        
        # Create and start scheduler
        scheduler = AdaptiveScheduler(config)
        
        try:
            # Normal mode - run scheduler blocking
            await scheduler.start(mode=args.mode)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            await scheduler.stop()
    
    async def _run_daemon_mode(self, config: BrassConfig, args):
        """Run in daemon mode with proper background operation."""
        import os
        import signal
        import asyncio
        
        logger.info(f"Starting daemon mode for {config.project_root}")
        
        # Create PID file atomically to prevent race conditions
        pid_file = config.project_root / '.brass' / 'monitoring.pid'
        pid_file.parent.mkdir(exist_ok=True)
        
        # Check if daemon is already running
        if pid_file.exists():
            try:
                existing_pid = int(pid_file.read_text().strip())
                # Check if process is actually running
                os.kill(existing_pid, 0)  # Doesn't kill, just checks if process exists
                logger.error(f"Daemon already running with PID {existing_pid}")
                return
            except (OSError, ValueError):
                # Process doesn't exist or PID file is corrupted, safe to proceed
                logger.info("Stale PID file found, removing...")
                pid_file.unlink(missing_ok=True)
        
        # Write PID file atomically using temporary file
        import tempfile
        temp_pid_file = pid_file.with_suffix('.tmp')
        try:
            temp_pid_file.write_text(str(os.getpid()))
            temp_pid_file.replace(pid_file)  # Atomic rename on POSIX systems
            logger.info(f"Daemon started with PID {os.getpid()}")
        except Exception as e:
            logger.error(f"Failed to create PID file: {e}")
            temp_pid_file.unlink(missing_ok=True)
            return
        
        # Set up signal handling
        def signal_handler(signum, frame):
            logger.info(f"Daemon received signal {signum}, shutting down...")
            # Clean up PID file and any temporary files with existence check
            pid_file.unlink(missing_ok=True)
            if temp_pid_file.exists():  # Check before unlinking to prevent race condition
                temp_pid_file.unlink(missing_ok=True)
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create scheduler
        scheduler = AdaptiveScheduler(config)
        
        try:
            # Run initial analysis
            logger.info("Running initial analysis...")
            await scheduler._run_and_track()
            
            # Schedule periodic runs without blocking
            logger.info("Starting periodic background monitoring...")
            
            # Simple background loop - run analysis every interval with failure protection
            max_failures = 5
            failure_count = 0
            base_backoff = 60
            
            while failure_count < max_failures:
                try:
                    await asyncio.sleep(args.interval)
                    await scheduler._run_and_track()
                    failure_count = 0  # Reset on success
                except (asyncio.CancelledError, KeyboardInterrupt):
                    logger.info("Daemon shutdown requested")
                    break
                except (OSError, PermissionError) as e:
                    logger.critical(f"System-level error in daemon: {e}")
                    failure_count += 1
                    if failure_count >= max_failures:
                        logger.critical("Maximum daemon failures reached, shutting down")
                        break
                    backoff_time = min(base_backoff * (2 ** failure_count), 300)  # Max 5 min
                    await asyncio.sleep(backoff_time)
                except Exception as e:
                    failure_count += 1
                    backoff_time = min(base_backoff * (2 ** failure_count), 300)  # Max 5 min
                    logger.error(f"Application error in daemon loop ({failure_count}/{max_failures}): {e}")
                    if failure_count >= max_failures:
                        logger.critical("Maximum daemon failures reached, shutting down")
                        break
                    await asyncio.sleep(backoff_time)
                    
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
        finally:
            await scheduler.stop()
            # Clean up PID file and any temporary files with consistent pattern
            pid_file.unlink(missing_ok=True)
            if temp_pid_file.exists():  # Consistent with signal handler pattern
                temp_pid_file.unlink(missing_ok=True)
    
    async def _cmd_analyze(self, config: BrassConfig, args):
        """Run single analysis."""
        logger.info(f"Running Copper Sun Brass analysis for {config.project_root}")
        
        runner = BrassRunner(config)
        
        try:
            await runner.initialize_agents()
            
            if args.paths:
                # Specific path analysis not yet implemented - provide clear error message
                logger.error("Specific path analysis not yet implemented. Use 'brass analyze' for full project analysis.")
                sys.exit(1)
            
            await runner.run_once()
            
            # Show summary
            stats = runner.get_stats()
            self._print_summary(stats)
            
        finally:
            await runner.shutdown()
    
    async def _cmd_briefing(self, config: BrassConfig):
        """Generate analysis briefing."""
        logger.info("Generating Copper Sun Brass briefing...")
        
        storage = BrassStorage(config.db_path)
        scheduler = AdaptiveScheduler(config)
        
        # Generate briefing
        await scheduler._morning_briefing()
        
        # Display briefing with proper error handling
        briefing_path = config.project_root / '.brass' / 'morning_briefing.md'
        if briefing_path.exists():
            try:
                print(briefing_path.read_text())
            except (OSError, PermissionError, UnicodeDecodeError) as e:
                logger.error(f"Failed to read briefing file {briefing_path}: {e}")
        else:
            logger.error("Failed to generate briefing")
    
    async def _cmd_stats(self, config: BrassConfig):
        """Show Copper Sun Brass statistics."""
        storage = BrassStorage(config.db_path)
        
        # Get various stats
        obs_count = storage.get_observation_count()
        recent_stats = storage.get_activity_stats()
        ml_stats = storage.get_ml_stats()
        
        print(f"""
Copper Sun Brass Statistics for {config.project_root}
{'=' * 50}

Observations:
  Total: {obs_count}
  Critical: {recent_stats.get('critical_count', 0)}
  Important: {recent_stats.get('important_count', 0)}
  
Recent Activity (24h):
  Files analyzed: {recent_stats.get('files_analyzed', 0)}
  Observations: {recent_stats.get('total_observations', 0)}
  
ML Pipeline:
  Total processed: {ml_stats.get('total_processed', 0)}
  Cache hits: {ml_stats.get('cache_hits', 0)}
  Avg time: {ml_stats.get('avg_processing_ms', 0):.1f}ms
""")
    
    async def _cmd_check(self, config: BrassConfig, args):
        """Check specific files."""
        logger.info(f"Checking {len(args.files)} files...")
        
        runner = BrassRunner(config)
        
        try:
            await runner.initialize_agents()
            
            # Check each file
            for file_path in args.files:
                path = Path(file_path)
                if not path.exists():
                    logger.error(f"File not found: {file_path}")
                    continue
                
                # Single file analysis not yet implemented - provide clear error message
                logger.error(f"Single file analysis not yet implemented for {file_path}. Use 'brass analyze' for full project analysis.")
            
            logger.error("Single file analysis not yet fully implemented. Use 'brass analyze' for full project analysis.")
            sys.exit(1)
            
        finally:
            await runner.shutdown()
    
    async def _cmd_init(self, config: BrassConfig, args):
        """Initialize Copper Sun Brass for project."""
        logger.info(f"Initializing Copper Sun Brass for {config.project_root}")
        
        brass_dir = config.project_root / '.brass'
        
        if brass_dir.exists() and not args.force:
            logger.error("Copper Sun Brass already initialized. Use --force to reinitialize.")
            sys.exit(1)
        
        # Create directories
        brass_dir.mkdir(exist_ok=True)
        (brass_dir / 'models').mkdir(exist_ok=True)
        (brass_dir / 'cache').mkdir(exist_ok=True)
        
        # Create default config
        config_path = brass_dir / 'config.json'
        config.save()
        
        # Create git hook for triggers
        git_dir = config.project_root / '.git'
        if git_dir.exists():
            hooks_dir = git_dir / 'hooks'
            hooks_dir.mkdir(exist_ok=True)
            
            post_commit_hook = hooks_dir / 'post-commit'
            post_commit_hook.write_text("""#!/bin/sh
# Copper Sun Brass git hook - trigger analysis on commit
touch .brass/trigger
""")
            post_commit_hook.chmod(0o755)
            logger.info("Installed git hooks")
        
        logger.info("Copper Sun Brass initialized successfully!")
        print(f"""
✅ Copper Sun Brass initialized for {config.project_root}

Next steps:
1. Start monitoring: brass start
2. Run analysis: brass analyze
3. View stats: brass stats

Copper Sun Brass will provide continuous intelligence to your Claude Code sessions.
""")
    
    def _enable_daemon_mode(self):
        """Configure for daemon operation."""
        # Set up proper logging for daemon mode
        logging.getLogger().handlers.clear()
        
        # Log to file only in daemon mode with robust error handling
        try:
            log_file = Path.cwd() / '.brass' / 'daemon.log'
            log_file.parent.mkdir(exist_ok=True)
            
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(logging.INFO)
        except (OSError, PermissionError) as e:
            # Fallback to stderr if daemon log setup fails
            logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
            logging.getLogger().setLevel(logging.INFO)
            logger.error(f"Failed to setup daemon logging, using stderr: {e}")
    
    def _print_summary(self, stats: Dict):
        """Print analysis summary."""
        print(f"""
Analysis Complete
{'=' * 30}
Observations: {stats.get('total_observations', 0)}
Errors: {stats.get('errors', 0)}
Runtime: {stats.get('avg_run_time_ms', 0):.1f}ms

ML Pipeline:
  Quick filtered: {stats.get('ml_pipeline', {}).get('quick_filter_rate', 0):.1%}
  ML processed: {stats.get('ml_pipeline', {}).get('ml_rate', 0):.1%}
""")


def main():
    """Main entry point."""
    cli = BrassCLI()
    
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        logger.info("Copper Sun Brass interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Copper Sun Brass error: {e}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()