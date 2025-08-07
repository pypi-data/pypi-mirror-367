#!/usr/bin/env python3
"""
Copper Sun Brass CLI - Command-line interface for Copper Sun Brass Pro setup and management.

This CLI is designed to be invoked by Claude Code during the setup process.
It handles license activation, preference management, and project initialization.
"""

import argparse
import json
import sys
import os
import sys
import time
import getpass
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    from .license_manager import LicenseManager, DEVELOPER_LICENSES
    from .license_compat import CompatibleLicenseManager, migrate_license_file
    from .context_manager import ContextManager
    from .ai_instructions_manager import AIInstructionsManager
    from .system_service_manager import SystemServiceManager
    from .background_process_manager import BackgroundProcessManager
    from .pure_python_security import PurePythonEncryption
    from .api_validation import validate_api_key
    from .migration_utils import ConfigMigration, suggest_migration_actions
except ImportError:
    # When running as script
    from license_manager import LicenseManager, DEVELOPER_LICENSES
    from license_compat import CompatibleLicenseManager, migrate_license_file
    from context_manager import ContextManager
    from ai_instructions_manager import AIInstructionsManager
    from system_service_manager import SystemServiceManager
    from background_process_manager import BackgroundProcessManager
    from pure_python_security import PurePythonEncryption
    from api_validation import validate_api_key
    from migration_utils import ConfigMigration, suggest_migration_actions

# Version automatically read from package metadata
try:
    from importlib.metadata import version
    VERSION = version("coppersun-brass")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version
        VERSION = version("coppersun-brass")
    except ImportError:
        # Final fallback if metadata unavailable
        VERSION = "2.0.2"

# Default paths
BRASS_DIR = Path(".brass")
CONFIG_FILE = BRASS_DIR / "config.json"
AI_INSTRUCTIONS_FILE = BRASS_DIR / "AI_INSTRUCTIONS.md"

# Visual theme definitions
VISUAL_THEMES = {
    "colorful": {
        "active": "🎺",
        "insight": "💡", 
        "alert": "🚨",
        "success": "✨",
        "check": "✅"
    },
    "professional": {
        "active": "📊",
        "insight": "📈",
        "alert": "⚠️",
        "success": "✓",
        "check": "✓"
    },
    "monochrome": {
        "active": "●",
        "insight": "▶",
        "alert": "▲",
        "success": "✓",
        "check": "✓"
    }
}

# Verbosity templates
VERBOSITY_TEMPLATES = {
    "detailed": "{{emoji}} Copper Sun Brass: {{action}} | {{context}} | {{timing}}",
    "balanced": "{{emoji}} Copper Sun Brass: {{message}}",
    "minimal": "{{emoji}} Copper Sun Brass{{optional_message}}"
}

def safe_print(message: str):
    """Print with Windows-safe encoding handling."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace problematic characters for Windows console
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message)


def secure_input(prompt: str, is_sensitive: bool = False) -> str:
    """
    Get user input with optional masking for sensitive data.
    
    Args:
        prompt: The prompt to display
        is_sensitive: If True, mask input (for passwords/API keys)
    
    Returns:
        The user input string
    """
    if is_sensitive:
        try:
            # Validate getpass is available
            if not hasattr(getpass, 'getpass'):
                print("⚠️  Secure input module unavailable, input will be visible")
                return input(prompt)
            
            return getpass.getpass(prompt)
        except (KeyboardInterrupt, EOFError):
            return ""
        except Exception as e:
            # Fallback to regular input if getpass fails
            print("⚠️  Secure input unavailable, input will be visible")
            # Log security event (basic logging)
            import logging
            logging.getLogger(__name__).warning(f"Secure input failed, using fallback: {type(e).__name__}")
            return input(prompt)
    else:
        return input(prompt)


class ProgressReporter:
    """Provides visual feedback for long-running operations."""
    
    def __init__(self, operation_name: str, show_timing: bool = True):
        self.operation_name = operation_name
        self.start_time = time.time()
        self.show_timing = show_timing
        self.steps_completed = 0
        self.total_steps = None
    
    def update(self, message: str, emoji: str = "🔄"):
        """Update progress with a status message."""
        self.steps_completed += 1
        
        if self.total_steps:
            step_info = f" ({self.steps_completed}/{self.total_steps})"
        else:
            step_info = ""
        
        safe_print(f"{emoji} {message}{step_info}...")
    
    def set_total_steps(self, total: int):
        """Set the total number of expected steps for better progress tracking."""
        self.total_steps = total
    
    def complete(self, message: str = None, emoji: str = "✅"):
        """Mark operation as complete with optional custom message."""
        elapsed = time.time() - self.start_time
        
        if message:
            final_msg = message
        else:
            final_msg = f"{self.operation_name} complete"
        
        if self.show_timing and elapsed > 0.1:  # Only show timing for operations > 100ms
            timing_info = f" ({elapsed:.1f}s)"
        else:
            timing_info = ""
        
        safe_print(f"{emoji} {final_msg}{timing_info}")
    
    def error(self, message: str, emoji: str = "❌"):
        """Mark operation as failed with error message."""
        elapsed = time.time() - self.start_time
        
        if self.show_timing and elapsed > 0.1:
            timing_info = f" (after {elapsed:.1f}s)"
        else:
            timing_info = ""
        
        safe_print(f"{emoji} {message}{timing_info}")
    
    def substep(self, message: str, emoji: str = "  🔸"):
        """Show a sub-step within the current operation."""
        safe_print(f"{emoji} {message}...")
    
    @staticmethod
    def quick_status(message: str, emoji: str = "🔄"):
        """Show a quick status message without timing (for fast operations)."""
        safe_print(f"{emoji} {message}...")
    
    @staticmethod  
    def success(message: str, emoji: str = "✅"):
        """Show a quick success message without timing."""
        safe_print(f"{emoji} {message}")


class BrassCLI:
    """Main CLI handler for Copper Sun Brass operations."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with hierarchy: env > global > project > defaults."""
        # 1. Start with defaults
        config = self._default_config()
        
        # 2. Load global user config (PRIORITIZE GLOBAL FOR API KEYS)
        global_config_file = Path.home() / ".brass" / "config.json"
        if global_config_file.exists():
            try:
                with open(global_config_file, 'r') as f:
                    global_config = json.load(f)
                    # Decrypt if encrypted
                    encryption = PurePythonEncryption()
                    global_config = encryption.decrypt_config(global_config)
                    config = self._merge_configs(config, global_config)
            except Exception as e:
                print(f"Warning: Could not load global config: {e}")
        
        # 3. Load project-level config (but don't override API keys from global)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    project_config = json.load(f)
                    # Decrypt if encrypted
                    encryption = PurePythonEncryption()
                    project_config = encryption.decrypt_config(project_config)
                    
                    # Preserve global API keys - don't let project override them
                    global_api_keys = {}
                    if 'user_preferences' in config:
                        for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                            if config['user_preferences'].get(key):
                                global_api_keys[key] = config['user_preferences'][key]
                    
                    config = self._merge_configs(config, project_config)
                    
                    # Restore global API keys
                    if global_api_keys and 'user_preferences' in config:
                        config['user_preferences'].update(global_api_keys)
                        
            except Exception as e:
                print(f"Warning: Could not load project config: {e}")
        
        # 4. Override with environment variables (highest priority)
        if os.getenv('ANTHROPIC_API_KEY'):
            config['user_preferences']['claude_api_key'] = os.getenv('ANTHROPIC_API_KEY')
        if os.getenv('LEMONSQUEEZY_API_KEY'):
            config['user_preferences']['lemonsqueezy_api_key'] = os.getenv('LEMONSQUEEZY_API_KEY')
        
        return config
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration structure."""
        return {
            "version": VERSION,
            "user_preferences": {
                "visual_theme": "colorful",
                "verbosity": "balanced",
                "license_key": None,
                "claude_api_key": None,
                "lemonsqueezy_api_key": None,
                "setup_date": None
            }
        }
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two config dictionaries, with override taking precedence for non-null values."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            elif value is not None:  # Only override with non-null values
                result[key] = value
        return result
    
    def _save_config(self, scope: str = "local"):
        """Save configuration with encryption and secure permissions.
        
        Args:
            scope: "global" to save to ~/.brass/config.json, "local" for project-level
        """
        import stat
        
        if scope == "global":
            config_file = Path.home() / ".brass" / "config.json"
            config_dir = config_file.parent
            config_dir.mkdir(exist_ok=True)
            config_dir.chmod(stat.S_IRWXU)  # 700 - user only
            config = self.config.copy()
        else:  # local scope
            config_file = CONFIG_FILE
            BRASS_DIR.mkdir(exist_ok=True)
            BRASS_DIR.chmod(stat.S_IRWXU)  # 700 - user only
            self._ensure_gitignore()
            config = self.config.copy()
        
        # Encrypt config before saving
        encryption = PurePythonEncryption()
        encrypted_config = encryption.encrypt_config(config)
        
        # Save config with secure permissions
        with open(config_file, 'w') as f:
            json.dump(encrypted_config, f, indent=2)
        config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600 - user read/write only
    
    def _ensure_gitignore(self):
        """Ensure .brass/ is in .gitignore to protect API keys."""
        gitignore = Path(".gitignore")
        
        if not gitignore.exists():
            # Create .gitignore with .brass/ entry
            with open(gitignore, "w") as f:
                f.write("# Copper Sun Brass\n.brass/\n")
            return
        
        # Check if .brass/ already in .gitignore
        content = gitignore.read_text()
        if ".brass/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Copper Sun Brass\n.brass/\n")
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard with fallback handling."""
        if not CLIPBOARD_AVAILABLE:
            return False
        
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
    
    def _print_copy_paste_box(self, message: str, copied: bool = False):
        """Print a formatted box with copy-paste instructions using target emoji style."""
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        print("🎯")
        print("🎯  \033[32m❗ COPY THIS MESSAGE AND PASTE IT TO CLAUDE CODE RIGHT NOW:\033[0m")
        print("🎯")
        print(f"🎯  {message}")
        print("🎯")
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        
        if copied:
            print("\n📋 Message copied to clipboard automatically!")
        else:
            print("\n📋 Clipboard unavailable - please copy the message above manually")
    
    def activate(self, license_key: str) -> bool:
        """Activate Copper Sun Brass with a license key."""
        # Try to migrate old license file if it exists
        migrate_license_file()
        
        # Use standard license manager for validation
        license_info = LicenseManager.validate_license(license_key)
        
        if not license_info.valid:
            safe_print(f"❌ License validation failed: {license_info.reason}")
            safe_print("💡 Double-check your license key")
            safe_print("💡 Get support at: https://brass.coppersun.dev/support")
            return False
        
        # Check if expired
        if license_info.expires:
            safe_print(f"✅ License valid for {license_info.days_remaining} days")
        
        # Store license information
        self.config["user_preferences"]["license_key"] = license_key
        self.config["user_preferences"]["license_type"] = license_info.type
        self.config["user_preferences"]["license_expires"] = license_info.expires
        self.config["user_preferences"]["license_email"] = license_info.email
        
        self._save_config()
        
        if license_info.type == "developer":
            safe_print("✅ Developer license activated - never expires!")
            safe_print("🚀 Full Copper Sun Brass Pro features enabled")
        elif license_info.type == "trial":
            safe_print(f"✅ Trial license activated - {license_info.days_remaining} days remaining")
        else:
            safe_print("✅ License activated successfully!")
            
        return True
    
    def generate_trial(self, days: int = 15, activate: bool = False):
        """Generate trial license with optional activation."""
        safe_print(f"🎯 Generating {days}-day trial license...")
        
        # Use standard license manager for trial generation
        trial_license = LicenseManager.generate_trial_license(days)
        
        if not trial_license:
            safe_print("❌ Trial license generation failed")
            safe_print("💡 Please contact support if this continues")
            return False
        
        if activate:
            safe_print("🔑 Activating trial license...")
            if self.activate(trial_license):
                safe_print(f"✅ Trial activated successfully!")
                safe_print(f"🎺 {days} days of full Copper Sun Brass Pro features")
                return True
            else:
                safe_print("❌ Trial activation failed")
                safe_print("💡 Try: brass activate <trial-license>")
                return False
        else:
            safe_print(f"🎯 Trial license generated: {trial_license}")
            safe_print(f"📝 To activate: brass activate {trial_license}")
            return trial_license
    
    def config_set(self, key: str, value: str = None, scope: str = "global"):
        """Set a configuration value."""
        # Map simple keys to nested structure
        key_map = {
            "visual_theme": ["user_preferences", "visual_theme"],
            "verbosity": ["user_preferences", "verbosity"],
            "claude_api_key": ["user_preferences", "claude_api_key"],
            "lemonsqueezy_api_key": ["user_preferences", "lemonsqueezy_api_key"],
            "user_name": ["user_preferences", "user_name"]
        }
        
        # Define sensitive keys that should use secure input
        sensitive_keys = {"claude_api_key", "lemonsqueezy_api_key"}
        
        if key not in key_map:
            print(f"❌ Configuration key '{key}' not recognized")
            print(f"💡 Available keys: {', '.join(key_map.keys())}")
            print(f"💡 Example: brass config set visual_theme colorful")
            return
        
        # If no value provided and it's a sensitive key, prompt securely
        if value is None and key in sensitive_keys:
            if key == "claude_api_key":
                value = secure_input("🔑 Enter your Claude API key: ", is_sensitive=True).strip()
            elif key == "lemonsqueezy_api_key":
                value = secure_input("🔑 Enter your LemonSqueezy API key: ", is_sensitive=True).strip()
            
            if not value:
                print("❌ No value provided, configuration unchanged")
                return
        elif value is None:
            print(f"❌ Value required for '{key}'")
            print(f"💡 Usage: brass config set {key} <value>")
            if key in sensitive_keys:
                print(f"💡 For secure input: brass config set {key}")
            return
        
        # Validate values
        if key == "visual_theme" and value not in VISUAL_THEMES:
            print(f"❌ Visual theme '{value}' not available")
            print(f"💡 Available themes: {', '.join(VISUAL_THEMES.keys())}")
            print(f"💡 Example: brass config set visual_theme colorful")
            return
        
        if key == "verbosity" and value not in VERBOSITY_TEMPLATES:
            print(f"❌ Verbosity level '{value}' not available")
            print(f"💡 Available levels: {', '.join(VERBOSITY_TEMPLATES.keys())}")
            print(f"💡 Example: brass config set verbosity balanced")
            return
        
        # Validate API key formats
        if key == "claude_api_key" and value and not value.startswith("sk-ant-"):
            print("⚠️  Warning: API key format may be incorrect")
            print("💡 Claude API keys typically start with 'sk-ant-api'")
            print("💡 Get your key at: https://console.anthropic.com")
        
        # Determine config file based on scope
        if scope == "global":
            config_file = Path.home() / ".brass" / "config.json"
            config_dir = config_file.parent
            config_dir.mkdir(exist_ok=True)
            
            # Secure global config directory permissions
            import stat
            config_dir.chmod(stat.S_IRWXU)  # 700 - user only
            
            # Load or create global config
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                except Exception:
                    config = self._default_config()
            else:
                config = self._default_config()
        else:  # local scope
            config_file = CONFIG_FILE
            config = self.config.copy()  # Use current loaded config
        
        # Set the value
        config_path = key_map[key]
        current = config
        for part in config_path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[config_path[-1]] = value
        
        # Save to appropriate file with secure permissions
        if scope == "global":
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600 - user read/write only
        else:
            self.config = config
            self._save_config()
        
        # Mask sensitive values in success message
        if key in sensitive_keys:
            masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"✅ Configuration updated ({scope}): {key} = {masked_value}")
        else:
            print(f"✅ Configuration updated ({scope}): {key} = {value}")
        
        # Security reminder for API keys
        if "api_key" in key:
            if scope == "global":
                print("🔒 Security tip: For production/CI, use environment variables instead:")
                if key == "claude_api_key":
                    print("   export ANTHROPIC_API_KEY=your-key")
                elif key == "lemonsqueezy_api_key":
                    print("   export LEMONSQUEEZY_API_KEY=your-key")
        
        # Reload config to reflect changes
        self.config = self._load_config()
    
    def config_get(self, key: str):
        """Get a configuration value showing the resolved result."""
        key_map = {
            "visual_theme": ["user_preferences", "visual_theme"],
            "verbosity": ["user_preferences", "verbosity"],
            "claude_api_key": ["user_preferences", "claude_api_key"],
            "lemonsqueezy_api_key": ["user_preferences", "lemonsqueezy_api_key"],
            "user_name": ["user_preferences", "user_name"],
            "license_key": ["user_preferences", "license_key"]
        }
        
        if key not in key_map:
            print(f"❌ Configuration key '{key}' not recognized")
            print(f"💡 Available keys: {', '.join(key_map.keys())}")
            print(f"💡 Use: brass config set <key> <value>")
            return
        
        # Get resolved value
        config_path = key_map[key]
        current = self.config
        for part in config_path:
            current = current.get(part, {})
        
        if current:
            # Mask sensitive keys
            if "api_key" in key and len(str(current)) > 10:
                masked = str(current)[:8] + "..." + str(current)[-4:]
                print(f"{key}: {masked}")
            else:
                print(f"{key}: {current}")
        else:
            print(f"{key}: (not set)")
    
    def config_list(self):
        """List all configuration values."""
        prefs = self.config.get("user_preferences", {})
        
        print("📋 Current Configuration (resolved):\n")
        
        # Non-sensitive values
        for key in ["visual_theme", "verbosity", "user_name"]:
            value = prefs.get(key, "(not set)")
            print(f"  {key}: {value}")
        
        # API keys (masked)
        for key in ["claude_api_key", "lemonsqueezy_api_key"]:
            value = prefs.get(key)
            if value and len(str(value)) > 10:
                masked = str(value)[:8] + "..." + str(value)[-4:]
                print(f"  {key}: {masked}")
            else:
                print(f"  {key}: (not set)")
        
        # License info
        license_key = prefs.get("license_key")
        if license_key:
            license_type = prefs.get("license_type", "unknown")
            print(f"  license_key: {license_type} license active")
        else:
            print(f"  license_key: (not set)")
        
        print(f"\n📍 Config resolution order: env vars > ~/.brass/config.json > ./.brass/config.json > defaults")
        print(f"🔒 Security: Config files have 600 permissions (user read/write only)")
    
    def config_audit(self):
        """Show API key locations and security status - NEW SECURITY FEATURE."""
        print("🔒 Copper Sun Brass Security Audit\n")
        
        # Check resolved configuration (what the system actually uses)
        print("🎯 Resolved Configuration (Active Values):")
        resolved_prefs = self.config["user_preferences"]
        
        # Check Claude API key
        claude_key = resolved_prefs.get("claude_api_key")
        if claude_key:
            # Determine source of the key
            if os.getenv('ANTHROPIC_API_KEY'):
                print(f"  ✅ claude_api_key: Set (from ANTHROPIC_API_KEY environment variable)")
            else:
                print(f"  ✅ claude_api_key: Set (from config file)")
        else:
            print(f"  ⚪ claude_api_key: Not set")
        
        # Check LemonSqueezy API key
        lemonsqueezy_key = resolved_prefs.get("lemonsqueezy_api_key")
        if lemonsqueezy_key:
            if os.getenv('LEMONSQUEEZY_API_KEY'):
                print(f"  ✅ lemonsqueezy_api_key: Set (from LEMONSQUEEZY_API_KEY environment variable)")
            else:
                print(f"  ✅ lemonsqueezy_api_key: Set (from config file)")
        else:
            print(f"  ⚪ lemonsqueezy_api_key: Not set")
        
        # Check environment variables (for reference)
        print("\n📍 Environment Variables:")
        env_keys = ['ANTHROPIC_API_KEY', 'LEMONSQUEEZY_API_KEY']
        env_found = False
        for key in env_keys:
            if os.getenv(key):
                env_found = True
                print(f"  ✅ {key}: Set (takes highest priority)")
            else:
                print(f"  ⚪ {key}: Not set")
        
        if not env_found:
            print("  💡 Environment variables take highest priority and override config files")
        
        # Check global config
        print("\n📁 Global Configuration:")
        global_config_file = Path.home() / ".brass" / "config.json"
        if global_config_file.exists():
            try:
                import stat
                file_stats = global_config_file.stat()
                permissions = oct(file_stats.st_mode)[-3:]
                
                with open(global_config_file, 'r') as f:
                    global_config = json.load(f)
                
                is_encrypted = global_config.get('_encrypted', False)
                has_api_keys = False
                
                if is_encrypted:
                    print(f"  ✅ {global_config_file}")
                    print(f"     🔐 Encrypted: Yes")
                    print(f"     🛡️  Permissions: {permissions} (should be 600)")
                    if '_encrypted_data' in global_config:
                        print(f"     🔑 Contains encrypted API keys")
                        has_api_keys = True
                else:
                    # Check for unencrypted API keys
                    if 'user_preferences' in global_config:
                        prefs = global_config['user_preferences']
                        for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                            if prefs.get(key) and prefs[key] != '[ENCRYPTED]':
                                has_api_keys = True
                                break
                    
                    print(f"  ⚠️  {global_config_file}")
                    print(f"     🔓 Encrypted: No")
                    print(f"     🛡️  Permissions: {permissions} (should be 600)")
                    if has_api_keys:
                        print(f"     ⚠️  Contains UNENCRYPTED API keys")
                
                if permissions != '600':
                    print(f"     🚨 Security Issue: File permissions should be 600")
                    
            except Exception as e:
                print(f"  ❌ Error reading {global_config_file}: {e}")
        else:
            print(f"  ⚪ {global_config_file}: Not found")
            print(f"     💡 Global config recommended for API key storage")
        
        # Check local project config
        print("\n📁 Project Configuration:")
        local_config_file = Path(".brass/config.json")
        if local_config_file.exists():
            try:
                import stat
                file_stats = local_config_file.stat()
                permissions = oct(file_stats.st_mode)[-3:]
                
                with open(local_config_file, 'r') as f:
                    local_config = json.load(f)
                
                is_encrypted = local_config.get('_encrypted', False)
                has_api_keys = False
                
                if 'user_preferences' in local_config:
                    prefs = local_config['user_preferences']
                    for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                        if prefs.get(key) and prefs[key] not in [None, '', '[ENCRYPTED]']:
                            has_api_keys = True
                            break
                
                print(f"  📄 {local_config_file}")
                print(f"     🔐 Encrypted: {'Yes' if is_encrypted else 'No'}")
                print(f"     🛡️  Permissions: {permissions} (should be 600)")
                
                if has_api_keys:
                    if is_encrypted:
                        print(f"     🔑 Contains encrypted API keys")
                    else:
                        print(f"     ⚠️  Contains UNENCRYPTED API keys")
                        print(f"     💡 Consider moving to global config: brass config global set claude_api_key")
                else:
                    print(f"     ✅ No API keys stored locally")
                    
            except Exception as e:
                print(f"  ❌ Error reading {local_config_file}: {e}")
        else:
            print(f"  ⚪ {local_config_file}: Not found")
            print(f"     💡 Local config stores project-specific settings")
        
        # Check for legacy .env files
        print("\n📁 Legacy .env Files:")
        env_files_found = []
        search_paths = [
            Path(".env"),
            Path("../.env"),  
            Path("../../.env"),
        ]
        
        for env_path in search_paths:
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    has_api_keys = 'ANTHROPIC_API_KEY' in content or 'LEMONSQUEEZY_API_KEY' in content
                    if has_api_keys:
                        env_files_found.append(env_path)
                        print(f"  ⚠️  {env_path}: Contains API keys")
                        print(f"     💡 Consider moving to global config for security")
                except Exception:
                    pass
        
        if not env_files_found:
            print(f"  ✅ No legacy .env files with API keys found")
        
        # Security recommendations
        print("\n🛡️  Security Recommendations:")
        print("  1. Store API keys in global config (encrypted automatically)")
        print("  2. Use environment variables for production/CI environments")
        print("  3. Keep project configs for non-sensitive settings only")
        print("  4. Run 'brass uninstall --credentials' to clean up API keys")
        print("  5. File permissions should be 600 (user read/write only)")
        
        # Summary
        print(f"\n📊 Security Status Summary:")
        claude_key_active = bool(resolved_prefs.get("claude_api_key"))
        lemonsqueezy_key_active = bool(resolved_prefs.get("lemonsqueezy_api_key"))
        using_env_vars = bool(os.getenv('ANTHROPIC_API_KEY') or os.getenv('LEMONSQUEEZY_API_KEY'))
        legacy_files = len(env_files_found)
        
        print(f"  🔑 Claude API Key: {'✅ Active' if claude_key_active else '❌ Missing'}")
        print(f"  🔑 LemonSqueezy API Key: {'✅ Active' if lemonsqueezy_key_active else '⚪ Not needed for basic usage'}")
        
        if using_env_vars:
            print("  ✅ Using environment variables (most secure for production)")
        elif claude_key_active and global_config_file.exists():
            print("  ✅ Using global config (recommended for development)")
        elif claude_key_active:
            print("  ⚠️  Using local config (consider moving to global)")
        else:
            print("  ❌ No API key configuration detected")
        
        if legacy_files > 0:
            print(f"  ⚠️  {legacy_files} legacy .env file(s) with API keys found")
        else:
            print("  ✅ No legacy API key files found")
    
    def config_show(self):
        """Display current configuration hierarchy - NEW FEATURE."""
        print("📋 Copper Sun Brass Configuration Hierarchy\n")
        
        # Show resolution order
        print("🔄 Resolution Order (highest to lowest priority):")
        print("  1. Environment Variables")
        print("  2. Global Config (~/.brass/config.json)")
        print("  3. Project Config (./.brass/config.json)")
        print("  4. Built-in Defaults")
        
        # Check each level
        print("\n📍 Environment Variables:")
        env_vars = ['ANTHROPIC_API_KEY', 'LEMONSQUEEZY_API_KEY']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "(set)"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ⚪ {var}: Not set")
        
        # Global config
        print("\n📁 Global Configuration:")
        global_config_file = Path.home() / ".brass" / "config.json"
        if global_config_file.exists():
            print(f"  ✅ {global_config_file}")
            try:
                with open(global_config_file, 'r') as f:
                    global_config = json.load(f)
                    
                if global_config.get('_encrypted'):
                    print(f"     🔐 Status: Encrypted")
                    if '_encrypted_data' in global_config:
                        print(f"     🔑 Contains: Encrypted sensitive data")
                else:
                    print(f"     🔓 Status: Plain text")
                    
                # Show non-sensitive values
                if 'user_preferences' in global_config:
                    prefs = global_config['user_preferences']
                    for key in ['visual_theme', 'verbosity']:
                        if key in prefs:
                            print(f"     📝 {key}: {prefs[key]}")
                            
            except Exception as e:
                print(f"     ❌ Error reading: {e}")
        else:
            print(f"  ⚪ {global_config_file}: Not found")
        
        # Project config  
        print("\n📁 Project Configuration:")
        project_config_file = Path(".brass/config.json")
        if project_config_file.exists():
            print(f"  ✅ {project_config_file}")
            try:
                with open(project_config_file, 'r') as f:
                    project_config = json.load(f)
                    
                if project_config.get('_encrypted'):
                    print(f"     🔐 Status: Encrypted")
                else:
                    print(f"     🔓 Status: Plain text")
                    
                # Show settings
                if 'user_preferences' in project_config:
                    prefs = project_config['user_preferences']
                    for key, value in prefs.items():
                        if key not in ['claude_api_key', 'lemonsqueezy_api_key', 'license_key']:
                            print(f"     📝 {key}: {value}")
                            
            except Exception as e:
                print(f"     ❌ Error reading: {e}")
        else:
            print(f"  ⚪ {project_config_file}: Not found")
        
        # Final resolved values
        print("\n✨ Final Resolved Configuration:")
        prefs = self.config.get("user_preferences", {})
        
        # Show current values (excluding sensitive data)
        display_keys = ['visual_theme', 'verbosity', 'user_name']
        for key in display_keys:
            value = prefs.get(key, "(default)")
            print(f"  📋 {key}: {value}")
        
        # API keys (masked)
        for key in ['claude_api_key', 'lemonsqueezy_api_key']:
            value = prefs.get(key)
            if value:
                if len(str(value)) > 10:
                    masked = str(value)[:8] + "..." + str(value)[-4:]
                    source = self._identify_config_source(key)
                    print(f"  🔑 {key}: {masked} (from {source})")
                else:
                    print(f"  🔑 {key}: (set)")
            else:
                print(f"  🔑 {key}: (not configured)")
        
        print(f"\n💡 Use 'brass config audit' for detailed security analysis")
    
    def _identify_config_source(self, key: str) -> str:
        """Identify the source of a configuration value."""
        # Check environment first
        env_key_map = {
            'claude_api_key': 'ANTHROPIC_API_KEY',
            'lemonsqueezy_api_key': 'LEMONSQUEEZY_API_KEY'
        }
        
        if key in env_key_map and os.getenv(env_key_map[key]):
            return "environment"
        
        # Check global config
        global_config_file = Path.home() / ".brass" / "config.json"
        if global_config_file.exists():
            try:
                with open(global_config_file, 'r') as f:
                    global_config = json.load(f)
                
                # Handle encrypted configs
                if global_config.get('_encrypted'):
                    if '_encrypted_data' in global_config:
                        return "global (encrypted)"
                elif 'user_preferences' in global_config:
                    prefs = global_config['user_preferences']
                    if prefs.get(key):
                        return "global"
            except Exception:
                pass
        
        # Check project config
        project_config_file = Path(".brass/config.json")
        if project_config_file.exists():
            try:
                with open(project_config_file, 'r') as f:
                    project_config = json.load(f)
                
                if 'user_preferences' in project_config:
                    prefs = project_config['user_preferences']
                    if prefs.get(key):
                        return "project"
            except Exception:
                pass
        
        return "default"
    
    def migrate_configurations(self, dry_run: bool = False):
        """Migrate configurations to secure encrypted storage - NEW SECURITY FEATURE."""
        print("🔧 Copper Sun Brass Configuration Migration\n")
        
        migration = ConfigMigration()
        
        # Step 1: Analyze current state
        print("1. 🔍 Analyzing current configuration...")
        status = migration.detect_migration_needed()
        
        print(f"   Migration needed: {'Yes' if status['migration_needed'] else 'No'}")
        print(f"   Priority level: {status['priority']}")
        print(f"   Configurations found: {len(status['legacy_configs_found'])}")
        
        if not status['migration_needed']:
            print("\n✅ Your configuration is already secure!")
            print("💡 No migration needed.")
            print("🛡️  Run 'brass config audit' to verify security status")
            return
        
        # Step 2: Show what needs migration
        print(f"\n2. 📋 Configuration analysis:")
        
        if status['security_issues']:
            print("   🚨 Security issues found:")
            for issue in status['security_issues']:
                print(f"     • {issue}")
        
        if status['legacy_configs_found']:
            print("   📁 Configurations found:")
            for config in status['legacy_configs_found']:
                config_type = config['type'].replace('_', ' ').title()
                encryption_status = "Encrypted" if config['encrypted'] else "Plain text"
                api_status = "Contains API keys" if config['has_api_keys'] else "No API keys"
                print(f"     • {config_type}: {config['location']}")
                print(f"       Status: {encryption_status}, {api_status}")
        
        # Step 3: Show recommendations
        if status['recommendations']:
            print(f"\n3. 💡 Recommendations:")
            for rec in status['recommendations']:
                print(f"   • {rec}")
        
        if dry_run:
            print(f"\n🔍 DRY RUN MODE - No changes will be made")
            print(f"💡 Run without --dry-run to perform actual migration")
            
            # Show what would be done
            try:
                results = migration.migrate_configurations(dry_run=True)
                
                if results['actions_taken']:
                    print(f"\n📋 Actions that would be taken:")
                    for action in results['actions_taken']:
                        print(f"   • {action}")
                
            except Exception as e:
                print(f"\n❌ Error during dry run: {e}")
            
            return
        
        # Step 4: Confirm migration
        print(f"\n4. 🔧 Ready to migrate")
        print(f"💡 This will:")
        print(f"   • Create secure encrypted storage in ~/.brass/")
        print(f"   • Encrypt API keys with machine-specific encryption")
        print(f"   • Create backup copies of existing configurations")
        print(f"   • Preserve all your current settings")
        
        confirm = input(f"\nProceed with migration? (Y/n): ").strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            print(f"\n🔄 Starting migration...")
            
            try:
                results = migration.migrate_configurations(dry_run=False)
                
                if results['success']:
                    print(f"✅ Migration completed successfully!")
                    
                    if results['actions_taken']:
                        print(f"\n📋 Actions completed:")
                        for action in results['actions_taken']:
                            if not action.startswith('DRY RUN'):
                                print(f"   • {action}")
                    
                    if results['security_improvements']:
                        print(f"\n🛡️  Security improvements:")
                        for improvement in results['security_improvements']:
                            print(f"   • {improvement}")
                    
                    if results['backed_up_files']:
                        print(f"\n💾 Backup files created:")
                        for backup in results['backed_up_files']:
                            print(f"   • {backup}")
                    
                    print(f"\n🔄 Reloading configuration...")
                    self.config = self._load_config()
                    
                    print(f"\n🎉 Migration complete! Your configuration is now secure.")
                    print(f"💡 Run 'brass config audit' to verify the new security status")
                    
                else:
                    print(f"❌ Migration encountered issues:")
                    for error in results['errors']:
                        print(f"   • {error}")
                    
                    print(f"\n💡 You may need to:")
                    print(f"   • Check file permissions")
                    print(f"   • Manually move configuration files")
                    print(f"   • Contact support if issues persist")
                
            except Exception as e:
                print(f"❌ Migration failed with error: {e}")
                print(f"💡 Try running with --dry-run to diagnose issues")
                print(f"💡 Check that you have write permissions to ~/.config/")
        
        else:
            print(f"⏭️  Migration cancelled")
            print(f"💡 Run 'brass migrate' again when you're ready")
            print(f"💡 Use 'brass config audit' to see current security status")
    
    def init(self, mode: str = "claude-companion", integration_mode: Optional[str] = None):
        """Initialize Copper Sun Brass for the current project.
        
        Args:
            mode: Initialization mode (default: claude-companion)
            integration_mode: Override integration questions ('claude-code', 'basic', or None for interactive)
        """
        # Check if license is activated
        if not self.config["user_preferences"].get("license_key"):
            print("❌ License activation required")
            print("💡 Activate with: brass activate <your-license-key>")
            print("💡 Start free trial: brass generate-trial --activate")
            print("💡 Get license: https://brass.coppersun.dev/checkout")
            return False
        
        # Validate license is still valid
        license_key = self.config["user_preferences"]["license_key"]
        license_info = LicenseManager.validate_license(license_key)
        if not license_info.valid:
            if "expired" in license_info.reason.lower():
                # CRITICAL: This redirects via Cloudflare to LemonSqueezy checkout
                # Test mode: Redirects to test checkout URL
                # Live mode: Redirects to live checkout URL  
                # To switch: Update Cloudflare redirect rule, NO code changes needed
                # Documentation: See docs/planning/CHECKOUT_URL_MANAGEMENT.md
                print(f"⏰ Trial expired. Upgrade to continue: https://brass.coppersun.dev/checkout")
                print("\n🔑 Have a license key from your purchase email?")
                new_license = secure_input("Enter your license key (from purchase email): ", is_sensitive=True).strip()
                if new_license:
                    print("\n🔄 Activating license...")
                    if self.activate(new_license):
                        print("✅ License activated! Welcome to Brass Pro.")
                        # Continue with initialization after successful activation
                        license_info = LicenseManager.validate_license(new_license)
                    else:
                        print("❌ License activation failed")
                        print("💡 Double-check your license key")
                        print("💡 Contact support: https://brass.coppersun.dev/support")
                        return False
                else:
                    print("\n💡 Run 'brass activate <license-key>' when you have your license.")
                    return False
            else:
                print(f"❌ License validation failed: {license_info.reason}")
                print("💡 Activate with: brass activate <your-license-key>")
                print("💡 Start free trial: brass generate-trial --activate")
                return False
        
        # Check for migration opportunities (NEW SECURITY FEATURE)
        migration = ConfigMigration()
        migration_status = migration.detect_migration_needed()
        
        if migration_status['migration_needed']:
            print(f"\n🔧 Configuration Migration Available")
            priority = migration_status['priority']
            
            if priority == 'high':
                print("🚨 SECURITY NOTICE: Unencrypted API keys detected!")
                print("🔒 Your API keys should be encrypted for security.")
            elif priority == 'medium':
                print("⚠️  Security improvement available")
                print("🔒 Consider consolidating API key storage for better security.")
            
            # Show specific issues
            if migration_status['security_issues']:
                print("\n📋 Issues found:")
                for issue in migration_status['security_issues']:
                    print(f"  • {issue}")
            
            # Offer migration
            print(f"\n💡 We can automatically migrate your configuration to be more secure.")
            print(f"💡 This will:")
            print(f"   • Encrypt API keys with machine-specific encryption")
            print(f"   • Move config to standard location (~/.brass/)")
            print(f"   • Create secure backups of existing files")
            
            migrate_now = input("\n🔧 Migrate now? (recommended) (Y/n): ").strip().lower()
            
            if migrate_now in ['', 'y', 'yes']:
                print("\n🔄 Starting secure migration...")
                
                try:
                    migration_results = migration.migrate_configurations(dry_run=False)
                    
                    if migration_results['success']:
                        print("✅ Migration completed successfully!")
                        
                        if migration_results['security_improvements']:
                            print("\n🛡️  Security improvements:")
                            for improvement in migration_results['security_improvements']:
                                print(f"  • {improvement}")
                        
                        if migration_results['backed_up_files']:
                            print(f"\n💾 Backup files created:")
                            for backup in migration_results['backed_up_files']:
                                print(f"  • {backup}")
                        
                        # Reload config after migration
                        self.config = self._load_config()
                        print(f"\n🔄 Configuration reloaded with new secure settings")
                        
                    else:
                        print("❌ Migration encountered issues:")
                        for error in migration_results['errors']:
                            print(f"  • {error}")
                        print("💡 You can try manual migration later with 'brass migrate'")
                        
                except Exception as e:
                    print(f"❌ Migration failed: {e}")
                    print("💡 You can try manual migration later with 'brass migrate'")
            else:
                print("⏭️  Skipping migration for now")
                print("💡 Run 'brass migrate' later to improve security")
                print("💡 Use 'brass config audit' to see detailed security status")
        
        # Check if Claude API key is configured - if not, enter guided setup
        if not self.config["user_preferences"].get("claude_api_key"):
            print("🎯 Claude API key required for AI analysis and insights")
            print("💡 Tip: Set ANTHROPIC_API_KEY environment variable for production")
            
            # Add retry limit to prevent infinite loop
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                print("🎯🎯🎯")
                api_key = secure_input("🎯 Enter your Claude API key (or press Enter for instructions): ", is_sensitive=True).strip()
                
                if api_key:
                    # Validate API key before saving
                    print("🔍 Validating API key...")
                    is_valid, message = validate_api_key('claude_api_key', api_key)
                    
                    if is_valid:
                        # Save to GLOBAL config by default for security
                        self.config["user_preferences"]["claude_api_key"] = api_key
                        self._save_config(scope="global")
                        print("✅ API key validated and saved globally!")
                        print("🔒 API key encrypted and stored securely in ~/.brass/config.json")
                        print("💡 All future projects will use this key automatically")
                        break
                    else:
                        print(f"❌ API key validation failed: {message}")
                        print("💡 Double-check your key from https://console.anthropic.com")
                        
                        # Ask if user wants to save anyway (for offline scenarios)
                        if "network" in message.lower() or "test failed" in message.lower():
                            save_anyway = input("🤔 Save API key anyway? (y/N): ").strip().lower()
                            if save_anyway == 'y':
                                self.config["user_preferences"]["claude_api_key"] = api_key
                                self._save_config(scope="global")
                                print("⚠️  API key saved without validation (network issues)")
                                break
                        retry_count += 1
                        continue
                else:
                    # User pressed Enter - show instructions
                    print("\n🎯 To get your Claude API key:")
                    print("   1. Visit https://console.anthropic.com")
                    print("   2. Sign up or log in to your account")
                    print("   3. Navigate to 'API Keys' section")
                    print("   4. Click 'Create Key'")
                    print("\n💡 Alternative: Set environment variable ANTHROPIC_API_KEY")
                    
                    # Ask again for key input
                    retry_count += 1
                    continue
            
            # Maximum retries reached
            if retry_count >= max_retries:
                print("❌ Maximum API key attempts reached. Please try again later.")
                print("💡 Alternative: Set ANTHROPIC_API_KEY environment variable")
                print("💡 Or run: brass config set claude_api_key")
                return
        
        # Initialize progress tracking for setup
        progress = ProgressReporter("Project initialization")
        progress.set_total_steps(7)  # Added ML model setup step
        
        try:
            # Step 1: Create directory structure
            progress.update("Creating project structure", "📁")
            BRASS_DIR.mkdir(exist_ok=True)
            
            # Step 2: Initialize context manager
            progress.update("Initializing context system", "🔧")
            context_manager = ContextManager()
            
            # Step 3: Generate status and context files
            progress.update("Analyzing project structure", "🔍")
            context_manager.update_status()
            context_manager.update_context("Copper Sun Brass Pro initialized - ready to track your development progress")
            
            # Step 4: Generate insights
            progress.update("Generating initial insights", "💡")
            context_manager.generate_insights()
            
            # Step 4.5: Set up ML models (critical for intelligence generation)
            progress.update("Setting up AI models", "🧠")
            self._setup_ml_models()
            
            # Step 5: Save configuration and history
            progress.update("Saving configuration", "⚙️")
            context_manager.add_to_history(
                "Copper Sun Brass Pro activated",
                {
                    "mode": mode,
                    "theme": self.config["user_preferences"].get("visual_theme", "colorful"),
                    "verbosity": self.config["user_preferences"].get("verbosity", "balanced")
                }
            )
            
            # Save initialization timestamp
            import datetime
            self.config["user_preferences"]["setup_date"] = datetime.datetime.now().isoformat()
            self._save_config()
            
            # Step 6: Setup AI instructions
            progress.update("Configuring AI integration", "🤖")
            ai_manager = AIInstructionsManager()
            ai_file, ai_message = ai_manager.ensure_ai_instructions_exist()
            
            progress.complete(f"Copper Sun Brass initialized in {mode} mode")
            
            # START AUTOMATIC MONITORING (NEW SECTION)
            print("\n🚀 Starting automatic monitoring...")
            
            monitoring_success, monitoring_msg = self._start_automatic_monitoring()
            
            if monitoring_success:
                print(f"{monitoring_msg}")
                print("📊 Four AI agents now analyzing your project continuously")
                print("📁 Check .brass/ files for intelligence updates")
                print("🔍 Use 'brass status' to check monitoring status")
            else:
                print(f"{monitoring_msg}")
                print("🔧 Run 'brass status' to check monitoring status")
                print("💡 For troubleshooting, check .brass/ directory for log files")
            
            # Show setup results
            print(f"\n📁 Created .brass/ folder with context files")
            print(f"📝 {ai_message}")
            try:
                print(f"📄 AI instructions: {ai_file.relative_to(Path.cwd())}")
            except ValueError:
                # Handle case where paths don't match
                print(f"📄 AI instructions: {ai_file.name}")
                
        except Exception as e:
            progress.error(f"Initialization failed: {str(e)}")
            print("💡 Check directory permissions and try again")
            return False
        
        # Ask about Claude Code integration (or use provided mode)
        self._handle_claude_code_integration(integration_mode)
    
    def _handle_claude_code_integration(self, integration_mode: Optional[str] = None):
        """Handle Claude Code integration setup with user interaction or flag override.
        
        Args:
            integration_mode: 'claude-code', 'basic', or None for interactive
        """
        if integration_mode == 'claude-code':
            print("\n🎯 Auto-configuring Claude Code integration (--claude-code flag)")
            self._setup_claude_code_integration(automated=True)
        elif integration_mode == 'basic':
            print("\n🎯 Setting up developer mode (--no-integration flag)")
            self._setup_basic_mode(automated=True)
        else:
            # Interactive mode
            print("\n🎯 Claude Code Integration Setup")
            
            # Add attempt limit to prevent infinite loop
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                print("🎯🎯🎯")
                response = input("🎯 **Are you using Claude Code in this project?** (Y/N): ").strip().lower()
                
                if response in ['y', 'yes']:
                    self._setup_claude_code_integration(automated=False)
                    break
                elif response in ['n', 'no']:
                    self._setup_basic_mode(automated=False)
                    break
                elif response in ['quit', 'exit', 'cancel', 'q']:
                    print("Setup cancelled by user.")
                    return
                else:
                    attempts += 1
                    print("Please enter 'y' for yes or 'n' for no (or 'quit' to cancel)")
            
            # Maximum attempts reached
            if attempts >= max_attempts:
                print("❌ Too many invalid responses. Defaulting to basic mode.")
                self._setup_basic_mode(automated=True)
    
    def _setup_claude_code_integration(self, automated: bool = False):
        """Set up Claude Code integration with copy-paste flow.
        
        Args:
            automated: If True, skip user confirmation prompts
        """
        print("\n✅ Auto-configuring Claude Code integration...")
        print("   📝 Created/updated CLAUDE.md with Brass instructions")
        print("   📁 Created .brass/ context directory")
        
        # The integration message
        integration_message = ("Going forward, always read the files in the .brass folder "
                             "for useful project intelligence.")
        
        if automated:
            # Automated mode - no user interaction
            print(f"\n📋 Integration message: \"{integration_message}\"")
            print("🚀 Automated Claude Code setup complete!")
            print("💡 Paste the above message to Claude Code when ready")
            
            # Show enhanced welcome message
            self._show_welcome_message()
        else:
            # Interactive mode - show copy-paste box and wait for confirmation
            print("\n🎯 FINAL STEP - Encourage Claude Code Integration:")
            
            # Try to copy to clipboard
            copied = self._copy_to_clipboard(integration_message)
            self._print_copy_paste_box(integration_message, copied)
            
            # User confirmation loop
            self._wait_for_paste_confirmation()
            
            print("\n🚀 Perfect! Brass + Claude Code integration complete!")
        
        # Show enhanced welcome message after Claude Code setup
        self._show_welcome_message()
    
    def _setup_basic_mode(self, automated: bool = False):
        """Set up developer mode without Claude Code integration.
        
        Args:
            automated: If True, skip user confirmation prompts
        """
        print("\n✅ Brass will run in developer mode")
        print("📁 Created .brass/ directory with context files")
        print("💡 Files update automatically as you work")
        
        if automated:
            # Automated mode - no user interaction
            print("\n✅ Developer mode setup complete! Brass is now analyzing your project...")
            
            # Show enhanced welcome message
            self._show_welcome_message()
        else:
            # Interactive mode - require confirmation
            print("\n🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
            print("🎯")
            print("🎯  ❗ CONFIRMATION REQUIRED:")
            print("🎯")
            print("🎯  Type \"I understand\" to confirm developer mode setup")
            print("🎯")
            print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
            
            # Add attempt limit for consistency with other user interaction loops
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                response = input("\n> ").strip()
                if response.lower() in ["i understand", "i understand."]:
                    break
                elif response.lower() in ["quit", "exit", "cancel", "ctrl+c", "q"]:
                    print("Setup incomplete. Run 'brass init' to resume setup.")
                    return
                else:
                    attempts += 1
                    print("Please type \"I understand\" to continue (or 'quit' to cancel)")
            
            # Maximum attempts reached
            if attempts >= max_attempts:
                print("❌ Too many invalid responses. Setup cancelled.")
                return
            
            print("\n✅ Developer mode setup complete! Brass is now analyzing your project...")
        
        # Show enhanced welcome message after developer mode setup  
        self._show_welcome_message()
        
        print("💡 To add Claude Code integration later: `brass init --claude-code`")
    
    def _wait_for_paste_confirmation(self):
        """Wait for user to confirm they pasted the message to Claude Code."""
        print("\n🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        print("🎯")
        print("🎯  \033[32m❗ CONFIRMATION REQUIRED:\033[0m")
        print("🎯")
        print("🎯  Type \"I pasted it\" after pasting message to Claude Code")
        print("🎯")
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        
        # Add attempt limit for consistency with other user interaction loops
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts:
            response = input("\n> ").strip().lower()
            if response in ["i pasted it", "i pasted it.", "pasted", "copied", "done"]:
                break
            elif response in ["quit", "exit", "cancel", "ctrl+c", "q"]:
                print("Setup incomplete. Run 'brass init' to resume setup.")
                return
            else:
                attempts += 1
                print("Please type \"I pasted it\" after copying the message to Claude Code (or 'quit' to cancel)")
        
        # Maximum attempts reached
        if attempts >= max_attempts:
            print("❌ Too many invalid responses. Setup cancelled.")
            return
    
    def _show_welcome_message(self):
        """Show enhanced welcome message after successful initialization."""
        print("\n🎺 Welcome to Copper Sun Brass Pro!")
        print("\nWhat happens now:")
        print("✅ Brass creates .brass/ directory with project intelligence")
        print("✅ Continuous monitoring and analysis of your codebase begins")
        print("✅ AI recommendations automatically update as you work")
        print("✅ Your development context persists across all sessions")
        print("\n📋 Essential commands:")
        print("• brass status       - Check system status and trial information")
        print("• brass insights     - View project analysis and recommendations")
        print("• brass scout scan   - Analyze your codebase for issues and patterns")
        print("• brass refresh      - Update project intelligence")
        print("• brass --help       - See all available commands and options")
        print("\n🚀 Try it now: Run 'brass insights' to see what Brass found in your project!")
    
    def _cleanup_external_ai_instruction_files(self, description: str = "Cleaning") -> int:
        """Clean AI instruction files OUTSIDE of .brass/ directory.
        
        Args:
            description: Description for user feedback (e.g., "Removing integration from")
            
        Returns:
            int: Number of files cleaned
        """
        ai_manager = AIInstructionsManager()
        found_files = ai_manager.find_ai_instruction_files()
        
        # Filter to exclude .brass/ directory files using proper path analysis
        brass_dir = Path.cwd() / ".brass"
        external_files = [f for f in found_files if not self._is_in_brass_directory(f, brass_dir)]
        
        if not external_files:
            return 0
            
        print(f"\n📄 Found {len(external_files)} external AI instruction file(s) to clean:")
        
        removed_count = 0
        for file in external_files:
            try:
                # Read current content
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if it has Copper Sun Brass section
                if ai_manager.BRASS_SECTION_START in content:
                    # Remove the Brass section
                    start_idx = content.find(ai_manager.BRASS_SECTION_START)
                    end_idx = content.find(ai_manager.BRASS_SECTION_END) + len(ai_manager.BRASS_SECTION_END)
                    
                    if end_idx > start_idx:
                        # Remove section and clean up extra newlines
                        new_content = content[:start_idx] + content[end_idx:]
                        new_content = new_content.replace('\n\n\n', '\n\n')  # Clean up extra newlines
                        
                        with open(file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"  ✅ {file.name}: Removed Copper Sun Brass section")
                        removed_count += 1
                    else:
                        print(f"  ⚠️  {file.name}: Malformed section markers")
                else:
                    print(f"  ℹ️  {file.name}: No Copper Sun Brass section found")
                    
            except Exception as e:
                print(f"  ❌ {file.name}: Error - {str(e)}")
        
        return removed_count
    
    def _is_in_brass_directory(self, file_path: Path, brass_dir: Path) -> bool:
        """Check if a file path is within the .brass directory."""
        try:
            return file_path.resolve().is_relative_to(brass_dir.resolve())
        except (OSError, ValueError):
            # If path resolution fails, use string comparison as fallback
            return '.brass' in str(file_path)
    
    def remove_integration(self):
        """Remove Claude Code integration and return to developer mode."""
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            print("💡 This will set up the .brass/ directory and project monitoring")
            return
        
        print("🗑️  Removing Claude Code integration...")
        
        # Clean up external AI instruction files
        removed_count = self._cleanup_external_ai_instruction_files("Removing Claude Code integration from")
        
        if removed_count > 0:
            print(f"\n✅ Cleaned {removed_count} file(s)")
        else:
            print("\n💡 No external AI instruction files needed cleaning")
        
        # Remove integration marker from config (if we add one in the future)
        # For now, just inform user about .brass/ directory
        
        print("\n📁 .brass/ directory preserved with project context")
        print("💡 Copper Sun Brass will continue running in basic mode")
        print("\n✅ Claude Code integration removed successfully!")
        print("   To re-enable integration: brass init --claude-code")
    
    
    def status(self):
        """Check Copper Sun Brass status."""
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            print("💡 This will set up project monitoring and analysis")
            return
        
        prefs = self.config["user_preferences"]
        
        print(f"🧠 Copper Sun Brass Status\n")
        print(f"Version: {VERSION}")
        # Show license status with more detail
        if prefs.get('license_key'):
            license_type = prefs.get('license_type', 'unknown')
            if license_type == 'developer':
                print(f"License: ✅ Developer (never expires)")
            elif prefs.get('license_expires'):
                # Recalculate days remaining
                from datetime import datetime
                expiry = datetime.fromisoformat(prefs['license_expires'])
                days_left = (expiry - datetime.now()).days
                if days_left > 0:
                    print(f"License: ✅ {license_type.title()} ({days_left} days remaining)")
                else:
                    print(f"License: ❌ Expired")
            else:
                print(f"License: ✅ Activated")
        else:
            print(f"License: ❌ Not activated")
        print(f"Claude API: {'✅ Configured' if prefs.get('claude_api_key') else '❌ Not configured (REQUIRED)'}")
        print(f"Visual Theme: {prefs.get('visual_theme', 'not set')}")
        print(f"Verbosity: {prefs.get('verbosity', 'not set')}")
        
        if prefs.get('setup_date'):
            print(f"Setup Date: {prefs['setup_date'][:10]}")
        
        # Check monitoring status
        print(f"\n📊 Monitoring Status:")
        monitoring_status = self._check_monitoring_status()
        
        if monitoring_status["any_running"]:
            if monitoring_status["type"] == "system_service":
                print("  ✅ System service active - monitoring automatically")
                print("     🔄 Survives reboots and crashes")
            else:
                print("  ✅ Background process active - monitoring until reboot")
                print("     💡 For permanent monitoring, run 'brass init' with administrator privileges")
        else:
            print("  ❌ No monitoring active")
            print("     🚀 Start with: brass init")
            print("     🔧 Or manually: python -m coppersun_brass start")
        
        # Check context files
        print(f"\n📁 Context Files:")
        for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]:
            filepath = BRASS_DIR / filename
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  ✓ {filename} ({size} bytes)")
            else:
                print(f"  ✗ {filename} (missing)")
    
    def stop_monitoring(self):
        """Stop background monitoring process with enhanced error handling."""
        from .background_process_manager import BackgroundProcessManager
        from pathlib import Path
        
        print("🛑 Stopping background monitoring...")
        
        # Check if .brass directory exists
        brass_dir = Path.cwd() / ".brass"
        if not brass_dir.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            return
        
        try:
            manager = BackgroundProcessManager(Path.cwd())
            success, message = manager.stop_background_process()
            
            if success:
                print("✅ Background monitoring stopped")
                print(f"   {message}")
            else:
                print("❌ Failed to stop monitoring")
                print(f"   {message}")
                print("💡 Troubleshooting options:")
                print("   • Check process manually: ps aux | grep coppersun_brass")
                print("   • Force kill: pkill -f coppersun_brass")
                print("   • Remove PID file: rm .brass/monitoring.pid")
                
        except ImportError as e:
            print("❌ Error importing background process manager")
            print(f"   {e}")
            print("💡 Try: brass uninstall && brass reinstall")
        except Exception as e:
            print(f"❌ Unexpected error stopping monitoring: {e}")
            print("💡 Manual cleanup options:")
            print("   • Force kill: pkill -f coppersun_brass")
            print("   • Remove PID file: rm .brass/monitoring.pid")
            print("   • Check logs: brass logs")
    
    def restart_monitoring(self):
        """Restart background monitoring process with enhanced error handling."""
        from .background_process_manager import BackgroundProcessManager
        from pathlib import Path
        
        print("🔄 Restarting background monitoring...")
        
        # Check if .brass directory exists
        brass_dir = Path.cwd() / ".brass"
        if not brass_dir.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            return
        
        try:
            manager = BackgroundProcessManager(Path.cwd())
            
            # First stop if running
            is_running = manager.is_background_running()
            if is_running:
                print("   🛑 Stopping current monitoring...")
                success, message = manager.stop_background_process()
                if not success:
                    print(f"   ⚠️ Stop failed: {message}")
                    print("   ⚠️ Attempting restart anyway...")
                else:
                    print(f"   ✅ {message}")
            else:
                print("   📭 No existing monitoring process found")
            
            # Small delay to ensure cleanup is complete
            import time
            time.sleep(1)
            
            # Start monitoring
            print("   🚀 Starting monitoring...")
            success, message = manager.start_background_process()
            
            if success:
                print("✅ Background monitoring restarted")
                print(f"   {message}")
                print("💡 Check status: brass status")
            else:
                print("❌ Failed to restart monitoring")
                print(f"   {message}")
                print("💡 Troubleshooting options:")
                print("   • Check Python installation: which python")
                print("   • Verify brass installation: brass --version")
                print("   • Reinitialize: brass init")
                print("   • Check logs: brass logs")
                
        except ImportError as e:
            print("❌ Error importing background process manager")
            print(f"   {e}")
            print("💡 Try: brass uninstall && curl -fsSL https://brass.coppersun.dev/setup | bash")
        except Exception as e:
            print(f"❌ Unexpected error restarting monitoring: {e}")
            print("💡 Recovery options:")
            print("   • Clean restart: brass init")
            print("   • Check system resources: df -h && free -h")
            print("   • Verify permissions: ls -la .brass/")
            print("   • Check logs: brass logs")
    
    def show_logs(self, follow: bool = False, lines: int = 50):
        """Show monitoring logs."""
        from pathlib import Path
        import subprocess
        import sys
        
        brass_dir = Path.cwd() / ".brass"
        log_file = brass_dir / "monitoring.log"
        error_log_file = brass_dir / "monitoring.error.log"
        
        if not brass_dir.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            return
        
        print("📋 Monitoring Logs")
        print("=" * 50)
        
        # Check if logs exist
        if not log_file.exists() and not error_log_file.exists():
            print("📭 No log files found")
            print("💡 Background monitoring may not be running")
            print("💡 Try: brass status")
            return
        
        if follow:
            print("🔍 Following log output (Ctrl+C to stop)...")
            if not log_file.exists():
                print("❌ Log file doesn't exist yet")
                print("💡 Start monitoring first: brass restart")
                return
                
            try:
                if sys.platform == "win32":
                    # Windows doesn't have tail -f, use PowerShell
                    try:
                        result = subprocess.run([
                            "powershell", "-Command", 
                            f"Get-Content '{log_file}' -Wait -Tail {lines}"
                        ], timeout=300)  # 5 minute timeout
                        if result.returncode != 0:
                            print(f"❌ PowerShell command failed with exit code {result.returncode}")
                    except subprocess.TimeoutExpired:
                        print("❌ Log following timed out after 5 minutes")
                    except FileNotFoundError:
                        print("❌ PowerShell not found")
                        print("💡 Try: brass logs (without --follow)")
                    except Exception as e:
                        print(f"❌ Error following log: {e}")
                else:
                    # Use tail -f on Unix systems
                    try:
                        result = subprocess.run(["tail", "-f", "-n", str(lines), str(log_file)], timeout=300)
                        if result.returncode != 0:
                            print(f"❌ tail command failed with exit code {result.returncode}")
                    except subprocess.TimeoutExpired:
                        print("❌ Log following timed out after 5 minutes")
                    except FileNotFoundError:
                        print("❌ 'tail' command not found")
                        print("💡 Try: brass logs (without --follow)")
                    except Exception as e:
                        print(f"❌ Error following log: {e}")
            except KeyboardInterrupt:
                print("\n✅ Stopped following logs")
            except PermissionError:
                print("❌ Permission denied reading log file")
                print("💡 Check file permissions: ls -la .brass/")
            except Exception as e:
                print(f"❌ Error following logs: {e}")
                print("💡 Try: brass logs (without --follow)")
        else:
            # Show recent logs
            try:
                if log_file.exists():
                    print(f"\n📄 Standard Output (last {lines} lines):")
                    print("-" * 40)
                    if sys.platform == "win32":
                        try:
                            result = subprocess.run([
                                "powershell", "-Command", 
                                f"Get-Content '{log_file}' -Tail {lines}"
                            ], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0:
                                print(result.stdout)
                            else:
                                print(f"❌ PowerShell command failed: {result.stderr}")
                        except subprocess.TimeoutExpired:
                            print("❌ Command timed out after 30 seconds")
                        except FileNotFoundError:
                            print("❌ PowerShell not found on system")
                        except Exception as e:
                            print(f"❌ Error reading log: {e}")
                    else:
                        try:
                            result = subprocess.run([
                                "tail", "-n", str(lines), str(log_file)
                            ], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0:
                                print(result.stdout)
                            else:
                                print(f"❌ tail command failed: {result.stderr}")
                        except subprocess.TimeoutExpired:
                            print("❌ Command timed out after 30 seconds")
                        except FileNotFoundError:
                            print("❌ 'tail' command not found on system")
                        except Exception as e:
                            print(f"❌ Error reading log: {e}")
                
                if error_log_file.exists():
                    print(f"\n⚠️ Error Output (last {lines} lines):")
                    print("-" * 40)
                    if sys.platform == "win32":
                        try:
                            result = subprocess.run([
                                "powershell", "-Command", 
                                f"Get-Content '{error_log_file}' -Tail {lines}"
                            ], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0:
                                print(result.stdout)
                            else:
                                print(f"❌ PowerShell command failed: {result.stderr}")
                        except subprocess.TimeoutExpired:
                            print("❌ Command timed out after 30 seconds")
                        except FileNotFoundError:
                            print("❌ PowerShell not found on system")
                        except Exception as e:
                            print(f"❌ Error reading error log: {e}")
                    else:
                        try:
                            result = subprocess.run([
                                "tail", "-n", str(lines), str(error_log_file)
                            ], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0:
                                print(result.stdout)
                            else:
                                print(f"❌ tail command failed: {result.stderr}")
                        except subprocess.TimeoutExpired:
                            print("❌ Command timed out after 30 seconds")
                        except FileNotFoundError:
                            print("❌ 'tail' command not found on system")
                        except Exception as e:
                            print(f"❌ Error reading error log: {e}")
                        
            except Exception as e:
                print(f"❌ Error reading logs: {e}")
                print("💡 Check .brass/ directory for log files")
    
    def refresh(self):
        """Force a context refresh."""
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            return
        
        # Initialize progress tracking
        progress = ProgressReporter("Context refresh")
        progress.set_total_steps(4)
        
        try:
            # Use ContextManager to refresh all context files
            context_manager = ContextManager()
            
            # Step 1: Update status
            progress.update("Scanning project structure", "🔍")
            context_manager.update_status(force=True)
            
            # Step 2: Update context
            progress.update("Analyzing codebase patterns", "📊")
            context_manager.update_context()
            
            # Step 3: Generate insights
            progress.update("Generating AI insights", "💡")
            context_manager.generate_insights()
            
            # Step 4: Update history
            progress.update("Updating history log", "📝")
            context_manager.add_to_history("Manual context refresh triggered")
            
            progress.complete("Context refreshed - all files updated")
            
        except Exception as e:
            progress.error(f"Context refresh failed: {str(e)}")
            print("💡 Try: brass status (to check project setup)")
            raise
    
    def insights(self):
        """Display current insights."""
        insights_file = BRASS_DIR / "INSIGHTS.md"
        
        if not insights_file.exists():
            print("❌ No insights available yet")
            print("💡 Run: brass refresh (to generate initial insights)")
            print("💡 Or: brass scout scan (to analyze your codebase)")
            return
        
        # Show progress for file reading (quick operation)
        ProgressReporter.quick_status("Loading current insights", "📖")
        
        try:
            with open(insights_file, 'r') as f:
                content = f.read()
            
            # Quick success message
            ProgressReporter.success("Insights loaded")
            print(content)
            
        except Exception as e:
            print(f"❌ Failed to read insights file: {str(e)}")
            print("💡 Try: brass refresh (to regenerate insights)")
    
    def update_ai_instructions(self):
        """Update AI instruction files with current Copper Sun Brass configuration."""
        print("🔍 Scanning for AI instruction files...")
        
        ai_manager = AIInstructionsManager()
        found_files = ai_manager.find_ai_instruction_files()
        
        if found_files:
            print(f"\n📄 Found {len(found_files)} AI instruction file(s):")
            for file in found_files:
                print(f"  - {file.relative_to(Path.cwd())}")
            
            print("\n🔄 Updating files with Copper Sun Brass configuration...")
            updated_count = 0
            
            for file in found_files:
                success, message = ai_manager.update_ai_instruction_file(file)
                if success:
                    print(f"  ✅ {file.name}: {message}")
                    updated_count += 1
                else:
                    print(f"  ❌ {file.name}: {message}")
            
            print(f"\n✅ Updated {updated_count}/{len(found_files)} files")
        else:
            print("\n📝 No existing AI instruction files found")
            print("Creating new AI instructions file...")
            
            new_file = ai_manager.create_default_ai_instructions()
            print(f"✅ Created: {new_file.relative_to(Path.cwd())}")
        
        print("\n💡 Tell Claude to re-read the AI instructions to apply changes")
    
    def handle_scout_command(self, args):
        """Handle Scout agent commands"""
        if not args.scout_command:
            print("💡 Use 'brass scout --help' to see available Scout commands")
            return
            
        if args.scout_command == 'scan':
            self._scout_scan(args)
        elif args.scout_command == 'status':
            self._scout_status()
        elif args.scout_command == 'analyze':
            self._scout_analyze(args)
        else:
            print(f"❌ PC Load Letter... Just kidding! Unknown Scout command: {args.scout_command}")
    
    def _scout_scan(self, args):
        """Run Scout scan command with enhanced display options"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            from ..core.dcp_adapter import DCPAdapter
            from .display_formatters import ScoutResultsFormatter
            
            print(f"🔍 Scanning {args.path} with Scout Agent...")
            if args.deep:
                print("🧠 Deep analysis enabled")
            
            # Create DCP adapter and Scout agent
            dcp = DCPAdapter()
            scout = ScoutAgent(dcp)
            
            # Run analysis
            results = scout.analyze(args.path, deep_analysis=args.deep)
            
            # Apply file filter if specified
            if args.file:
                results = self._filter_results_by_file(results, args.file)
                print(f"🎯 Results filtered for file: {args.file}")
            
            # Apply content filter
            if args.filter != 'all':
                results = self._filter_results_by_type(results, args.filter)
                print(f"🔍 Results filtered by type: {args.filter}")
            
            # Apply priority filter
            if args.priority != 'all':
                results = self._filter_results_by_priority(results, args.priority)
                print(f"📊 Results filtered by priority: {args.priority}")
            
            # Create formatter and display results
            formatter = ScoutResultsFormatter(detail_level=args.detail, limit=args.limit)
            output = formatter.format_results(results, format_type=args.format)
            print(output)
            
            # Export if requested
            if args.export:
                self._export_scout_results(results, args.export, formatter)
                
        except Exception as e:
            print(f"❌ Scout scan failed: {e}")
            print("💡 Try: brass scout status (to check agent availability)")
            print("💡 Or: brass refresh (to update project context)")
    
    def _scout_status(self):
        """Show Scout agent status"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            print("🔍 Scout Agent Status:")
            print("  ✅ Available")
            print("  📊 Ready for analysis")
            print("  🧠 Deep analysis capabilities enabled")
        except ImportError:
            print("❌ Scout Agent not available")
            print("💡 This may indicate a package installation issue")
            print("💡 Try: pip install --upgrade coppersun-brass")
    
    def _scout_analyze(self, args):
        """Run Scout comprehensive analysis with enhanced display options"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            from ..core.dcp_adapter import DCPAdapter
            from .display_formatters import ScoutResultsFormatter
            
            # Create DCP adapter and Scout agent  
            dcp = DCPAdapter()
            scout = ScoutAgent(dcp)
            
            # Initialize progress tracking for analysis
            # Use lighter analysis for single files to improve performance
            if args.file:
                progress = ProgressReporter(f"Analyzing file: {args.file}")
                progress.set_total_steps(3)
                progress.update("Initializing analysis", "🔍")
                # For single files, use faster analysis unless user specifically wants deep analysis
                analysis_types = {'todo', 'patterns'} if args.detail != 'verbose' else None
                results = scout.analyze(args.file, deep_analysis=(args.detail == 'verbose'), analysis_types=analysis_types)
                progress.update("Processing results", "📊")
            else:
                progress = ProgressReporter(f"Analyzing directory: {args.path}")
                progress.set_total_steps(4)
                progress.update("Discovering files", "📁")
                # For directories, always use deep analysis as expected
                results = scout.analyze(args.path, deep_analysis=True)
                progress.update("Processing results", "📊")
            
            # Apply content filter
            if args.filter != 'all':
                results = self._filter_results_by_type(results, args.filter)
                print(f"🔍 Results filtered by type: {args.filter}")
            
            # Apply priority filter
            if args.priority != 'all':
                results = self._filter_results_by_priority(results, args.priority)
                print(f"📊 Results filtered by priority: {args.priority}")
            
            # Validate results before formatting
            if not results:
                print("⚠️ No analysis results returned")
                return
                
            # Create formatter and display results
            formatter = ScoutResultsFormatter(detail_level=args.detail, limit=args.limit)
            output = formatter.format_results(results, format_type=args.format)
            
            if not output or output.strip() == "":
                print("⚠️ Analysis completed but no findings to display")
            else:
                print(output)
            
            # Complete progress tracking
            progress.update("Generating output", "📝")
            
            # Show analysis metadata
            print(f"\n📊 Analysis duration: {getattr(results, 'analysis_duration', 0):.2f}s")
            
            # Generate DCP observations for AI coordination
            observations = results.to_dcp_observations()
            print(f"📊 Generated {len(observations)} intelligence observations")
            
            # CRITICAL FIX: Store observations and generate output files for Claude Code
            target_path = args.file if args.file else args.path
            storage_result = self._store_observations_and_generate_files(observations, target_path)
            if storage_result:
                print(f"✅ Persistent intelligence ready for Claude Code in .brass/")
            
            # Export if requested
            if args.export:
                self._export_scout_results(results, args.export, formatter)
            
            # Complete the progress reporter
            progress.complete("Analysis completed successfully")
            
        except FileNotFoundError as e:
            print(f"❌ File or directory not found: {e}")
            print("💡 Check that the path exists and is accessible")
        except PermissionError as e:
            print(f"❌ Permission denied: {e}")
            print("💡 Check file permissions")
        except TimeoutError as e:
            print(f"❌ Analysis timed out: {e}")
            print("💡 Try analyzing a smaller directory or single file")
            print("💡 Use: brass scout scan (for faster basic scanning)")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print("💡 Check that the path exists and is accessible")
            print("💡 Try: brass scout scan (for basic scanning instead)")
            import traceback
            print("🔧 Debug information:")
            traceback.print_exc()

    def _store_observations_and_generate_files(self, observations, target_directory):
        """Store observations and generate output files - CRITICAL INTEGRATION FIX"""
        try:
            # Import required components
            from coppersun_brass.config import BrassConfig
            from coppersun_brass.core.dcp_adapter import DCPAdapter
            from coppersun_brass.core.output_generator import OutputGenerator
            
            # Initialize persistence infrastructure
            config = BrassConfig(project_root=target_directory)
            dcp = DCPAdapter()
            
            # CLI commands display results only - no database storage or file generation
            # This prevents interference with background monitoring system
            
            print(f"📊 Analysis duration: {analysis_duration:.2f}s")
            print(f"📊 Generated {len(observations)} intelligence observations")
            
            return {
                'observations_analyzed': len(observations),
                'duration': analysis_duration,
                'display_only': True
            }
            
        except Exception as e:
            print(f"⚠️  Analysis error: {e}")
            print("📊 Analysis failed")
            print("💡 Try: brass scout scan (for lighter analysis)")
            return None

    def _filter_results_by_file(self, results, target_file):
        """Filter Scout results to show only findings from specific file."""
        from pathlib import Path
        target_path = Path(target_file).resolve()
        
        # Filter TODO findings
        filtered_todos = [f for f in results.todo_findings 
                         if hasattr(f, 'file_path') and Path(str(f.file_path)).resolve() == target_path]
        
        # Filter pattern results
        filtered_patterns = [r for r in results.pattern_results 
                           if hasattr(r, 'file_path') and Path(str(r.file_path)).resolve() == target_path]
        
        # Filter AST results
        filtered_ast = [r for r in results.ast_results 
                       if hasattr(r, 'file_path') and Path(str(r.file_path)).resolve() == target_path]
        
        # Create filtered results object
        class FilteredResults:
            def __init__(self):
                self.todo_findings = filtered_todos
                self.pattern_results = filtered_patterns
                self.ast_results = filtered_ast
                self.analysis_duration = getattr(results, 'analysis_duration', 0)
        
        return FilteredResults()
    
    def _filter_results_by_type(self, results, filter_type):
        """Filter Scout results by content type."""
        class FilteredResults:
            def __init__(self):
                if filter_type == 'todos':
                    self.todo_findings = results.todo_findings
                    self.pattern_results = []
                    self.ast_results = []
                elif filter_type == 'security':
                    self.todo_findings = []
                    self.pattern_results = results.pattern_results
                    self.ast_results = []
                elif filter_type == 'quality':
                    self.todo_findings = []
                    self.pattern_results = []
                    self.ast_results = results.ast_results
                else:  # 'all'
                    self.todo_findings = results.todo_findings
                    self.pattern_results = results.pattern_results
                    self.ast_results = results.ast_results
                
                self.analysis_duration = getattr(results, 'analysis_duration', 0)
        
        return FilteredResults()
    
    def _filter_results_by_priority(self, results, priority_level):
        """Filter Scout results by priority level based on confidence scores."""
        def meets_priority(item, level):
            confidence = getattr(item, 'confidence', 0.0)
            if level == 'high':
                return confidence > 0.8
            elif level == 'medium':
                return 0.6 <= confidence <= 0.8
            elif level == 'low':
                return confidence < 0.6
            else:  # 'all'
                return True
        
        # Filter all result types
        filtered_todos = [f for f in results.todo_findings if meets_priority(f, priority_level)]
        filtered_patterns = [r for r in results.pattern_results if meets_priority(r, priority_level)]
        filtered_ast = [r for r in results.ast_results if meets_priority(r, priority_level)]
        
        # Create filtered results object
        class FilteredResults:
            def __init__(self):
                self.todo_findings = filtered_todos
                self.pattern_results = filtered_patterns
                self.ast_results = filtered_ast
                self.analysis_duration = getattr(results, 'analysis_duration', 0)
        
        return FilteredResults()
    
    def _export_scout_results(self, results, export_path, formatter):
        """Export Scout results to file."""
        try:
            from pathlib import Path
            
            export_file = Path(export_path)
            
            # Generate markdown content
            markdown_content = formatter.format_results(results, format_type='markdown')
            
            # Write to file
            export_file.write_text(markdown_content, encoding='utf-8')
            print(f"📄 Results exported to: {export_file}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")

    def legal(self):
        """Show legal documents URL."""
        print("Legal documents: https://brass.coppersun.dev/legal")

    def uninstall(self, credentials_only: bool = False, remove_all: bool = False, dry_run: bool = False):
        """Securely remove Copper Sun Brass credentials and data."""
        print("🗑️  Copper Sun Brass Uninstall")
        
        if remove_all and credentials_only:
            print("❌ Cannot use both --credentials and --all flags")
            return
        
        # Discover files to remove
        files_to_remove = []
        
        # 1. Global config file (new location)
        global_config = Path.home() / ".brass" / "config.json"
        if global_config.exists():
            files_to_remove.append(("Global config (API keys, license)", global_config))
        
        # 1a. Legacy global config file (old location)
        legacy_global_config = Path.home() / ".brass" / "config.json"
        if legacy_global_config.exists():
            files_to_remove.append(("Legacy global config", legacy_global_config))
        
        # 2. Global directories (if removing all)
        global_brass_dir = Path.home() / ".brass"
        if remove_all and global_brass_dir.exists():
            files_to_remove.append(("Global .brass directory", global_brass_dir))
        
        # 3. Find project .brass directories (if removing all)
        if remove_all:
            # Scan common project locations
            search_paths = [
                Path.home() / "Desktop",
                Path.home() / "Documents", 
                Path.home() / "Projects",
                Path.cwd().parent if Path.cwd().name != Path.home().name else Path.cwd(),
                Path.cwd()  # Also search current directory recursively
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    try:
                        for brass_dir in search_path.rglob(".brass"):
                            if brass_dir.is_dir():
                                files_to_remove.append(("Project .brass directory", brass_dir))
                    except (PermissionError, OSError):
                        # Skip directories we can't access
                        continue
        
        # 4. Current project .brass directory (if in a project)
        current_brass = BRASS_DIR
        if current_brass.exists():
            if remove_all:
                files_to_remove.append(("Current project .brass directory", current_brass))
            elif not credentials_only:
                # Default mode: remove config but keep project data
                current_config = current_brass / "config.json" 
                if current_config.exists():
                    files_to_remove.append(("Current project config", current_config))
        
        # 5. Cached credentials (if any)
        cache_locations = [
            Path.home() / ".cache" / "brass",
            Path.home() / ".local" / "share" / "brass"
        ]
        for cache_dir in cache_locations:
            if cache_dir.exists():
                if credentials_only:
                    # Only remove credential files from cache
                    for cred_file in cache_dir.glob("*credential*"):
                        files_to_remove.append(("Cached credentials", cred_file))
                elif remove_all:
                    files_to_remove.append(("Cache directory", cache_dir))
        
        if not files_to_remove:
            print("✅ No Copper Sun Brass files found to remove")
            return
        
        # Show what will be removed
        print(f"\n📋 Found {len(files_to_remove)} item(s) to remove:")
        for description, path in files_to_remove:
            status = "📁" if path.is_dir() else "📄"
            print(f"  {status} {description}: {path}")
        
        if dry_run:
            print("\n🔍 Dry run complete - no files were actually removed")
            return
        
        # Confirm with user
        if remove_all:
            print("\n🚨 WARNING: --all will remove ALL Copper Sun Brass data including project intelligence!")
            print("💡 Project .brass/ directories contain your work and insights")
        elif credentials_only:
            print("\n🔒 Removing only credentials and license data")
        else:
            print("\n🔒 Removing credentials and user config (keeping project data)")
        
        print("🎯🎯🎯")
        confirm = input("🎯 Type 'yes' to confirm removal: ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Uninstall cancelled")
            return
        
        # Stop background processes system-wide (if removing all)
        if remove_all:
            print("\n🛑 Stopping background monitoring processes...")
            
            # Import BackgroundProcessManager locally to avoid circular imports
            try:
                from .background_process_manager import BackgroundProcessManager
            except ImportError:
                try:
                    from background_process_manager import BackgroundProcessManager
                except Exception as e:
                    print(f"⚠️  Could not import BackgroundProcessManager: {e}")
                    BackgroundProcessManager = None
            except Exception as e:
                print(f"⚠️  Could not import BackgroundProcessManager: {e}")
                BackgroundProcessManager = None
                
            if BackgroundProcessManager:
                # Find and terminate processes from ALL projects system-wide
                processes_found = 0
                processes_stopped = 0
                failed_projects = []
                
                # Search paths for .brass directories (same as file discovery)
                search_paths = [
                    Path.home() / "Desktop",
                    Path.home() / "Documents", 
                    Path.home() / "Projects",
                    Path.cwd().parent if Path.cwd().name != Path.home().name else Path.cwd(),
                    Path.cwd()  # Also search current directory recursively  
                ]
                
                # Remove duplicates and ensure they exist
                unique_paths = []
                for path in search_paths:
                    if path.exists() and path not in unique_paths:
                        unique_paths.append(path)
                
                for search_path in unique_paths:
                    try:
                        for brass_dir in search_path.rglob(".brass"):
                            if brass_dir.is_dir():
                                project_root = brass_dir.parent
                                pid_file = brass_dir / "monitoring.pid"
                                
                                if pid_file.exists():
                                    processes_found += 1
                                    manager = BackgroundProcessManager(project_root)
                                    success, message = manager.stop_background_process()
                                    
                                    if success:
                                        processes_stopped += 1
                                        print(f"  ✅ {project_root.name}: {message}")
                                    else:
                                        print(f"  ⚠️  {project_root.name}: {message}")
                                        # Store failed projects for detailed guidance
                                        failed_projects.append((project_root.name, project_root, message))
                                        
                    except (PermissionError, OSError) as e:
                        # Skip directories we can't access
                        continue
                    except Exception as e:
                        print(f"  ⚠️  Error scanning {search_path}: {e}")
                        continue
                
                # Summary message
                if processes_found == 0:
                    print("  ℹ️  No background processes found")
                elif processes_stopped == processes_found:
                    print(f"  ✅ Successfully stopped all {processes_stopped} background process(es)")
                else:
                    print(f"  ⚠️  Stopped {processes_stopped}/{processes_found} background process(es)")
                    
                    # Provide detailed guidance for failed processes
                    if failed_projects:
                        print(f"\n🚨 {len(failed_projects)} process(es) could not be stopped automatically:")
                        for project_name, project_root, error_msg in failed_projects:
                            print(f"\n📁 Project: {project_name}")
                            print(f"   Location: {project_root}")
                            print(f"   Issue: {error_msg}")
                            
                        print("\n💡 Manual cleanup options:")
                        print("   Option 1 - Kill all Brass processes:")
                        print("     pkill -f coppersun_brass")
                        print("     # Or on Windows: taskkill /F /IM python.exe /FI \"COMMANDLINE eq *coppersun_brass*\"")
                        
                        print("\n   Option 2 - Kill specific processes by project:")
                        for project_name, project_root, _ in failed_projects:
                            pid_file = project_root / ".brass" / "monitoring.pid"
                            if pid_file.exists():
                                try:
                                    pid = pid_file.read_text().strip()
                                    print(f"     # {project_name}: kill {pid}  # Or on Windows: taskkill /PID {pid} /F")
                                except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError) as e:
                                    print(f"     # {project_name}: Check {pid_file} for PID, then kill <PID> (Error: {e})")
                            else:
                                print(f"     # {project_name}: No PID file found - process may already be dead")
                                
                        print("\n   Option 3 - Clean up PID files manually:")
                        for project_name, project_root, _ in failed_projects:
                            pid_file = project_root / ".brass" / "monitoring.pid"
                            print(f"     rm \"{pid_file}\"  # Remove stale PID file for {project_name}")
                            
                        print("\n   After manual cleanup, verify with:")
                        print("     ps aux | grep coppersun_brass  # Should show no processes")
                        
            else:
                print("  ⚠️  Could not load process management - background processes may remain running")
                print("\n💡 Manual cleanup options:")
                print("   # Kill all Brass processes:")
                print("   pkill -f coppersun_brass")
                print("   # Or on Windows: taskkill /F /IM python.exe /FI \"COMMANDLINE eq *coppersun_brass*\"")
                print("\n   # Verify cleanup:")
                print("   ps aux | grep coppersun_brass  # Should show no processes")
        
        # Clean up external AI instruction files (if removing all)
        if remove_all:
            print("\n🧹 Cleaning up external AI instruction files...")
            ai_removed_count = self._cleanup_external_ai_instruction_files("Removing Brass integration from")
            
            if ai_removed_count > 0:
                print(f"✅ Cleaned {ai_removed_count} external AI instruction file(s)")
            else:
                print("ℹ️  No external AI instruction files needed cleaning")
        
        # Remove files
        removed_count = 0
        for description, path in files_to_remove:
            try:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  ✅ Removed: {description}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {description}: {e}")
        
        print(f"\n✅ Uninstall complete! Removed {removed_count}/{len(files_to_remove)} items")
        
        if remove_all:
            print("🎺 All Copper Sun Brass data has been removed")
        elif credentials_only:
            print("🎺 Credentials removed - project data preserved")  
        else:
            print("🎺 User credentials removed - project intelligence preserved")
        
        print("💡 To reinstall: curl -fsSL https://brass.coppersun.dev/setup | bash")
    
    def generate_completion(self, shell: str = 'bash'):
        """Generate shell completion script for brass commands."""
        
        if shell == 'bash':
            script = '''_brass_completion() {
    local cur prev commands config_keys
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    commands="activate generate-trial config init status stat refresh insights insight update-ai remove-integration scout uninstall cleanup completion help"
    
    # Configuration keys
    config_keys="visual_theme verbosity claude_api_key user_name"
    
    case ${prev} in
        brass)
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        config)
            COMPREPLY=( $(compgen -W "set global local get list" -- ${cur}) )
            return 0
            ;;
        set)
            COMPREPLY=( $(compgen -W "${config_keys}" -- ${cur}) )
            return 0
            ;;
        global)
            COMPREPLY=( $(compgen -W "set" -- ${cur}) )
            return 0
            ;;
        local)
            COMPREPLY=( $(compgen -W "set" -- ${cur}) )
            return 0
            ;;
        get)
            COMPREPLY=( $(compgen -W "${config_keys}" -- ${cur}) )
            return 0
            ;;
        scout)
            COMPREPLY=( $(compgen -W "status scan analyze" -- ${cur}) )
            return 0
            ;;
        uninstall|cleanup)
            COMPREPLY=( $(compgen -W "--credentials --all --dry-run" -- ${cur}) )
            return 0
            ;;
        completion)
            COMPREPLY=( $(compgen -W "--shell" -- ${cur}) )
            return 0
            ;;
        --shell)
            COMPREPLY=( $(compgen -W "bash zsh" -- ${cur}) )
            return 0
            ;;
        visual_theme)
            COMPREPLY=( $(compgen -W "colorful professional monochrome" -- ${cur}) )
            return 0
            ;;
        verbosity)
            COMPREPLY=( $(compgen -W "detailed balanced minimal" -- ${cur}) )
            return 0
            ;;
        init)
            case ${cur} in
                --*)
                    COMPREPLY=( $(compgen -W "--mode --claude-code --no-integration" -- ${cur}) )
                    ;;
            esac
            return 0
            ;;
        scan|analyze)
            case ${cur} in
                --*)
                    COMPREPLY=( $(compgen -W "--path --deep" -- ${cur}) )
                    ;;
            esac
            return 0
            ;;
    esac
    
    # Handle flags for specific commands
    case ${COMP_WORDS[1]} in
        init)
            case ${cur} in
                --*)
                    COMPREPLY=( $(compgen -W "--mode --claude-code --no-integration" -- ${cur}) )
                    ;;
            esac
            ;;
        scout)
            if [[ ${COMP_WORDS[2]} == "scan" || ${COMP_WORDS[2]} == "analyze" ]]; then
                case ${cur} in
                    --*)
                        COMPREPLY=( $(compgen -W "--path --deep" -- ${cur}) )
                        ;;
                esac
            fi
            ;;
        uninstall|cleanup)
            case ${cur} in
                --*)
                    COMPREPLY=( $(compgen -W "--credentials --all --dry-run" -- ${cur}) )
                    ;;
            esac
            ;;
    esac
}

complete -F _brass_completion brass'''
            
        elif shell == 'zsh':
            script = '''#compdef brass

_brass() {
    local context state line
    
    _arguments -C \\
        '1: :->commands' \\
        '*: :->args'
        
    case $state in
        commands)
            _values 'brass commands' \\
                'activate[Activate license key]' \\
                'generate-trial[Start free 15-day trial]' \\
                'config[Manage settings and API keys]' \\
                'init[Initialize project]' \\
                'status[Check system status]' \\
                'stat[Check system status (alias)]' \\
                'refresh[Update project analysis]' \\
                'insights[Show AI recommendations]' \\
                'insight[Show AI recommendations (alias)]' \\
                'update-ai[Update AI instruction files]' \\
                'remove-integration[Remove Claude Code integration]' \\
                'scout[Code analysis agent]' \\
                'uninstall[Remove Brass securely]' \\
                'cleanup[Remove Brass securely (alias)]' \\
                'completion[Generate shell completion script]' \\
                'help[Show help information]'
            ;;
        args)
            case $words[2] in
                config)
                    _values 'config commands' \\
                        'set[Set configuration value]' \\
                        'global[Global configuration]' \\
                        'local[Local configuration]' \\
                        'get[Get configuration value]' \\
                        'list[List all configuration]'
                    ;;
                scout)
                    _values 'scout commands' \\
                        'status[Scout agent status]' \\
                        'scan[Scan for code issues]' \\
                        'analyze[Deep code analysis]'
                    ;;
                uninstall|cleanup)
                    _arguments \\
                        '--credentials[Remove only credentials]' \\
                        '--all[Remove everything]' \\
                        '--dry-run[Preview removal]'
                    ;;
                completion)
                    _arguments \\
                        '--shell[Shell type]:shell:(bash zsh)'
                    ;;
                init)
                    _arguments \\
                        '--mode[Initialization mode]:mode:' \\
                        '--claude-code[Auto-configure for Claude Code]' \\
                        '--no-integration[Developer mode only]'
                    ;;
            esac
            
            # Handle nested commands
            if [[ $words[2] == "config" && $words[3] == "set" ]]; then
                case $CURRENT in
                    4)
                        _values 'configuration keys' \\
                            'visual_theme' \\
                            'verbosity' \\
                            'claude_api_key' \\
                            'user_name'
                        ;;
                    5)
                        case $words[4] in
                            visual_theme)
                                _values 'visual themes' 'colorful' 'professional' 'monochrome'
                                ;;
                            verbosity)
                                _values 'verbosity levels' 'detailed' 'balanced' 'minimal'
                                ;;
                        esac
                        ;;
                esac
            fi
            
            if [[ $words[2] == "scout" && ($words[3] == "scan" || $words[3] == "analyze") ]]; then
                _arguments \\
                    '--path[Directory path]:path:_directories' \\
                    '--deep[Enable deep analysis]'
            fi
            ;;
    esac
}

_brass'''
        
        else:
            print(f"❌ Unsupported shell: {shell}")
            print("💡 Supported shells: bash, zsh")
            return
        
        # Display installation instructions
        print(f"# {shell.title()} completion for Copper Sun Brass")
        print(f"# Generated by brass completion --shell {shell}")
        print()
        
        if shell == 'bash':
            install_path = "~/.local/share/bash-completion/completions/brass"
            reload_cmd = "source ~/.bashrc"
        else:  # zsh
            install_path = "~/.local/share/zsh/site-functions/_brass"
            reload_cmd = "source ~/.zshrc"
        
        print(f"# Installation:")
        print(f"# 1. Save this script to: {install_path}")
        print(f"# 2. Restart your shell or run: {reload_cmd}")
        print(f"# 3. Test with: brass <TAB>")
        print()
        print("# Script:")
        print(script)
    
    def _start_automatic_monitoring(self) -> Tuple[bool, str]:
        """Start automatic monitoring with maximum reliability."""
        
        try:
            # 🔧 CRITICAL FIX: Use our main API to start monitoring
            from ..core.brass import Brass
            from ..config import BrassConfig
            
            # Initialize Brass with current project
            config = BrassConfig(Path.cwd())
            brass = Brass(Path.cwd(), config)
            
            # Start monitoring using our main API
            monitoring_started = brass.start_monitoring()
            
            if monitoring_started:
                # Background monitoring is now running - initial analysis will happen automatically
                return True, "✅ Automatic monitoring started - background analysis will populate .brass files"
            else:
                return False, "❌ Failed to start automatic monitoring"
                
        except Exception as e:
            # Fallback to original system service approach
            try:
                # Initialize managers
                service_manager = SystemServiceManager(Path.cwd())
                background_manager = BackgroundProcessManager(Path.cwd())
                
                # Check if already running
                if service_manager.is_service_running():
                    return True, "✅ System service already running"
                elif background_manager.is_background_running():
                    return True, "✅ Background process already running"
                
                # Try system service first (100% reliability)
                service_success, service_msg = service_manager.install_service()
                if service_success:
                    return True, f"✅ System service installed - runs automatically forever\n   {service_msg}"
                
                # Fallback to background process (80% reliability)
                bg_success, bg_msg = background_manager.start_background_process()
                if bg_success:
                    return True, f"✅ Background monitoring started\n   {bg_msg}\n   💡 For permanent setup across reboots, run brass init with administrator privileges"
                
                # Both failed
                return False, f"❌ Automatic startup failed\n   Service: {service_msg}\n   Background: {bg_msg}\n   💡 Start manually with: python -m coppersun_brass start"
                
            except Exception as fallback_error:
                return False, f"❌ All monitoring methods failed\n   Main API: {e}\n   Fallback: {fallback_error}\n   💡 Start manually with: python -m coppersun_brass start"
    
    def _check_monitoring_status(self) -> Dict[str, Any]:
        """Check current monitoring status."""
        service_manager = SystemServiceManager(Path.cwd())
        background_manager = BackgroundProcessManager(Path.cwd())
        
        status = {
            "service_running": service_manager.is_service_running(),
            "background_running": background_manager.is_background_running(),
            "any_running": False,
            "type": "none"
        }
        
        if status["service_running"]:
            status["any_running"] = True
            status["type"] = "system_service"
        elif status["background_running"]:
            status["any_running"] = True
            status["type"] = "background_process"
        
        return status

    def _setup_ml_models(self):
        """Set up pure Python ML engine (no external dependencies)."""
        try:
            from ..ml.pure_python_ml import get_pure_python_ml_engine
            import logging
            
            # Test pure Python ML engine
            ml_logger = logging.getLogger('coppersun_brass.ml')
            original_level = ml_logger.level
            ml_logger.setLevel(logging.WARNING)
            
            try:
                # Initialize pure Python ML engine
                engine = get_pure_python_ml_engine()
                print("   ✅ Pure Python ML ready (2.5MB - zero dependencies!)")
                print("   🩸 BLOOD OATH: No external downloads needed")
            except Exception as e:
                print(f"   💀 FATAL: Pure Python ML failed: {e}")
                print("   🩸 This violates ML mandatory requirement")
            finally:
                # Restore logging level
                ml_logger.setLevel(original_level)
                
        except ImportError:
            print("   💀 FATAL: Pure Python ML not available")
            print("   🩸 BLOOD OATH VIOLATION: Pure Python ML should always work")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Copper Sun Brass - AI Development Intelligence System (Background Monitoring)",
        epilog="For more information, visit https://brass.coppersun.dev"
    )
    
    parser.add_argument('--version', action='version', version=f'Copper Sun Brass {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Commands in alphabetical order (excluding aliases from help display)
    
    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Enter your paid license key')
    activate_parser.add_argument('license_key', help='Your Copper Sun Brass license key (XXXX-XXXX-XXXX-XXXX)')
    
    # Config command  
    config_parser = subparsers.add_parser('config', help='Manage settings and API keys (use without value for secure API key input)')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    
    # Config set command (defaults to global)
    config_set_parser = config_subparsers.add_parser('set', help='Set a configuration value (global scope)')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', nargs='?', help='Configuration value (will prompt securely for API keys if omitted)')
    
    # Config global set command
    config_global_parser = config_subparsers.add_parser('global', help='Global configuration commands')
    config_global_subparsers = config_global_parser.add_subparsers(dest='global_command')
    
    config_global_set_parser = config_global_subparsers.add_parser('set', help='Set a global configuration value')
    config_global_set_parser.add_argument('key', help='Configuration key')
    config_global_set_parser.add_argument('value', nargs='?', help='Configuration value (will prompt securely for API keys if omitted)')
    
    # Config local set command
    config_local_parser = config_subparsers.add_parser('local', help='Local (project) configuration commands')
    config_local_subparsers = config_local_parser.add_subparsers(dest='local_command')
    
    config_local_set_parser = config_local_subparsers.add_parser('set', help='Set a local configuration value')
    config_local_set_parser.add_argument('key', help='Configuration key')
    config_local_set_parser.add_argument('value', nargs='?', help='Configuration value (will prompt securely for API keys if omitted)')
    
    # Config get command
    config_get_parser = config_subparsers.add_parser('get', help='Get a configuration value')
    config_get_parser.add_argument('key', help='Configuration key')
    
    # Config list command
    config_subparsers.add_parser('list', help='List all configuration values')
    
    # Config audit command - NEW SECURITY FEATURE
    config_subparsers.add_parser('audit', help='Show API key locations and security status')
    
    # Config show command - NEW FEATURE
    config_subparsers.add_parser('show', help='Display current configuration hierarchy')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Copper Sun Brass in current project')
    init_parser.add_argument('--mode', default='claude-companion', 
                            help='Initialization mode (default: claude-companion)')
    init_parser.add_argument('--claude-code', action='store_true',
                            help='Skip questions and auto-configure for Claude Code integration')
    init_parser.add_argument('--no-integration', action='store_true',
                            help='Skip questions and set up developer mode (no Claude Code integration)')
    
    # Insights command
    subparsers.add_parser('insights', help='Show AI recommendations for your project')
    
    # Legal command
    subparsers.add_parser('legal', help='Show legal documents URL')
    
    # Refresh command
    subparsers.add_parser('refresh', help='Update project analysis')
    
    # Remove integration command
    subparsers.add_parser('remove-integration', help='Remove Claude Code integration and return to developer mode')
    
    # Scout commands - Hidden from help (background monitoring handles analysis automatically)
    scout_parser = subparsers.add_parser('scout', add_help=False)
    scout_subparsers = scout_parser.add_subparsers(dest='scout_command', help='''
Commands:
  scan      Quick scan for TODOs and basic issues (recommended)
  analyze   Deep analysis with AST parsing (WARNING: may timeout on large codebases)
  status    Show Scout agent availability

Use 'brass scout <command> --help' for detailed command options and examples.

Examples:
  brass scout scan                    # Quick scan of current directory
  brass scout scan --limit 10        # Show only 10 results per category
  brass scout analyze --file app.py  # Deep analysis of single file
  brass scout status                  # Check if Scout is working''')
    
    scout_scan_parser = scout_subparsers.add_parser('scan', help='Quick scan for code issues and patterns')
    scout_scan_parser.description = '''
Quick scan for code issues and patterns

brass scout scan options:
  brass scout scan                                    # Basic scan of current directory
  brass scout scan --path src                        # Scan specific directory
  brass scout scan --limit 5                         # Show only 5 items per category
  brass scout scan --detail summary                  # Show just counts and basics
  brass scout scan --detail verbose                  # Show full details with metadata
  brass scout scan --format json                     # Output as JSON data
  brass scout scan --format markdown                 # Output as formatted text
  brass scout scan --file app.py                     # Analyze single file only
  brass scout scan --filter todos                    # Show only TODO items
  brass scout scan --filter security                 # Show only security issues
  brass scout scan --priority high                   # Show only high-priority items
  brass scout scan --export results.txt              # Export results to file
  brass scout scan --deep                            # Enable deep analysis (WARNING: may timeout)
  brass scout scan --path src --limit 5              # Scan src/ directory, show 5 items
  brass scout scan --filter todos --priority high    # High-priority TODOs only
  brass scout scan --format json --export results.json  # Export to JSON file'''
    scout_scan_parser.add_argument('--path', default='.', help='Directory to scan (default: current)')
    scout_scan_parser.add_argument('--deep', action='store_true', help='Enable deep AST analysis (WARNING: may timeout on large codebases)')
    scout_scan_parser.add_argument('--detail', choices=['summary', 'normal', 'verbose'], default='normal', 
                                 help='Output detail: summary=counts only, normal=enhanced display, verbose=full details')
    scout_scan_parser.add_argument('--limit', type=int, default=20, help='Max items to display per category (default: 20)')
    scout_scan_parser.add_argument('--format', choices=['table', 'json', 'markdown'], default='table', 
                                 help='Output format: table=console display, json=structured data, markdown=formatted text')
    scout_scan_parser.add_argument('--file', help='Analyze specific file only')
    scout_scan_parser.add_argument('--filter', choices=['todos', 'security', 'quality', 'all'], default='all',
                                 help='Filter by type: todos=TODO comments, security=security issues, quality=code quality, all=everything')
    scout_scan_parser.add_argument('--priority', choices=['high', 'medium', 'low', 'all'], default='all',
                                 help='Filter by priority: high/medium/low priority items only, all=everything')
    scout_scan_parser.add_argument('--export', help='Export results to file (markdown format)')
    
    scout_status_parser = scout_subparsers.add_parser('status', help='Show Scout agent status and capabilities')
    scout_status_parser.description = '''
Show Scout agent status and capabilities

brass scout status options:
  brass scout status                                    # Show Scout agent availability and capabilities
  
This command displays:
- Whether Scout agent is available and functional
- Current configuration and capabilities
- Recent analysis statistics
- System resource usage information'''
    
    scout_analyze_parser = scout_subparsers.add_parser('analyze', help='Deep code analysis with AST parsing (WARNING: may timeout on large codebases)')
    scout_analyze_parser.description = '''
Deep code analysis with AST parsing (WARNING: may timeout on large codebases)

brass scout analyze options:
  brass scout analyze                                   # Deep analysis of current directory (may timeout)
  brass scout analyze --path src                       # Deep analysis of specific directory
  brass scout analyze --file app.py                    # Deep analysis of single file only (recommended)
  brass scout analyze --limit 5                        # Show only 5 items per category
  brass scout analyze --detail summary                 # Show just counts and basics
  brass scout analyze --detail verbose                 # Show full details with metadata
  brass scout analyze --format json                    # Output as JSON data
  brass scout analyze --format markdown                # Output as formatted text
  brass scout analyze --filter todos                   # Show only TODO items
  brass scout analyze --filter security                # Show only security issues
  brass scout analyze --priority high                  # Show only high-priority items
  brass scout analyze --export results.txt             # Export results to file
  brass scout analyze --file main.py --format json    # Analyze single file, output JSON
  brass scout analyze --path src --limit 3             # Analyze src/ directory, show 3 items

WARNING: This command uses deep AST parsing and may timeout on large codebases.
For faster results, use 'brass scout scan' or specify a single file with --file.'''
    scout_analyze_parser.add_argument('--path', default='.', help='Directory to analyze (default: current)')
    scout_analyze_parser.add_argument('--detail', choices=['summary', 'normal', 'verbose'], default='normal',
                                    help='Output detail: summary=counts only, normal=enhanced display, verbose=full details')
    scout_analyze_parser.add_argument('--limit', type=int, default=20, help='Max items to display per category (default: 20)')
    scout_analyze_parser.add_argument('--format', choices=['table', 'json', 'markdown'], default='table',
                                    help='Output format: table=console display, json=structured data, markdown=formatted text')
    scout_analyze_parser.add_argument('--file', help='Analyze specific file only')
    scout_analyze_parser.add_argument('--filter', choices=['todos', 'security', 'quality', 'all'], default='all',
                                    help='Filter by type: todos=TODO comments, security=security issues, quality=code quality, all=everything')
    scout_analyze_parser.add_argument('--priority', choices=['high', 'medium', 'low', 'all'], default='all',
                                    help='Filter by priority: high/medium/low priority items only, all=everything')
    scout_analyze_parser.add_argument('--export', help='Export results to file (markdown format)')
    
    # Status command
    subparsers.add_parser('status', help='Check setup and trial status')
    
    # Process control commands for background monitoring
    subparsers.add_parser('stop', help='Stop background monitoring')
    subparsers.add_parser('restart', help='Restart background monitoring')
    logs_parser = subparsers.add_parser('logs', help='Show monitoring logs')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow log output in real-time')
    logs_parser.add_argument('--lines', '-n', type=int, default=50, help='Number of lines to show (default: 50)')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Securely remove Copper Sun Brass credentials and data (use --all to remove everything)')
    uninstall_parser.add_argument('--credentials', action='store_true', 
                                 help='Remove only API keys and license data (keep project files)')
    uninstall_parser.add_argument('--all', action='store_true',
                                 help='Remove everything including .brass/ project directories')
    uninstall_parser.add_argument('--dry-run', action='store_true',
                                 help='Show what would be removed without actually removing it')
    
    # Migrate command - Hidden from help (solves non-existent problem - no legacy installations)
    migrate_parser = subparsers.add_parser('migrate', add_help=False)
    migrate_parser.add_argument('--dry-run', action='store_true',
                               help='Show what would be migrated without making changes')
    
    # Update AI instructions command
    subparsers.add_parser('update-ai', help='Update AI instruction files with Copper Sun Brass configuration')
    
    # Hidden completion command (functional but not advertised)
    completion_parser = subparsers.add_parser('completion', add_help=False)
    completion_parser.add_argument('--shell', choices=['bash', 'zsh'], default='bash')
    
    # Hidden generate-trial command (for testing/internal use)
    generate_trial_parser = subparsers.add_parser('generate-trial', add_help=False)
    generate_trial_parser.add_argument('--activate', action='store_true', help='Automatically activate the trial license')
    generate_trial_parser.add_argument('--days', type=int, default=15, help='Trial duration in days (default: 15)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = BrassCLI()
    
    # Handle commands
    if args.command == 'activate':
        cli.activate(args.license_key)
    elif args.command == 'generate-trial':
        cli.generate_trial(args.days, args.activate)
    elif args.command == 'config':
        if args.config_command == 'set':
            cli.config_set(args.key, args.value, scope='global')
        elif args.config_command == 'global' and args.global_command == 'set':
            cli.config_set(args.key, args.value, scope='global')
        elif args.config_command == 'local' and args.local_command == 'set':
            cli.config_set(args.key, args.value, scope='local')
        elif args.config_command == 'get':
            cli.config_get(args.key)
        elif args.config_command == 'list':
            cli.config_list()
        elif args.config_command == 'audit':
            cli.config_audit()
        elif args.config_command == 'show':
            cli.config_show()
        else:
            print("❌ Config command not recognized")
            print("💡 Available commands: set, global, local, get, list, audit, show")
            print("💡 Example: brass config set visual_theme colorful")
            print("💡 Security: brass config audit (show API key locations)")
    elif args.command == 'init':
        # Handle conflicting flags
        if args.claude_code and args.no_integration:
            print("❌ Conflicting flags: Cannot use both --claude-code and --no-integration")
            print("💡 Use one flag or neither (for interactive mode)")
            sys.exit(1)
        
        # Determine integration mode from flags
        integration_mode = None
        if args.claude_code:
            integration_mode = 'claude-code'
        elif args.no_integration:
            integration_mode = 'basic'
        
        cli.init(args.mode, integration_mode=integration_mode)
    elif args.command == 'status':
        cli.status()
    elif args.command == 'stop':
        cli.stop_monitoring()
    elif args.command == 'restart':
        cli.restart_monitoring()
    elif args.command == 'logs':
        cli.show_logs(follow=args.follow, lines=args.lines)
    elif args.command == 'refresh':
        cli.refresh()
    elif args.command == 'insights':
        cli.insights()
    elif args.command == 'migrate':
        cli.migrate_configurations(dry_run=args.dry_run)
    elif args.command == 'update-ai':
        cli.update_ai_instructions()
    elif args.command == 'remove-integration':
        cli.remove_integration()
    elif args.command == 'uninstall':
        cli.uninstall(
            credentials_only=args.credentials,
            remove_all=args.all,
            dry_run=args.dry_run
        )
    elif args.command == 'scout':
        cli.handle_scout_command(args)
    elif args.command == 'legal':
        cli.legal()
    elif args.command == 'completion':
        cli.generate_completion(args.shell)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()