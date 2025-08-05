"""
Rich Terminal Display for MassGen Coordination

Enhanced terminal interface using Rich library with live updates,
beautiful formatting, code highlighting, and responsive layout.
"""

import re
import time
import threading
import asyncio
import os
import sys
import select
import tty
import termios
import subprocess
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any
from .terminal_display import TerminalDisplay

try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.status import Status
    from rich.box import ROUNDED, HEAVY, DOUBLE

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

    # Provide dummy classes when Rich is not available
    class Layout:
        pass

    class Panel:
        pass

    class Console:
        pass

    class Live:
        pass

    class Columns:
        pass

    class Table:
        pass

    class Syntax:
        pass

    class Text:
        pass

    class Align:
        pass

    class Progress:
        pass

    class SpinnerColumn:
        pass

    class TextColumn:
        pass

    class Status:
        pass

    ROUNDED = HEAVY = DOUBLE = None


class RichTerminalDisplay(TerminalDisplay):
    """Enhanced terminal display using Rich library for beautiful formatting."""

    def __init__(self, agent_ids: List[str], **kwargs):
        """Initialize rich terminal display.

        Args:
            agent_ids: List of agent IDs to display
            **kwargs: Additional configuration options
                - theme: Color theme ('dark', 'light', 'cyberpunk') (default: 'dark')
                - refresh_rate: Display refresh rate in Hz (default: 4)
                - enable_syntax_highlighting: Enable code syntax highlighting (default: True)
                - max_content_lines: Base lines per agent column before scrolling (default: 8)
                - show_timestamps: Show timestamps for events (default: True)
                - enable_status_jump: Enable jumping to latest status when agent status changes (default: True)
                - truncate_web_search_on_status_change: Truncate web search content when status changes (default: True)
                - max_web_search_lines_on_status_change: Max web search lines to keep on status changes (default: 3)
                - enable_flush_output: Enable flush output for final answer display (default: True)
                - flush_char_delay: Delay between characters in flush output (default: 0.03)
                - flush_word_delay: Extra delay after punctuation in flush output (default: 0.08)
        """
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library is required for RichTerminalDisplay. "
                "Install with: pip install rich"
            )

        super().__init__(agent_ids, **kwargs)

        # Terminal performance detection and adaptive refresh rate
        self._terminal_performance = self._detect_terminal_performance()
        self.refresh_rate = self._get_adaptive_refresh_rate(kwargs.get("refresh_rate"))

        # Rich-specific configuration
        self.theme = kwargs.get("theme", "dark")
        self.enable_syntax_highlighting = kwargs.get("enable_syntax_highlighting", True)
        self.max_content_lines = kwargs.get("max_content_lines", 8)
        self.max_line_length = kwargs.get("max_line_length", 100)
        self.show_timestamps = kwargs.get("show_timestamps", True)

        # Initialize Rich console and detect terminal dimensions
        self.console = Console(force_terminal=True, legacy_windows=False)
        self.terminal_size = self.console.size
        # Dynamic column width calculation - will be updated on resize
        self.num_agents = len(agent_ids)
        self.fixed_column_width = max(
            20, self.terminal_size.width // self.num_agents - 1
        )
        self.agent_panel_height = max(
            10, self.terminal_size.height - 13
        )  # Reserve space for header(5) + footer(8)

        self.orchestrator = kwargs.get("orchestrator", None)

        # Terminal resize handling
        self._resize_lock = threading.Lock()
        self._setup_resize_handler()

        self.live = None
        self._lock = threading.RLock()
        # Adaptive refresh intervals based on terminal performance
        self._last_update = 0
        self._update_interval = self._get_adaptive_update_interval()
        self._last_full_refresh = 0
        self._full_refresh_interval = self._get_adaptive_full_refresh_interval()

        # Performance monitoring
        self._refresh_times = []
        self._dropped_frames = 0
        self._performance_check_interval = 5.0  # Check performance every 5 seconds

        # Async refresh components - more workers for faster updates
        self._refresh_executor = ThreadPoolExecutor(
            max_workers=min(len(agent_ids) * 2 + 8, 20)
        )
        self._agent_panels_cache = {}
        self._header_cache = None
        self._footer_cache = None
        self._layout_update_lock = threading.Lock()
        self._pending_updates = set()
        self._shutdown_flag = False

        # Priority update queue for critical status changes
        self._priority_updates = set()
        self._status_update_executor = ThreadPoolExecutor(max_workers=4)

        # Theme configuration
        self._setup_theme()

        # Interactive mode variables
        self._keyboard_interactive_mode = kwargs.get("keyboard_interactive_mode", True)
        self._safe_keyboard_mode = kwargs.get(
            "safe_keyboard_mode", False
        )  # Non-interfering keyboard mode
        self._key_handler = None
        self._input_thread = None
        self._stop_input_thread = False
        self._original_settings = None
        self._agent_selector_active = (
            False  # Flag to prevent duplicate agent selector calls
        )

        # Store final presentation for re-display
        self._stored_final_presentation = None
        self._stored_presentation_agent = None
        self._stored_vote_results = None

        # Code detection patterns
        self.code_patterns = [
            r"```(\w+)?\n(.*?)\n```",  # Markdown code blocks
            r"`([^`]+)`",  # Inline code
            r"def\s+\w+\s*\(",  # Python functions
            r"class\s+\w+\s*[:(\s]",  # Python classes
            r"import\s+\w+",  # Python imports
            r"from\s+\w+\s+import",  # Python from imports
        ]

        # Progress tracking
        self.agent_progress = {agent_id: 0 for agent_id in agent_ids}
        self.agent_activity = {agent_id: "waiting" for agent_id in agent_ids}

        # Status change tracking to prevent unnecessary refreshes
        self._last_agent_status = {agent_id: "waiting" for agent_id in agent_ids}
        self._last_agent_activity = {agent_id: "waiting" for agent_id in agent_ids}
        self._last_content_hash = {agent_id: "" for agent_id in agent_ids}

        # Adaptive debounce mechanism for updates
        self._debounce_timers = {}
        self._debounce_delay = self._get_adaptive_debounce_delay()

        # Layered refresh strategy
        self._critical_updates = set()  # Status changes, errors, tool results
        self._normal_updates = set()  # Text content, thinking updates
        self._decorative_updates = set()  # Progress bars, timestamps

        # Message filtering settings - tool content always important
        self._important_content_types = {"presentation", "status", "tool", "error"}
        self._status_change_keywords = {
            "completed",
            "failed",
            "waiting",
            "error",
            "voted",
            "voting",
            "tool",
            "vote recorded",
        }
        self._important_event_keywords = {
            "completed",
            "failed",
            "voting",
            "voted",
            "final",
            "error",
            "started",
            "coordination",
            "tool",
            "vote recorded",
        }

        # Status jump mechanism for web search interruption
        self._status_jump_enabled = kwargs.get(
            "enable_status_jump", True
        )  # Enable jumping to latest status
        self._web_search_truncate_on_status_change = kwargs.get(
            "truncate_web_search_on_status_change", True
        )  # Truncate web search content on status changes
        self._max_web_search_lines = kwargs.get(
            "max_web_search_lines_on_status_change", 3
        )  # Maximum lines to keep from web search when status changes

        # Flush output configuration for final answer display
        self._enable_flush_output = kwargs.get(
            "enable_flush_output", True
        )  # Enable flush output for final answer
        self._flush_char_delay = kwargs.get(
            "flush_char_delay", 0.03
        )  # Delay between characters
        self._flush_word_delay = kwargs.get(
            "flush_word_delay", 0.08
        )  # Extra delay after punctuation

        # File-based output system
        self.output_dir = kwargs.get("output_dir", "agent_outputs")
        self.agent_files = {}
        self.system_status_file = None
        self._selected_agent = None
        self._setup_agent_files()

        # Adaptive text buffering system to accumulate chunks
        self._text_buffers = {agent_id: "" for agent_id in agent_ids}
        self._max_buffer_length = self._get_adaptive_buffer_length()
        self._buffer_timeout = self._get_adaptive_buffer_timeout()
        self._buffer_timers = {agent_id: None for agent_id in agent_ids}

        # Adaptive batching for updates
        self._update_batch = set()
        self._batch_timer = None
        self._batch_timeout = self._get_adaptive_batch_timeout()

    def _setup_resize_handler(self):
        """Setup SIGWINCH signal handler for terminal resize detection."""
        if not sys.stdin.isatty():
            return  # Skip if not running in a terminal

        try:
            # Set up signal handler for SIGWINCH (window change)
            signal.signal(signal.SIGWINCH, self._handle_resize_signal)
        except (AttributeError, OSError):
            # SIGWINCH might not be available on all platforms
            pass

    def _handle_resize_signal(self, signum, frame):
        """Handle SIGWINCH signal when terminal is resized."""
        # Use a separate thread to handle resize to avoid signal handler restrictions
        threading.Thread(target=self._handle_terminal_resize, daemon=True).start()

    def _handle_terminal_resize(self):
        """Handle terminal resize by recalculating layout and refreshing display."""
        with self._resize_lock:
            try:
                # VSCode-specific resize stabilization
                if self._terminal_performance["type"] == "vscode":
                    # VSCode terminal sometimes sends multiple resize events
                    # Add delay to let resize settle
                    time.sleep(0.05)

                # Get new terminal size
                new_size = self.console.size

                # Check if size actually changed
                if (
                    new_size.width != self.terminal_size.width
                    or new_size.height != self.terminal_size.height
                ):

                    # Update stored terminal size
                    old_size = self.terminal_size
                    self.terminal_size = new_size

                    # VSCode-specific post-resize delay
                    if self._terminal_performance["type"] == "vscode":
                        # Give VSCode terminal extra time to stabilize after resize
                        time.sleep(0.02)

                    # Recalculate layout dimensions
                    self._recalculate_layout()

                    # Clear all caches to force refresh
                    self._invalidate_display_cache()

                    # Force a complete display update
                    with self._lock:
                        # Mark all components for update
                        self._pending_updates.add("header")
                        self._pending_updates.add("footer")
                        self._pending_updates.update(self.agent_ids)

                        # Schedule immediate update
                        self._schedule_async_update(force_update=True)

                    # Small delay to allow display to stabilize
                    time.sleep(0.1)

            except Exception:
                # Silently handle errors to avoid disrupting the application
                pass

    def _recalculate_layout(self):
        """Recalculate layout dimensions based on current terminal size."""
        # Recalculate column width
        self.fixed_column_width = max(
            20, self.terminal_size.width // self.num_agents - 1
        )

        # Recalculate panel height (reserve space for header and footer)
        self.agent_panel_height = max(10, self.terminal_size.height - 13)

    def _invalidate_display_cache(self):
        """Invalidate all cached display components to force refresh."""
        self._agent_panels_cache.clear()
        self._header_cache = None
        self._footer_cache = None

    def _setup_agent_files(self):
        """Setup individual txt files for each agent and system status file."""
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Initialize file paths for each agent
        for agent_id in self.agent_ids:
            file_path = Path(self.output_dir) / f"{agent_id}.txt"
            self.agent_files[agent_id] = file_path
            # Clear existing file content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"=== {agent_id.upper()} OUTPUT LOG ===\n\n")

        # Initialize system status file
        self.system_status_file = Path(self.output_dir) / "system_status.txt"
        with open(self.system_status_file, "w", encoding="utf-8") as f:
            f.write("=== SYSTEM STATUS LOG ===\n\n")

    def _detect_terminal_performance(self):
        """Detect terminal performance characteristics for adaptive refresh rates."""
        terminal_info = {
            "type": "unknown",
            "performance_tier": "medium",  # low, medium, high
            "supports_unicode": True,
            "supports_color": True,
            "buffer_size": "normal",
        }

        try:
            # Get terminal type from environment
            term = os.environ.get("TERM", "").lower()
            term_program = os.environ.get("TERM_PROGRAM", "").lower()

            # Classify terminal types by performance
            if "iterm.app" in term_program or "iterm" in term_program.lower():
                terminal_info["performance_tier"] = "high"
                terminal_info["type"] = "iterm"
                terminal_info["supports_unicode"] = True
            elif (
                "vscode" in term_program
                or "code" in term_program
                or self._detect_vscode_terminal()
            ):
                # VSCode integrated terminal - needs special handling for flaky behavior
                terminal_info["performance_tier"] = "medium"
                terminal_info["type"] = "vscode"
                terminal_info["supports_unicode"] = True
                terminal_info["buffer_size"] = "large"  # VSCode has good buffering
                terminal_info["needs_flush_delay"] = True  # Reduce flicker
                terminal_info["refresh_stabilization"] = True  # Add stability delays
            elif "apple_terminal" in term_program or term_program == "terminal":
                terminal_info["performance_tier"] = "high"
                terminal_info["type"] = "macos_terminal"
                terminal_info["supports_unicode"] = True
            elif "xterm-256color" in term or "alacritty" in term_program:
                terminal_info["performance_tier"] = "high"
                terminal_info["type"] = "modern"
            elif "screen" in term or "tmux" in term:
                terminal_info["performance_tier"] = "low"  # Multiplexers are slower
                terminal_info["type"] = "multiplexer"
            elif "xterm" in term:
                terminal_info["performance_tier"] = "medium"
                terminal_info["type"] = "xterm"
            elif term in ["dumb", "vt100", "vt220"]:
                terminal_info["performance_tier"] = "low"
                terminal_info["type"] = "legacy"
                terminal_info["supports_unicode"] = False

            # Check for SSH (typically slower)
            if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT"):
                if terminal_info["performance_tier"] == "high":
                    terminal_info["performance_tier"] = "medium"
                elif terminal_info["performance_tier"] == "medium":
                    terminal_info["performance_tier"] = "low"

            # Detect color support
            colorterm = os.environ.get("COLORTERM", "").lower()
            if colorterm in ["truecolor", "24bit"]:
                terminal_info["supports_color"] = True
            elif not self.console.is_terminal or term == "dumb":
                terminal_info["supports_color"] = False

        except Exception:
            # Fallback to safe defaults
            terminal_info["performance_tier"] = "low"

        return terminal_info

    def _detect_vscode_terminal(self):
        """Additional VSCode terminal detection using multiple indicators."""
        try:
            # Check for VSCode-specific environment variables
            vscode_indicators = [
                "VSCODE_INJECTION",
                "VSCODE_PID",
                "VSCODE_IPC_HOOK",
                "VSCODE_IPC_HOOK_CLI",
                "TERM_PROGRAM_VERSION",
            ]

            # Check if any VSCode-specific env vars are present
            for indicator in vscode_indicators:
                if os.environ.get(indicator):
                    return True

            # Check if parent process is code or VSCode
            try:
                import psutil

                current_process = psutil.Process()
                parent = current_process.parent()
                if parent and (
                    "code" in parent.name().lower() or "vscode" in parent.name().lower()
                ):
                    return True
            except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Check for common VSCode terminal patterns in environment
            term_program = os.environ.get("TERM_PROGRAM", "").lower()
            if term_program and any(
                pattern in term_program for pattern in ["code", "vscode"]
            ):
                return True

            return False
        except Exception:
            return False

    def _get_adaptive_refresh_rate(self, user_override=None):
        """Get adaptive refresh rate based on terminal performance."""
        if user_override is not None:
            return user_override

        perf_tier = self._terminal_performance["performance_tier"]
        term_type = self._terminal_performance["type"]

        # VSCode-specific optimization
        if term_type == "vscode":
            # Lower refresh rate for VSCode to prevent flaky behavior
            # VSCode terminal sometimes has rendering delays
            return 2

        refresh_rates = {
            "high": 10,  # Modern terminals
            "medium": 5,  # Standard terminals
            "low": 2,  # Multiplexers, SSH, legacy
        }

        return refresh_rates.get(perf_tier, 8)

    def _get_adaptive_update_interval(self):
        """Get adaptive update interval based on terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]

        intervals = {
            "high": 0.02,  # 20ms - very responsive
            "medium": 0.05,  # 50ms - balanced
            "low": 0.1,  # 100ms - conservative
        }

        return intervals.get(perf_tier, 0.05)

    def _get_adaptive_full_refresh_interval(self):
        """Get adaptive full refresh interval based on terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]

        intervals = {"high": 0.1, "medium": 0.2, "low": 0.5}  # 100ms  # 200ms  # 500ms

        return intervals.get(perf_tier, 0.2)

    def _get_adaptive_debounce_delay(self):
        """Get adaptive debounce delay based on terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]
        term_type = self._terminal_performance["type"]

        delays = {"high": 0.01, "medium": 0.03, "low": 0.05}  # 10ms  # 30ms  # 50ms

        base_delay = delays.get(perf_tier, 0.03)

        # Increase debounce delay for macOS terminals to reduce flakiness
        if term_type in ["iterm", "macos_terminal"]:
            base_delay *= 2.0  # Double the debounce delay for stability

        return base_delay

    def _get_adaptive_buffer_length(self):
        """Get adaptive buffer length based on terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]
        term_type = self._terminal_performance["type"]

        lengths = {
            "high": 800,  # Longer buffers for fast terminals
            "medium": 500,  # Standard buffer length
            "low": 200,  # Shorter buffers for slow terminals
        }

        base_length = lengths.get(perf_tier, 500)

        # Reduce buffer size for macOS terminals to improve responsiveness
        if term_type in ["iterm", "macos_terminal"]:
            base_length = min(base_length, 400)

        return base_length

    def _get_adaptive_buffer_timeout(self):
        """Get adaptive buffer timeout based on terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]
        term_type = self._terminal_performance["type"]

        timeouts = {
            "high": 0.5,  # Fast flush for responsive terminals
            "medium": 1.0,  # Standard timeout
            "low": 2.0,  # Longer timeout for slow terminals
        }

        base_timeout = timeouts.get(perf_tier, 1.0)

        # Increase buffer timeout for macOS terminals for smoother text flow
        if term_type in ["iterm", "macos_terminal"]:
            base_timeout *= 1.5  # 50% longer timeout for stability

        return base_timeout

    def _get_adaptive_batch_timeout(self):
        """Get adaptive batch timeout for update batching."""
        perf_tier = self._terminal_performance["performance_tier"]

        timeouts = {
            "high": 0.05,  # 50ms batching for fast terminals
            "medium": 0.1,  # 100ms batching for medium terminals
            "low": 0.2,  # 200ms batching for slow terminals
        }

        return timeouts.get(perf_tier, 0.1)

    def _monitor_performance(self):
        """Monitor refresh performance and adjust if needed."""
        current_time = time.time()

        # Clean old refresh time records (keep last 20)
        if len(self._refresh_times) > 20:
            self._refresh_times = self._refresh_times[-20:]

        # Calculate average refresh time
        if len(self._refresh_times) >= 5:
            avg_refresh_time = sum(self._refresh_times) / len(self._refresh_times)
            expected_refresh_time = 1.0 / self.refresh_rate

            # If refresh takes too long, downgrade performance
            if avg_refresh_time > expected_refresh_time * 2:
                self._dropped_frames += 1

                # After 3 dropped frames, reduce refresh rate
                if self._dropped_frames >= 3:
                    old_rate = self.refresh_rate
                    self.refresh_rate = max(2, int(self.refresh_rate * 0.7))
                    self._dropped_frames = 0

                    # Update intervals accordingly
                    self._update_interval = 1.0 / self.refresh_rate
                    self._full_refresh_interval *= 1.5

                    # Restart live display with new rate if active
                    if self.live and self.live.is_started:
                        try:
                            self.live.refresh_per_second = self.refresh_rate
                        except:
                            # If live display fails, fallback to simple mode
                            self._fallback_to_simple_display()

    def _create_live_display_with_fallback(self):
        """Create Live display with terminal compatibility checks and fallback."""
        try:
            # Test terminal capabilities
            if not self._test_terminal_capabilities():
                return self._fallback_to_simple_display()

            # Create Live display with adaptive settings
            live_settings = self._get_adaptive_live_settings()

            live = Live(self._create_layout(), console=self.console, **live_settings)

            # Test if Live display works
            try:
                # Quick test start/stop to verify functionality
                live.start()
                live.stop()
                return live
            except Exception:
                # Live display failed, try fallback
                return self._fallback_to_simple_display()

        except Exception:
            # Any error in setup, use fallback
            return self._fallback_to_simple_display()

    def _test_terminal_capabilities(self):
        """Test if terminal supports rich Live display features."""
        try:
            # Check if we're in a proper terminal
            if not self.console.is_terminal:
                return False

            # Check terminal type compatibility
            perf_tier = self._terminal_performance["performance_tier"]
            term_type = self._terminal_performance["type"]

            # Disable Live for very limited terminals
            if term_type == "legacy" or perf_tier == "low":
                # Allow basic terminals if not too limited
                term = os.environ.get("TERM", "").lower()
                if term in ["dumb", "vt100"]:
                    return False

            # Enable Live for macOS terminals with optimizations
            if term_type in ["iterm", "macos_terminal"]:
                return True

            # Test basic console functionality
            test_size = self.console.size
            if test_size.width < 20 or test_size.height < 10:
                return False

            return True

        except Exception:
            return False

    def _get_adaptive_live_settings(self):
        """Get Live display settings adapted to terminal performance."""
        perf_tier = self._terminal_performance["performance_tier"]

        settings = {
            "refresh_per_second": self.refresh_rate,
            "vertical_overflow": "ellipsis",
            "transient": False,
        }

        # Adjust settings based on performance tier
        if perf_tier == "low":
            settings["refresh_per_second"] = min(settings["refresh_per_second"], 3)
            settings["transient"] = True  # Reduce memory usage
        elif perf_tier == "medium":
            settings["refresh_per_second"] = min(settings["refresh_per_second"], 8)

        # Disable auto_refresh for multiplexers to prevent conflicts
        if self._terminal_performance["type"] == "multiplexer":
            settings["auto_refresh"] = False

        # macOS terminal-specific optimizations
        if self._terminal_performance["type"] in ["iterm", "macos_terminal"]:
            # Use more conservative refresh rates for macOS terminals to reduce flakiness
            settings["refresh_per_second"] = min(settings["refresh_per_second"], 5)
            # Enable transient mode to reduce flicker
            settings["transient"] = False
            # Ensure vertical overflow is handled gracefully
            settings["vertical_overflow"] = "ellipsis"

        # VSCode terminal-specific optimizations
        if self._terminal_performance["type"] == "vscode":
            # VSCode terminal needs very conservative refresh to prevent flaky behavior
            settings["refresh_per_second"] = min(settings["refresh_per_second"], 6)
            # Use transient mode to reduce rendering artifacts
            settings["transient"] = False
            # Handle overflow gracefully to prevent layout issues
            settings["vertical_overflow"] = "ellipsis"
            # Reduce auto-refresh frequency for stability
            settings["auto_refresh"] = True

        return settings

    def _fallback_to_simple_display(self):
        """Fallback to simple console output when Live display is not supported."""
        self._simple_display_mode = True

        # Print a simple status message
        try:
            self.console.print(
                "\n[yellow]Terminal compatibility: Using simple display mode[/yellow]"
            )
            self.console.print(
                f"[dim]Monitoring {len(self.agent_ids)} agents...[/dim]\n"
            )
        except:
            # If even basic console fails, use plain print
            print("\nUsing simple display mode...")
            print(f"Monitoring {len(self.agent_ids)} agents...\n")

        return None  # No Live display

    def _update_display_safe(self):
        """Safely update display with fallback support and terminal-specific synchronization."""
        # Add extra synchronization for macOS terminals and VSCode to prevent race conditions
        term_type = self._terminal_performance["type"]
        use_safe_mode = term_type in ["iterm", "macos_terminal", "vscode"]

        # VSCode-specific stabilization
        if term_type == "vscode" and self._terminal_performance.get(
            "refresh_stabilization"
        ):
            # Add small delay before refresh to let VSCode terminal stabilize
            time.sleep(0.01)

        try:
            if use_safe_mode:
                # For macOS terminals and VSCode, use more conservative locking
                with self._layout_update_lock:
                    with self._lock:  # Double locking for extra safety
                        if (
                            hasattr(self, "_simple_display_mode")
                            and self._simple_display_mode
                        ):
                            self._update_simple_display()
                        else:
                            self._update_live_display_safe()
            else:
                with self._layout_update_lock:
                    if (
                        hasattr(self, "_simple_display_mode")
                        and self._simple_display_mode
                    ):
                        self._update_simple_display()
                    else:
                        self._update_live_display()
        except Exception:
            # Fallback to simple display on any error
            self._fallback_to_simple_display()

        # VSCode-specific post-refresh stabilization
        if term_type == "vscode" and self._terminal_performance.get(
            "needs_flush_delay"
        ):
            # Small delay after refresh to prevent flicker
            time.sleep(0.005)

    def _update_simple_display(self):
        """Update display in simple mode without Live."""
        try:
            # Simple status update every few seconds
            current_time = time.time()
            if not hasattr(self, "_last_simple_update"):
                self._last_simple_update = 0

            if current_time - self._last_simple_update > 2.0:  # Update every 2 seconds
                status_line = f"[{time.strftime('%H:%M:%S')}] Agents: "
                for agent_id in self.agent_ids:
                    status = self.agent_status.get(agent_id, "waiting")
                    status_line += f"{agent_id}:{status} "

                try:
                    self.console.print(f"\r{status_line[:80]}", end="")
                except:
                    print(f"\r{status_line[:80]}", end="")

                self._last_simple_update = current_time

        except Exception:
            pass

    def _update_live_display(self):
        """Update Live display mode."""
        try:
            if self.live:
                self.live.update(self._create_layout())
        except Exception:
            # If Live display fails, switch to simple mode
            self._fallback_to_simple_display()

    def _update_live_display_safe(self):
        """Update Live display mode with extra safety for macOS terminals."""
        try:
            if self.live and self.live.is_started:
                # For macOS terminals, add a small delay to prevent flickering
                import time

                time.sleep(0.001)  # 1ms delay for terminal synchronization
                self.live.update(self._create_layout())
            elif self.live:
                # If live display exists but isn't started, try to restart it
                try:
                    self.live.start()
                    self.live.update(self._create_layout())
                except Exception:
                    self._fallback_to_simple_display()
        except Exception:
            # If Live display fails, switch to simple mode
            self._fallback_to_simple_display()

    def _setup_theme(self):
        """Setup color theme configuration."""
        themes = {
            "dark": {
                "primary": "bright_cyan",
                "secondary": "bright_blue",
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_magenta",
                "text": "white",
                "border": "blue",
                "panel_style": "blue",
                "header_style": "bold bright_cyan",
            },
            "light": {
                "primary": "blue",
                "secondary": "cyan",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "magenta",
                "text": "black",
                "border": "blue",
                "panel_style": "blue",
                "header_style": "bold blue",
            },
            "cyberpunk": {
                "primary": "bright_magenta",
                "secondary": "bright_cyan",
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_blue",
                "text": "bright_white",
                "border": "bright_magenta",
                "panel_style": "bright_magenta",
                "header_style": "bold bright_magenta",
            },
        }

        self.colors = themes.get(self.theme, themes["dark"])

        # VSCode terminal-specific color adjustments
        if self._terminal_performance["type"] == "vscode":
            # VSCode terminal sometimes has issues with certain bright colors
            # Use more stable color palette
            vscode_adjustments = {
                "primary": "cyan",  # Less bright than bright_cyan
                "secondary": "blue",
                "border": "cyan",
                "panel_style": "cyan",
            }
            self.colors.update(vscode_adjustments)

            # Set up VSCode-safe emoji mapping for better compatibility
            self._setup_vscode_emoji_fallbacks()

    def _setup_vscode_emoji_fallbacks(self):
        """Setup emoji fallbacks for VSCode terminal compatibility."""
        # VSCode terminal sometimes has issues with certain Unicode characters
        # Provide ASCII fallbacks for better stability
        self._emoji_fallbacks = {
            "🚀": ">>",  # Launch/rocket
            "🎯": ">",  # Target
            "💭": "...",  # Thinking
            "⚡": "!",  # Status update
            "🎨": "*",  # Theme
            "📝": "=",  # Writing
            "✅": "[OK]",  # Success
            "❌": "[X]",  # Error
            "⭐": "*",  # Important
            "🔍": "?",  # Search
            "📊": "|",  # Status/data
        }

        # Only use fallbacks if VSCode terminal has Unicode issues
        # This can be detected at runtime if needed
        if not self._terminal_performance.get("supports_unicode", True):
            self._use_emoji_fallbacks = True
        else:
            self._use_emoji_fallbacks = False

    def _safe_emoji(self, emoji: str) -> str:
        """Get safe emoji for current terminal, with VSCode fallbacks."""
        if (
            self._terminal_performance["type"] == "vscode"
            and self._use_emoji_fallbacks
            and emoji in self._emoji_fallbacks
        ):
            return self._emoji_fallbacks[emoji]
        return emoji

    def initialize(self, question: str, log_filename: Optional[str] = None):
        """Initialize the rich display with question and optional log file."""
        self.log_filename = log_filename
        self.question = question

        # Clear screen
        self.console.clear()

        # Create initial layout
        self._create_initial_display()

        # Setup keyboard handling if in interactive mode
        if self._keyboard_interactive_mode:
            self._setup_keyboard_handler()

        # Start live display with adaptive settings and fallback support
        self.live = self._create_live_display_with_fallback()
        if self.live:
            self.live.start()

        # Write initial system status
        self._write_system_status()

        # Interactive mode is handled through input prompts

    def _create_initial_display(self):
        """Create the initial welcome display."""
        welcome_text = Text()
        welcome_text.append(
            "🚀 MassGen Coordination Dashboard 🚀\n", style=self.colors["header_style"]
        )
        welcome_text.append(
            f"Multi-Agent System with {len(self.agent_ids)} agents\n",
            style=self.colors["primary"],
        )

        if self.log_filename:
            welcome_text.append(
                f"📁 Log: {self.log_filename}\n", style=self.colors["info"]
            )

        welcome_text.append(
            f"🎨 Theme: {self.theme.title()}", style=self.colors["secondary"]
        )

        welcome_panel = Panel(
            welcome_text,
            box=DOUBLE,
            border_style=self.colors["border"],
            title="[bold]Welcome[/bold]",
            title_align="center",
        )

        self.console.print(welcome_panel)
        self.console.print()

    def _create_layout(self) -> Layout:
        """Create the main layout structure with cached components."""
        layout = Layout()

        # Use cached components if available, otherwise create new ones
        header = self._header_cache if self._header_cache else self._create_header()
        agent_columns = self._create_agent_columns_from_cache()
        footer = self._footer_cache if self._footer_cache else self._create_footer()

        # Arrange layout
        layout.split_column(
            Layout(header, name="header", size=5),
            Layout(agent_columns, name="main"),
            Layout(footer, name="footer", size=8),
        )

        return layout

    def _create_agent_columns_from_cache(self) -> Columns:
        """Create agent columns using cached panels with fixed widths."""
        agent_panels = []

        for agent_id in self.agent_ids:
            if agent_id in self._agent_panels_cache:
                agent_panels.append(self._agent_panels_cache[agent_id])
            else:
                panel = self._create_agent_panel(agent_id)
                self._agent_panels_cache[agent_id] = panel
                agent_panels.append(panel)

        # Use fixed column widths with equal=False to enforce exact sizing
        return Columns(
            agent_panels, equal=False, expand=False, width=self.fixed_column_width
        )

    def _create_header(self) -> Panel:
        """Create the header panel."""
        header_text = Text()
        header_text.append(
            "🚀 MassGen Multi-Agent Coordination System",
            style=self.colors["header_style"],
        )

        if hasattr(self, "question"):
            header_text.append(
                f"\n💡 Question: {self.question[:80]}{'...' if len(self.question) > 80 else ''}",
                style=self.colors["info"],
            )

        return Panel(
            Align.center(header_text),
            box=ROUNDED,
            border_style=self.colors["border"],
            height=5,
        )

    def _create_agent_columns(self) -> Columns:
        """Create columns for each agent with fixed widths."""
        agent_panels = []

        for agent_id in self.agent_ids:
            panel = self._create_agent_panel(agent_id)
            agent_panels.append(panel)

        # Use fixed column widths with equal=False to enforce exact sizing
        return Columns(
            agent_panels, equal=False, expand=False, width=self.fixed_column_width
        )

    def _setup_keyboard_handler(self):
        """Setup keyboard handler for interactive agent selection."""
        try:
            # Simple key mapping for agent selection
            self._agent_keys = {}
            for i, agent_id in enumerate(self.agent_ids):
                key = str(i + 1)
                self._agent_keys[key] = agent_id

            # Start background input thread for Live mode
            if self._keyboard_interactive_mode:
                self._start_input_thread()

        except ImportError:
            self._keyboard_interactive_mode = False

    def _start_input_thread(self):
        """Start background thread for keyboard input during Live mode."""
        if not sys.stdin.isatty():
            return  # Can't handle input if not a TTY

        self._stop_input_thread = False

        # Choose input method based on safety requirements and terminal type
        term_type = self._terminal_performance["type"]

        if self._safe_keyboard_mode or term_type in ["iterm", "macos_terminal"]:
            # Use completely safe method for macOS terminals to avoid conflicts
            self._input_thread = threading.Thread(
                target=self._input_thread_worker_safe, daemon=True
            )
            self._input_thread.start()
        else:
            # Try improved method first, fallback to polling method if needed
            try:
                self._input_thread = threading.Thread(
                    target=self._input_thread_worker_improved, daemon=True
                )
                self._input_thread.start()
            except Exception:
                # Fallback to simpler polling method
                self._input_thread = threading.Thread(
                    target=self._input_thread_worker_fallback, daemon=True
                )
                self._input_thread.start()

    def _input_thread_worker_improved(self):
        """Improved background thread worker that doesn't interfere with Rich rendering."""
        try:
            # Save original terminal settings but don't change to raw mode
            if sys.stdin.isatty():
                self._original_settings = termios.tcgetattr(sys.stdin.fileno())
                # Use canonical mode with minimal changes
                new_settings = termios.tcgetattr(sys.stdin.fileno())
                # Enable non-blocking input without full raw mode
                new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
                new_settings[6][termios.VMIN] = 0  # Non-blocking
                new_settings[6][termios.VTIME] = 1  # 100ms timeout
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, new_settings)

            while not self._stop_input_thread:
                try:
                    # Use select with shorter timeout to be more responsive
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                        char = sys.stdin.read(1)
                        if char:
                            self._handle_key_press(char)
                except (BlockingIOError, OSError):
                    # Expected in non-blocking mode, continue
                    continue

        except (KeyboardInterrupt, EOFError):
            pass
        except Exception as e:
            # Handle errors gracefully
            pass
        finally:
            # Restore terminal settings
            self._restore_terminal_settings()

    def _input_thread_worker_fallback(self):
        """Fallback keyboard input method using simple polling without terminal mode changes."""
        import time

        # Show instructions to user
        self.console.print(
            "\n[dim]Keyboard support active. Press keys during Live display:[/dim]"
        )
        self.console.print(
            "[dim]1-{} to open agent files, 's' for system status, 'q' to quit[/dim]\n".format(
                len(self.agent_ids)
            )
        )

        try:
            while not self._stop_input_thread:
                # Use a much simpler approach - just sleep and check flag
                time.sleep(0.1)

                # In this fallback mode, we rely on the user using Ctrl+C or
                # external interruption rather than single-key detection
                # This prevents any terminal mode conflicts

        except (KeyboardInterrupt, EOFError):
            # Handle graceful shutdown
            pass
        except Exception:
            # Handle any other errors gracefully
            pass

    def _input_thread_worker_safe(self):
        """Completely safe keyboard input that never changes terminal settings."""
        # This method does nothing to avoid any interference with Rich rendering
        # Keyboard functionality is disabled in safe mode to prevent rendering issues
        try:
            while not self._stop_input_thread:
                time.sleep(0.5)  # Just wait without doing anything
        except:
            pass

    def _restore_terminal_settings(self):
        """Restore original terminal settings."""
        try:
            if self._original_settings and sys.stdin.isatty():
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN, self._original_settings
                )
                self._original_settings = None
        except:
            pass

    def _ensure_clean_keyboard_state(self):
        """Ensure clean keyboard state before starting agent selector."""
        # Stop input thread completely
        self._stop_input_thread = True
        if self._input_thread and self._input_thread.is_alive():
            try:
                self._input_thread.join(timeout=0.5)
            except:
                pass

        # Restore terminal settings to normal mode
        self._restore_terminal_settings()

        # Clear any pending keyboard input from stdin buffer
        try:
            if sys.stdin.isatty():
                import termios

                # Flush input buffer to remove any pending keystrokes
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except:
            pass

        # Small delay to ensure all cleanup is complete
        import time

        time.sleep(0.1)

    def _handle_key_press(self, key):
        """Handle key press events for agent selection."""
        if key in self._agent_keys:
            agent_id = self._agent_keys[key]
            self._open_agent_in_default_text_editor(agent_id)
        elif key == "s":
            self._open_system_status_in_default_text_editor()
        elif key == "q":
            # Quit the application - restore terminal and stop
            self._stop_input_thread = True
            self._restore_terminal_settings()

    def _open_agent_in_default_text_editor(self, agent_id: str):
        """Open agent's txt file in default text editor."""
        if agent_id not in self.agent_files:
            return

        file_path = self.agent_files[agent_id]
        if not file_path.exists():
            return

        try:
            # Use system default application to open text files
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=False)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(["xdg-open", str(file_path)], check=False)
            elif sys.platform == "win32":  # Windows
                subprocess.run(["start", str(file_path)], check=False, shell=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to external app method
            self._open_agent_in_external_app(agent_id)

    def _open_agent_in_vscode_new_window(self, agent_id: str):
        """Open agent's txt file in a new VS Code window."""
        if agent_id not in self.agent_files:
            return

        file_path = self.agent_files[agent_id]
        if not file_path.exists():
            return

        try:
            # Force open in new VS Code window
            subprocess.run(["code", "--new-window", str(file_path)], check=False)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to existing method if VS Code is not available
            self._open_agent_in_external_app(agent_id)

    def _open_system_status_in_default_text_editor(self):
        """Open system status file in default text editor."""
        if not self.system_status_file or not self.system_status_file.exists():
            return

        try:
            # Use system default application to open text files
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(self.system_status_file)], check=False)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(["xdg-open", str(self.system_status_file)], check=False)
            elif sys.platform == "win32":  # Windows
                subprocess.run(
                    ["start", str(self.system_status_file)], check=False, shell=True
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to external app method
            self._open_system_status_in_external_app()

    def _open_system_status_in_vscode_new_window(self):
        """Open system status file in a new VS Code window."""
        if not self.system_status_file or not self.system_status_file.exists():
            return

        try:
            # Force open in new VS Code window
            subprocess.run(
                ["code", "--new-window", str(self.system_status_file)], check=False
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to existing method if VS Code is not available
            self._open_system_status_in_external_app()

    def _open_agent_in_external_app(self, agent_id: str):
        """Open agent's txt file in external editor or terminal viewer."""
        if agent_id not in self.agent_files:
            return

        file_path = self.agent_files[agent_id]
        if not file_path.exists():
            return

        try:
            # Try different methods to open the file
            if sys.platform == "darwin":  # macOS
                # Try VS Code first, then other editors, then default text editor
                editors = ["code", "subl", "atom", "nano", "vim", "open"]
                for editor in editors:
                    try:
                        if editor == "open":
                            subprocess.run(
                                ["open", "-a", "TextEdit", str(file_path)], check=False
                            )
                        else:
                            subprocess.run([editor, str(file_path)], check=False)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif sys.platform.startswith("linux"):  # Linux
                # Try common Linux editors
                editors = ["code", "gedit", "kate", "nano", "vim", "xdg-open"]
                for editor in editors:
                    try:
                        subprocess.run([editor, str(file_path)], check=False)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif sys.platform == "win32":  # Windows
                # Try Windows editors
                editors = ["code", "notepad++", "notepad"]
                for editor in editors:
                    try:
                        subprocess.run(
                            [editor, str(file_path)], check=False, shell=True
                        )
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue

        except Exception:
            # If all else fails, show a message that the file exists
            pass

    def _open_system_status_in_external_app(self):
        """Open system status file in external editor or terminal viewer."""
        if not self.system_status_file or not self.system_status_file.exists():
            return

        try:
            # Try different methods to open the file
            if sys.platform == "darwin":  # macOS
                # Try VS Code first, then other editors, then default text editor
                editors = ["code", "subl", "atom", "nano", "vim", "open"]
                for editor in editors:
                    try:
                        if editor == "open":
                            subprocess.run(
                                [
                                    "open",
                                    "-a",
                                    "TextEdit",
                                    str(self.system_status_file),
                                ],
                                check=False,
                            )
                        else:
                            subprocess.run(
                                [editor, str(self.system_status_file)], check=False
                            )
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif sys.platform.startswith("linux"):  # Linux
                # Try common Linux editors
                editors = ["code", "gedit", "kate", "nano", "vim", "xdg-open"]
                for editor in editors:
                    try:
                        subprocess.run(
                            [editor, str(self.system_status_file)], check=False
                        )
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif sys.platform == "win32":  # Windows
                # Try Windows editors
                editors = ["code", "notepad++", "notepad"]
                for editor in editors:
                    try:
                        subprocess.run(
                            [editor, str(self.system_status_file)],
                            check=False,
                            shell=True,
                        )
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue

        except Exception:
            # If all else fails, show a message that the file exists
            pass

    def _show_agent_full_content(self, agent_id: str):
        """Display full content of selected agent from txt file."""
        if agent_id not in self.agent_files:
            return

        try:
            file_path = self.agent_files[agent_id]
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Add separator instead of clearing screen
                self.console.print("\n" + "=" * 80 + "\n")

                # Create header
                header_text = Text()
                header_text.append(
                    f"📄 {agent_id.upper()} - Full Content",
                    style=self.colors["header_style"],
                )
                header_text.append(
                    "\nPress any key to return to main view", style=self.colors["info"]
                )

                header_panel = Panel(
                    header_text, box=DOUBLE, border_style=self.colors["border"]
                )

                # Create content panel
                content_panel = Panel(
                    content,
                    title=f"[bold]{agent_id.upper()} Output[/bold]",
                    border_style=self.colors["border"],
                    box=ROUNDED,
                )

                self.console.print(header_panel)
                self.console.print(content_panel)

                # Wait for key press to return
                input("Press Enter to return to agent selector...")

                # Add separator instead of clearing screen
                self.console.print("\n" + "=" * 80 + "\n")

        except Exception as e:
            # Handle errors gracefully
            pass

    def show_agent_selector(self):
        """Show agent selector and handle user input."""

        if not self._keyboard_interactive_mode or not hasattr(self, "_agent_keys"):
            return

        # Prevent duplicate agent selector calls
        if self._agent_selector_active:
            return

        self._agent_selector_active = True

        # Ensure clean keyboard state before starting agent selector
        self._ensure_clean_keyboard_state()

        try:
            loop_count = 0
            while True:
                loop_count += 1

                # Display available options

                options_text = Text()
                options_text.append(
                    "\nThis is a system inspection interface for diving into the multi-agent collaboration behind the scenes in MassGen. It lets you examine each agent’s original output and compare it to the final MassGen answer in terms of quality. You can explore the detailed communication, collaboration, voting, and decision-making process.\n",
                    style=self.colors["text"],
                )

                options_text.append(
                    "\n🎮 Select an agent to view full output:\n",
                    style=self.colors["primary"],
                )

                for key, agent_id in self._agent_keys.items():
                    options_text.append(
                        f"  {key}: ", style=self.colors["warning"]
                    )
                    options_text.append(
                        f"Inspect the original answer and working log of agent ", style=self.colors["text"]
                    )
                    options_text.append(
                        f"{agent_id}\n", style=self.colors["warning"]
                    )

                options_text.append(
                    "  s: Inpsect the orchestrator working log including the voting process\n", style=self.colors["warning"]
                )

                # Add option to show final presentation if it's stored
                if self._stored_final_presentation and self._stored_presentation_agent:
                    options_text.append(
                        f"  f: Show final presentation from Selected Agent ({agent_id})\n", style=self.colors["success"]
                    )

                options_text.append("  q: Quit Inspection\n", style=self.colors["info"])

                self.console.print(
                    Panel(
                        options_text,
                        title="[bold]Agent Selector[/bold]",
                        border_style=self.colors["border"],
                    )
                )

                # Get user input
                try:
                    choice = input("Enter your choice: ").strip().lower()

                    if choice in self._agent_keys:
                        self._show_agent_full_content(self._agent_keys[choice])
                    elif choice == "s":
                        self._show_system_status()
                    elif choice == "f" and self._stored_final_presentation:
                        self._redisplay_final_presentation()
                    elif choice == "q":
                        break
                    else:
                        self.console.print(
                            f"[{self.colors['error']}]Invalid choice. Please try again.[/{self.colors['error']}]"
                        )
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    break
        finally:
            # Always reset the flag when exiting
            self._agent_selector_active = True

    def _redisplay_final_presentation(self):
        """Redisplay the stored final presentation."""
        if not self._stored_final_presentation or not self._stored_presentation_agent:
            self.console.print(
                f"[{self.colors['error']}]No final presentation stored.[/{self.colors['error']}]"
            )
            return

        # Add separator
        self.console.print("\n" + "=" * 80 + "\n")

        # Display the stored presentation
        self._display_final_presentation_content(
            self._stored_presentation_agent, self._stored_final_presentation
        )

        # Wait for user to continue
        input("\nPress Enter to return to agent selector...")

        # Add separator
        self.console.print("\n" + "=" * 80 + "\n")

    def _redisplay_final_presentation(self):
        """Redisplay the stored final presentation."""
        if not self._stored_final_presentation or not self._stored_presentation_agent:
            self.console.print(
                f"[{self.colors['error']}]No final presentation stored.[/{self.colors['error']}]"
            )
            return

        # Add separator
        self.console.print("\n" + "=" * 80 + "\n")

        # Display the stored presentation
        self._display_final_presentation_content(
            self._stored_presentation_agent, self._stored_final_presentation
        )

        # Wait for user to continue
        input("\nPress Enter to return to agent selector...")

        # Add separator
        self.console.print("\n" + "=" * 80 + "\n")

    def _show_system_status(self):
        """Display system status from txt file."""
        if not self.system_status_file or not self.system_status_file.exists():
            self.console.print(
                f"[{self.colors['error']}]System status file not found.[/{self.colors['error']}]"
            )
            return

        try:
            with open(self.system_status_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Add separator instead of clearing screen
            self.console.print("\n" + "=" * 80 + "\n")

            # Create header
            header_text = Text()
            header_text.append(
                "📊 SYSTEM STATUS - Full Log", style=self.colors["header_style"]
            )
            header_text.append(
                "\nPress any key to return to agent selector", style=self.colors["info"]
            )

            header_panel = Panel(
                header_text, box=DOUBLE, border_style=self.colors["border"]
            )

            # Create content panel
            content_panel = Panel(
                content,
                title="[bold]System Status Log[/bold]",
                border_style=self.colors["border"],
                box=ROUNDED,
            )

            self.console.print(header_panel)
            self.console.print(content_panel)

            # Wait for key press to return
            input("Press Enter to return to agent selector...")

            # Add separator instead of clearing screen
            self.console.print("\n" + "=" * 80 + "\n")

        except Exception as e:
            self.console.print(
                f"[{self.colors['error']}]Error reading system status file: {e}[/{self.colors['error']}]"
            )

    def _create_agent_panel(self, agent_id: str) -> Panel:
        """Create a panel for a specific agent."""
        # Get agent content
        agent_content = self.agent_outputs.get(agent_id, [])
        status = self.agent_status.get(agent_id, "waiting")
        activity = self.agent_activity.get(agent_id, "waiting")

        # Create content text
        content_text = Text()

        # Show more lines since we now support scrolling
        # max_display_lines = min(len(agent_content), self.max_content_lines * 3) if agent_content else 0

        # if max_display_lines == 0:
        #     content_text.append("No activity yet...", style=self.colors['text'])
        # else:
        #     # Show recent content with scrolling support
        #     display_content = agent_content[-max_display_lines:] if max_display_lines > 0 else agent_content

        #     for line in display_content:
        #         formatted_line = self._format_content_line(line)
        #         content_text.append(formatted_line)
        #         content_text.append("\n")

        max_lines = max(0, self.agent_panel_height - 3)
        if not agent_content:
            content_text.append("No activity yet...", style=self.colors["text"])
        else:
            for line in agent_content[-max_lines:]:
                formatted_line = self._format_content_line(line)
                content_text.append(formatted_line)
                content_text.append("\n")

        # Status indicator
        status_emoji = self._get_status_emoji(status, activity)
        status_color = self._get_status_color(status)

        # Get backend info if available
        backend_name = self._get_backend_name(agent_id)

        # Panel title with click indicator
        title = f"{status_emoji} {agent_id.upper()}"
        if backend_name != "Unknown":
            title += f" ({backend_name})"

        # Add interactive indicator if enabled
        if self._keyboard_interactive_mode and hasattr(self, "_agent_keys"):
            agent_key = next(
                (k for k, v in self._agent_keys.items() if v == agent_id), None
            )
            if agent_key:
                title += f" [Press {agent_key}]"

        # Create panel with scrollable content
        return Panel(
            content_text,
            title=f"[{status_color}]{title}[/{status_color}]",
            border_style=status_color,
            box=ROUNDED,
            height=self.agent_panel_height,
            width=self.fixed_column_width,
        )

    def _format_content_line(self, line: str) -> Text:
        """Format a content line with syntax highlighting and styling."""
        formatted = Text()

        # Skip empty lines
        if not line.strip():
            return formatted

        # Enhanced handling for web search content
        if self._is_web_search_content(line):
            return self._format_web_search_line(line)

        # Truncate line if too long
        if len(line) > self.max_line_length:
            line = line[: self.max_line_length - 3] + "..."

        # Check for special prefixes and format accordingly
        if line.startswith("→"):
            # Tool usage
            formatted.append("→ ", style=self.colors["warning"])
            formatted.append(line[2:], style=self.colors["text"])
        elif line.startswith("🎤"):
            # Presentation content
            formatted.append("🎤 ", style=self.colors["success"])
            formatted.append(line[3:], style=f"bold {self.colors['success']}")
        elif line.startswith("⚡"):
            # Working indicator or status jump indicator
            formatted.append("⚡ ", style=self.colors["warning"])
            if "jumped to latest" in line:
                formatted.append(line[3:], style=f"bold {self.colors['info']}")
            else:
                formatted.append(line[3:], style=f"italic {self.colors['warning']}")
        elif self._is_code_content(line):
            # Code content - apply syntax highlighting
            if self.enable_syntax_highlighting:
                formatted = self._apply_syntax_highlighting(line)
            else:
                formatted.append(line, style=f"bold {self.colors['info']}")
        else:
            # Regular content
            formatted.append(line, style=self.colors["text"])

        return formatted

    def _format_presentation_content(self, content: str) -> Text:
        """Format presentation content with enhanced styling for orchestrator queries."""
        formatted = Text()

        # Split content into lines for better formatting
        lines = content.split("\n") if "\n" in content else [content]

        for line in lines:
            if not line.strip():
                formatted.append("\n")
                continue

            # Special formatting for orchestrator query responses
            if line.startswith("**") and line.endswith("**"):
                # Bold emphasis for important points
                clean_line = line.strip("*").strip()
                formatted.append(clean_line, style=f"bold {self.colors['success']}")
            elif line.startswith("- ") or line.startswith("• "):
                # Bullet points with enhanced styling
                formatted.append(line[:2], style=self.colors["primary"])
                formatted.append(line[2:], style=self.colors["text"])
            elif line.startswith("#"):
                # Headers with different styling
                header_level = len(line) - len(line.lstrip("#"))
                clean_header = line.lstrip("# ").strip()
                if header_level <= 2:
                    formatted.append(
                        clean_header, style=f"bold {self.colors['header_style']}"
                    )
                else:
                    formatted.append(
                        clean_header, style=f"bold {self.colors['primary']}"
                    )
            elif self._is_code_content(line):
                # Code blocks in presentations
                if self.enable_syntax_highlighting:
                    formatted.append(self._apply_syntax_highlighting(line))
                else:
                    formatted.append(line, style=f"bold {self.colors['info']}")
            else:
                # Regular presentation text with enhanced readability
                formatted.append(line, style=self.colors["text"])

            # Add newline except for the last line
            if line != lines[-1]:
                formatted.append("\n")

        return formatted

    def _is_web_search_content(self, line: str) -> bool:
        """Check if content is from web search and needs special formatting."""
        web_search_indicators = [
            "[Provider Tool: Web Search]",
            "🔍 [Search Query]",
            "✅ [Provider Tool: Web Search]",
            "🔍 [Provider Tool: Web Search]",
        ]
        return any(indicator in line for indicator in web_search_indicators)

    def _format_web_search_line(self, line: str) -> Text:
        """Format web search content with better truncation and styling."""
        formatted = Text()

        # Handle different types of web search lines
        if "[Provider Tool: Web Search] Starting search" in line:
            formatted.append("🔍 ", style=self.colors["info"])
            formatted.append("Web search starting...", style=self.colors["text"])
        elif "[Provider Tool: Web Search] Searching" in line:
            formatted.append("🔍 ", style=self.colors["warning"])
            formatted.append("Searching...", style=self.colors["text"])
        elif "[Provider Tool: Web Search] Search completed" in line:
            formatted.append("✅ ", style=self.colors["success"])
            formatted.append("Search completed", style=self.colors["text"])
        elif any(
            pattern in line
            for pattern in ["🔍 [Search Query]", "Search Query:", "[Search Query]"]
        ):
            # Extract and display search query with better formatting
            # Try different patterns to extract the query
            query = None
            patterns = [
                ("🔍 [Search Query]", ""),
                ("[Search Query]", ""),
                ("Search Query:", ""),
                ("Query:", ""),
            ]

            for pattern, _ in patterns:
                if pattern in line:
                    parts = line.split(pattern, 1)
                    if len(parts) > 1:
                        query = parts[1].strip().strip("'\"").strip()
                        break

            if query:
                # Format the search query nicely
                if len(query) > 80:
                    # For long queries, show beginning and end
                    query = query[:60] + "..." + query[-17:]
                formatted.append("🔍 Search: ", style=self.colors["info"])
                formatted.append(f'"{query}"', style=f"italic {self.colors['text']}")
            else:
                formatted.append("🔍 Search query", style=self.colors["info"])
        else:
            # For long web search results, truncate more aggressively
            max_web_length = min(
                self.max_line_length // 2, 60
            )  # Much shorter for web content
            if len(line) > max_web_length:
                # Try to find a natural break point
                truncated = line[:max_web_length]
                # Look for sentence or phrase endings
                for break_char in [". ", "! ", "? ", ", ", ": "]:
                    last_break = truncated.rfind(break_char)
                    if last_break > max_web_length // 2:
                        truncated = truncated[: last_break + 1]
                        break
                line = truncated + "..."

            formatted.append(line, style=self.colors["text"])

        return formatted

    def _should_filter_content(self, content: str, content_type: str) -> bool:
        """Determine if content should be filtered out to reduce noise."""
        # Never filter important content types
        if content_type in ["status", "presentation", "error"]:
            return False

        # Filter out very long web search results that are mostly noise
        if len(content) > 1000 and self._is_web_search_content(content):
            # Check if it contains mostly URLs and technical details
            url_count = content.count("http")
            technical_indicators = (
                content.count("[")
                + content.count("]")
                + content.count("(")
                + content.count(")")
            )

            # If more than 50% seems to be technical metadata, filter it
            if url_count > 5 or technical_indicators > len(content) * 0.1:
                return True

        return False

    def _should_filter_line(self, line: str) -> bool:
        """Determine if a specific line should be filtered out."""
        # Filter lines that are pure metadata or formatting
        filter_patterns = [
            r"^\s*\([^)]+\)\s*$",  # Lines with just parenthetical citations
            r"^\s*\[[^\]]+\]\s*$",  # Lines with just bracketed metadata
            r"^\s*https?://\S+\s*$",  # Lines with just URLs
            r"^\s*\.\.\.\s*$",  # Lines with just ellipsis
        ]

        for pattern in filter_patterns:
            if re.match(pattern, line):
                return True

        return False

    def _truncate_web_search_content(self, agent_id: str):
        """Truncate web search content when important status updates occur."""
        if agent_id not in self.agent_outputs or not self.agent_outputs[agent_id]:
            return

        # Find web search content and truncate to keep only recent important lines
        content_lines = self.agent_outputs[agent_id]
        web_search_lines = []
        non_web_search_lines = []

        # Separate web search content from other content
        for line in content_lines:
            if self._is_web_search_content(line):
                web_search_lines.append(line)
            else:
                non_web_search_lines.append(line)

        # If there's a lot of web search content, truncate it
        if len(web_search_lines) > self._max_web_search_lines:
            # Keep only the first line (search start) and last few lines (search end/results)
            truncated_web_search = (
                web_search_lines[:1]  # First line (search start)
                + ["🔍 ... (web search content truncated due to status update) ..."]
                + web_search_lines[
                    -(self._max_web_search_lines - 2) :
                ]  # Last few lines
            )

            # Reconstruct the content with truncated web search
            # Keep recent non-web-search content and add truncated web search
            recent_non_web = non_web_search_lines[
                -(max(5, self.max_content_lines - len(truncated_web_search))) :
            ]
            self.agent_outputs[agent_id] = recent_non_web + truncated_web_search

        # Add a status jump indicator only if content was actually truncated
        if len(web_search_lines) > self._max_web_search_lines:
            self.agent_outputs[agent_id].append("⚡  Status updated - jumped to latest")

    def _is_code_content(self, content: str) -> bool:
        """Check if content appears to be code."""
        for pattern in self.code_patterns:
            if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                return True
        return False

    def _apply_syntax_highlighting(self, content: str) -> Text:
        """Apply syntax highlighting to content."""
        try:
            # Try to detect language
            language = self._detect_language(content)

            if language:
                # Use Rich Syntax for highlighting (simplified for now)
                return Text(content, style=f"bold {self.colors['info']}")
            else:
                return Text(content, style=f"bold {self.colors['info']}")
        except:
            return Text(content, style=f"bold {self.colors['info']}")

    def _detect_language(self, content: str) -> Optional[str]:
        """Detect programming language from content."""
        content_lower = content.lower()

        if any(
            keyword in content_lower
            for keyword in ["def ", "import ", "class ", "python"]
        ):
            return "python"
        elif any(
            keyword in content_lower
            for keyword in ["function", "var ", "let ", "const "]
        ):
            return "javascript"
        elif any(keyword in content_lower for keyword in ["<", ">", "html", "div"]):
            return "html"
        elif any(keyword in content_lower for keyword in ["{", "}", "json"]):
            return "json"

        return None

    def _get_status_emoji(self, status: str, activity: str) -> str:
        """Get emoji for agent status."""
        if status == "working":
            return "🔄"
        elif status == "completed":
            if "voted" in activity.lower():
                return "🗳️"  # Vote emoji for any voting activity
            elif "failed" in activity.lower():
                return "❌"
            else:
                return "✅"
        elif status == "waiting":
            return "⏳"
        else:
            return "❓"

    def _get_status_color(self, status: str) -> str:
        """Get color for agent status."""
        status_colors = {
            "working": self.colors["warning"],
            "completed": self.colors["success"],
            "waiting": self.colors["info"],
            "failed": self.colors["error"],
        }
        return status_colors.get(status, self.colors["text"])

    def _get_backend_name(self, agent_id: str) -> str:
        """Get backend name for agent."""
        try:
            if (
                hasattr(self, "orchestrator")
                and self.orchestrator
                and hasattr(self.orchestrator, "agents")
            ):
                agent = self.orchestrator.agents.get(agent_id)
                if (
                    agent
                    and hasattr(agent, "backend")
                    and hasattr(agent.backend, "get_provider_name")
                ):
                    return agent.backend.get_provider_name()
        except:
            pass
        return "Unknown"

    def _create_footer(self) -> Panel:
        """Create the footer panel with status and events."""
        footer_content = Text()

        # Agent status summary
        footer_content.append("📊 Agent Status: ", style=self.colors["primary"])

        status_counts = {}
        for status in self.agent_status.values():
            status_counts[status] = status_counts.get(status, 0) + 1

        status_parts = []
        for status, count in status_counts.items():
            emoji = self._get_status_emoji(status, status)
            status_parts.append(f"{emoji} {status.title()}: {count}")

        footer_content.append(" | ".join(status_parts), style=self.colors["text"])
        footer_content.append("\n")

        # Recent events
        if self.orchestrator_events:
            footer_content.append("📋 Recent Events:\n", style=self.colors["primary"])
            recent_events = self.orchestrator_events[-3:]  # Show last 3 events
            for event in recent_events:
                footer_content.append(f"  • {event}\n", style=self.colors["text"])

        # Log file info
        if self.log_filename:
            footer_content.append(
                f"📁 Log: {self.log_filename}\n", style=self.colors["info"]
            )

        # Interactive mode instructions
        if self._keyboard_interactive_mode and hasattr(self, "_agent_keys"):
            if self._safe_keyboard_mode:
                footer_content.append(
                    "📂 Safe Mode: Keyboard disabled to prevent rendering issues\n",
                    style=self.colors["warning"],
                )
                footer_content.append(
                    f"Output files saved in: {self.output_dir}/",
                    style=self.colors["info"],
                )
            else:
                footer_content.append(
                    "🎮 Live Mode Hotkeys: Press 1-", style=self.colors["primary"]
                )
                footer_content.append(
                    f"{len(self.agent_ids)} to open agent files in editor, 's' for system status",
                    style=self.colors["text"],
                )
                footer_content.append(
                    f"\n📂 Output files saved in: {self.output_dir}/",
                    style=self.colors["info"],
                )

        return Panel(
            footer_content,
            title="[bold]System Status [Press s][/bold]",
            border_style=self.colors["border"],
            box=ROUNDED,
        )

    def update_agent_content(
        self, agent_id: str, content: str, content_type: str = "thinking"
    ):
        """Update content for a specific agent with rich formatting and file output."""

        if agent_id not in self.agent_ids:
            return

        with self._lock:
            # Initialize agent outputs if needed
            if agent_id not in self.agent_outputs:
                self.agent_outputs[agent_id] = []

            # Write content to agent's txt file
            self._write_to_agent_file(agent_id, content, content_type)

            # Check if this is a status-changing content that should trigger web search truncation
            is_status_change = content_type in [
                "status",
                "presentation",
                "tool",
            ] or any(
                keyword in content.lower() for keyword in self._status_change_keywords
            )

            # If status jump is enabled and this is a status change, truncate web search content
            if (
                self._status_jump_enabled
                and is_status_change
                and self._web_search_truncate_on_status_change
                and self.agent_outputs[agent_id]
            ):

                self._truncate_web_search_content(agent_id)

            # Enhanced filtering for web search content
            if self._should_filter_content(content, content_type):
                return

            # Process content with buffering for smoother text display
            self._process_content_with_buffering(agent_id, content, content_type)

            # Categorize updates by priority for layered refresh strategy
            self._categorize_update(agent_id, content_type, content)

            # Schedule update based on priority
            is_critical = content_type in [
                "tool",
                "status",
                "presentation",
                "error",
            ] or any(
                keyword in content.lower() for keyword in self._status_change_keywords
            )
            self._schedule_layered_update(agent_id, is_critical)

    def _process_content_with_buffering(
        self, agent_id: str, content: str, content_type: str
    ):
        """Process content with buffering to accumulate text chunks."""
        # Cancel any existing buffer timer
        if self._buffer_timers.get(agent_id):
            self._buffer_timers[agent_id].cancel()
            self._buffer_timers[agent_id] = None

        # Special handling for content that should be displayed immediately
        if (
            content_type in ["tool", "status", "presentation", "error"]
            or "\n" in content
        ):
            # Flush any existing buffer first
            self._flush_buffer(agent_id)

            # Process multi-line content line by line
            if "\n" in content:
                for line in content.splitlines():
                    if line.strip() and not self._should_filter_line(line):
                        self.agent_outputs[agent_id].append(line)
            else:
                # Add single-line important content directly
                if content.strip():
                    self.agent_outputs[agent_id].append(content.strip())
            return

        # Add content to buffer
        self._text_buffers[agent_id] += content
        buffer = self._text_buffers[agent_id]

        # Simple buffer management - flush when buffer gets too long or after timeout
        if len(buffer) >= self._max_buffer_length:
            self._flush_buffer(agent_id)
            return

        # Set a timer to flush the buffer if no more content arrives
        self._set_buffer_timer(agent_id)

    def _flush_buffer(self, agent_id: str):
        """Flush the buffer for a specific agent."""
        if agent_id in self._text_buffers and self._text_buffers[agent_id]:
            buffer_content = self._text_buffers[agent_id].strip()
            if buffer_content:
                self.agent_outputs[agent_id].append(buffer_content)
            self._text_buffers[agent_id] = ""

        # Cancel any existing timer
        if self._buffer_timers.get(agent_id):
            self._buffer_timers[agent_id].cancel()
            self._buffer_timers[agent_id] = None

    def _set_buffer_timer(self, agent_id: str):
        """Set a timer to flush the buffer after a timeout."""
        if self._shutdown_flag:
            return

        # Cancel existing timer if any
        if self._buffer_timers.get(agent_id):
            self._buffer_timers[agent_id].cancel()

        def timeout_flush():
            with self._lock:
                if agent_id in self._text_buffers and self._text_buffers[agent_id]:
                    self._flush_buffer(agent_id)
                    # Trigger display update
                    self._pending_updates.add(agent_id)
                    self._schedule_async_update(force_update=True)

        self._buffer_timers[agent_id] = threading.Timer(
            self._buffer_timeout, timeout_flush
        )
        self._buffer_timers[agent_id].start()

    def _write_to_agent_file(self, agent_id: str, content: str, content_type: str):
        """Write content to agent's individual txt file."""
        if agent_id not in self.agent_files:
            return

        try:
            file_path = self.agent_files[agent_id]
            timestamp = time.strftime("%H:%M:%S")

            # Check if content contains emojis
            has_emoji = any(
                ord(char) > 127
                and ord(char) in range(0x1F600, 0x1F64F)
                or ord(char) in range(0x1F300, 0x1F5FF)
                or ord(char) in range(0x1F680, 0x1F6FF)
                or ord(char) in range(0x2600, 0x26FF)
                or ord(char) in range(0x2700, 0x27BF)
                for char in content
            )

            if has_emoji:
                # Format with newline and timestamp when emojis are present
                formatted_content = (
                    f"\n[{timestamp}] [{content_type.upper()}] {content}\n"
                )
            else:
                # Regular format without extra newline
                formatted_content = f"{content}"

            # Append to file
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(formatted_content)

        except Exception as e:
            # Handle file write errors gracefully
            pass

    def _write_system_status(self):
        """Write current system status to system status file - shows orchestrator events chronologically by time."""
        if not self.system_status_file:
            return

        try:
            # Clear file and write all orchestrator events chronologically
            with open(self.system_status_file, "w", encoding="utf-8") as f:
                f.write("=== SYSTEM STATUS LOG ===\n\n")

                # Show all orchestrator events in chronological order by time
                if self.orchestrator_events:
                    for event in self.orchestrator_events:
                        f.write(f"  • {event}\n")
                else:
                    f.write("  • No orchestrator events yet\n")

                f.write("\n")

        except Exception as e:
            # Handle file write errors gracefully
            pass

    def update_agent_status(self, agent_id: str, status: str):
        """Update status for a specific agent with rich indicators."""
        if agent_id not in self.agent_ids:
            return

        with self._lock:
            old_status = self.agent_status.get(agent_id, "waiting")
            last_tracked_status = self._last_agent_status.get(agent_id, "waiting")

            # Check if this is a vote-related status change
            current_activity = self.agent_activity.get(agent_id, "")
            is_vote_status = (
                "voted" in status.lower() or "voted" in current_activity.lower()
            )

            # Force update for vote statuses or actual status changes
            should_update = (
                old_status != status and last_tracked_status != status
            ) or is_vote_status

            if should_update:
                # Truncate web search content when status changes for immediate focus on new status
                if (
                    self._status_jump_enabled
                    and self._web_search_truncate_on_status_change
                    and old_status != status
                    and agent_id in self.agent_outputs
                    and self.agent_outputs[agent_id]
                ):

                    self._truncate_web_search_content(agent_id)

                super().update_agent_status(agent_id, status)
                self._last_agent_status[agent_id] = status

                # Mark for priority update - status changes get highest priority
                self._priority_updates.add(agent_id)
                self._pending_updates.add(agent_id)
                self._pending_updates.add("footer")
                self._schedule_priority_update(agent_id)
                self._schedule_async_update(force_update=True)

                # Write system status update
                self._write_system_status()
            elif old_status != status:
                # Update the internal status but don't refresh display if already tracked
                super().update_agent_status(agent_id, status)

    def add_orchestrator_event(self, event: str):
        """Add an orchestrator coordination event with timestamp."""
        with self._lock:
            if self.show_timestamps:
                timestamp = time.strftime("%H:%M:%S")
                formatted_event = f"[{timestamp}] {event}"
            else:
                formatted_event = event

            # Check for duplicate events
            if (
                hasattr(self, "orchestrator_events")
                and self.orchestrator_events
                and self.orchestrator_events[-1] == formatted_event
            ):
                return  # Skip duplicate events

            super().add_orchestrator_event(formatted_event)

            # Only update footer for important events that indicate real status changes
            if any(
                keyword in event.lower() for keyword in self._important_event_keywords
            ):
                # Mark footer for async update
                self._pending_updates.add("footer")
                self._schedule_async_update(force_update=True)
                # Write system status update for important events
                self._write_system_status()

    def display_vote_results(self, vote_results: Dict[str, Any]):
        """Display voting results in a formatted rich panel."""
        if not vote_results or not vote_results.get("vote_counts"):
            return

        # Stop live display temporarily for clean voting results output
        was_live = self.live is not None
        if self.live:
            self.live.stop()
            self.live = None

        vote_counts = vote_results.get("vote_counts", {})
        voter_details = vote_results.get("voter_details", {})
        winner = vote_results.get("winner")
        is_tie = vote_results.get("is_tie", False)

        # Create voting results content
        vote_content = Text()

        # Vote count section
        vote_content.append("📊 Vote Count:\n", style=self.colors["primary"])
        for agent_id, count in sorted(
            vote_counts.items(), key=lambda x: x[1], reverse=True
        ):
            winner_mark = "🏆" if agent_id == winner else "  "
            tie_mark = " (tie-broken)" if is_tie and agent_id == winner else ""
            vote_content.append(
                f"   {winner_mark} {agent_id}: {count} vote{'s' if count != 1 else ''}{tie_mark}\n",
                style=(
                    self.colors["success"]
                    if agent_id == winner
                    else self.colors["text"]
                ),
            )

        # Vote details section
        if voter_details:
            vote_content.append("\n🔍 Vote Details:\n", style=self.colors["primary"])
            for voted_for, voters in voter_details.items():
                vote_content.append(f"   → {voted_for}:\n", style=self.colors["info"])
                for voter_info in voters:
                    voter = voter_info["voter"]
                    reason = voter_info["reason"]
                    vote_content.append(
                        f'     • {voter}: "{reason}"\n', style=self.colors["text"]
                    )

        # Tie-breaking info
        if is_tie:
            vote_content.append(
                "\n⚖️  Tie broken by agent registration order\n",
                style=self.colors["warning"],
            )

        # Summary stats
        total_votes = vote_results.get("total_votes", 0)
        agents_voted = vote_results.get("agents_voted", 0)
        vote_content.append(
            f"\n📈 Summary: {agents_voted}/{total_votes} agents voted",
            style=self.colors["info"],
        )

        # Create and display the voting panel
        voting_panel = Panel(
            vote_content,
            title="[bold bright_cyan]🗳️  VOTING RESULTS[/bold bright_cyan]",
            border_style=self.colors["primary"],
            box=DOUBLE,
            expand=False,
        )

        self.console.print(voting_panel)
        self.console.print()

        # Restart live display if it was active
        if was_live:
            self.live = Live(
                self._create_layout(),
                console=self.console,
                refresh_per_second=self.refresh_rate,
                vertical_overflow="ellipsis",
                transient=False,
            )
            self.live.start()

    async def display_final_presentation(
        self,
        selected_agent: str,
        presentation_stream,
        vote_results: Dict[str, Any] = None,
    ):
        """Display final presentation from winning agent with enhanced orchestrator query support."""
        if not selected_agent:
            return ""

        # Stop live display for clean presentation output
        was_live = self.live is not None
        if self.live:
            self.live.stop()
            self.live = None

        # Create presentation header with orchestrator context
        header_text = Text()
        header_text.append(
            f"🎤 Final Presentation from {selected_agent}",
            style=self.colors["header_style"],
        )
        if vote_results and vote_results.get("vote_counts"):
            vote_count = vote_results["vote_counts"].get(selected_agent, 0)
            header_text.append(
                f" (Selected with {vote_count} votes)", style=self.colors["info"]
            )

        header_panel = Panel(
            Align.center(header_text),
            border_style=self.colors["success"],
            box=DOUBLE,
            title="[bold]Final Presentation[/bold]",
        )

        self.console.print(header_panel)
        self.console.print("=" * 60)

        presentation_content = ""
        chunk_count = 0

        try:
            # Enhanced streaming with orchestrator query awareness
            async for chunk in presentation_stream:
                chunk_count += 1
                content = getattr(chunk, "content", "") or ""
                chunk_type = getattr(chunk, "type", "")
                source = getattr(chunk, "source", selected_agent)

                if content:
                    # Ensure content is a string
                    if isinstance(content, list):
                        content = " ".join(str(item) for item in content)
                    elif not isinstance(content, str):
                        content = str(content)

                    # Accumulate content
                    presentation_content += content

                    # Enhanced formatting for orchestrator query responses
                    if chunk_type == "status":
                        # Status updates from orchestrator query
                        status_text = Text(f"🔄 {content}", style=self.colors["info"])
                        self.console.print(status_text)
                    elif "error" in chunk_type:
                        # Error handling in orchestrator query
                        error_text = Text(f"❌ {content}", style=self.colors["error"])
                        self.console.print(error_text)
                    else:
                        # Main presentation content with simple output
                        self.console.print(content, end="", highlight=False)

                # Handle orchestrator query completion signals
                if chunk_type == "done":
                    completion_text = Text(
                        f"\n✅ Presentation completed by {source}",
                        style=self.colors["success"],
                    )
                    self.console.print(completion_text)
                    break

        except Exception as e:
            # Enhanced error handling for orchestrator queries
            error_text = Text(
                f"❌ Error during final presentation: {e}", style=self.colors["error"]
            )
            self.console.print(error_text)

            # Fallback: try to get content from agent's stored answer
            if hasattr(self, "orchestrator") and self.orchestrator:
                try:
                    status = self.orchestrator.get_status()
                    if selected_agent in status.get("agent_states", {}):
                        stored_answer = status["agent_states"][selected_agent].get(
                            "answer", ""
                        )
                        if stored_answer:
                            fallback_text = Text(
                                f"\n📋 Fallback to stored answer:\n{stored_answer}",
                                style=self.colors["text"],
                            )
                            self.console.print(fallback_text)
                            presentation_content = stored_answer
                except Exception:
                    pass

        self.console.print("\n" + "=" * 60)

        # Show presentation statistics
        if chunk_count > 0:
            stats_text = Text(
                f"📊 Presentation processed {chunk_count} chunks",
                style=self.colors["info"],
            )
            self.console.print(stats_text)

        # Store the presentation content for later re-display
        if presentation_content:
            self._stored_final_presentation = presentation_content
            self._stored_presentation_agent = selected_agent
            self._stored_vote_results = vote_results

        # Restart live display if needed
        if was_live:
            time.sleep(0.5)  # Brief pause before restarting live display

        return presentation_content

    def show_final_answer(
        self,
        answer: str,
        vote_results: Dict[str, Any] = None,
        selected_agent: str = None,
    ):
        """Display the final coordinated answer prominently with voting results, final presentation, and agent selector."""
        # Flush all buffers before showing final answer
        with self._lock:
            self._flush_all_buffers()

        # Stop live display first to ensure clean output
        if self.live:
            self.live.stop()
            self.live = None

        # Auto-get vote results and selected agent from orchestrator if not provided
        if vote_results is None or selected_agent is None:
            try:
                if hasattr(self, "orchestrator") and self.orchestrator:
                    status = self.orchestrator.get_status()
                    vote_results = vote_results or status.get("vote_results", {})
                    selected_agent = selected_agent or status.get("selected_agent")
            except:
                pass

        # Force update all agent final statuses first (show voting results in agent panels)
        with self._lock:
            for agent_id in self.agent_ids:
                self._pending_updates.add(agent_id)
            self._pending_updates.add("footer")
            self._schedule_async_update(force_update=True)

        # Wait for agent status updates to complete
        time.sleep(0.5)
        self._force_display_final_vote_statuses()
        time.sleep(0.5)

        # Display voting results first if available
        if vote_results and vote_results.get("vote_counts"):
            self.display_vote_results(vote_results)
            time.sleep(1.0)  # Allow time for voting results to be visible

        # Now display only the selected agent instead of the full answer
        if selected_agent:
            selected_agent_text = Text(
                f"🏆 Selected agent: {selected_agent}", style=self.colors["success"]
            )
        else:
            selected_agent_text = Text(
                "No agent selected", style=self.colors["warning"]
            )

        final_panel = Panel(
            Align.center(selected_agent_text),
            title="[bold bright_green]🎯 FINAL COORDINATED ANSWER[/bold bright_green]",
            border_style=self.colors["success"],
            box=DOUBLE,
            expand=False,
        )

        self.console.print("\n")
        self.console.print(final_panel)

        # Show which agent was selected
        if selected_agent:
            selection_text = Text()
            selection_text.append(
                f"✅ Selected by: {selected_agent}", style=self.colors["success"]
            )
            if vote_results and vote_results.get("vote_counts"):
                vote_summary = ", ".join(
                    [
                        f"{agent}: {count}"
                        for agent, count in vote_results["vote_counts"].items()
                    ]
                )
                selection_text.append(
                    f"\n🗳️ Vote results: {vote_summary}", style=self.colors["info"]
                )

            selection_panel = Panel(
                selection_text, border_style=self.colors["info"], box=ROUNDED
            )
            self.console.print(selection_panel)

        self.console.print("\n")

        # Display selected agent's final provided answer directly without flush
        # if selected_agent:
        #     selected_agent_answer = self._get_selected_agent_final_answer(selected_agent)
        #     if selected_agent_answer:
        #         # Create header for the final answer
        #         header_text = Text()
        #         header_text.append(f"📝 {selected_agent}'s Final Provided Answer:", style=self.colors['primary'])

        #         header_panel = Panel(
        #             header_text,
        #             title=f"[bold]{selected_agent.upper()} Final Answer[/bold]",
        #             border_style=self.colors['primary'],
        #             box=ROUNDED
        #         )
        #         self.console.print(header_panel)

        #         # Display immediately without any flush effect
        #         answer_panel = Panel(
        #             Text(selected_agent_answer, style=self.colors['text']),
        #             border_style=self.colors['border'],
        #             box=ROUNDED
        #         )
        #         self.console.print(answer_panel)
        #         self.console.print("\n")

        # Display final presentation immediately after voting results
        if selected_agent and hasattr(self, "orchestrator") and self.orchestrator:
            try:
                self._show_orchestrator_final_presentation(selected_agent, vote_results)
                # Add a small delay to ensure presentation completes before agent selector
                time.sleep(1.0)
            except Exception as e:
                # Handle errors gracefully
                error_text = Text(
                    f"❌ Error getting final presentation: {e}",
                    style=self.colors["error"],
                )
                self.console.print(error_text)

        # Show interactive options for viewing agent details (only if not in safe mode)
        if (
            self._keyboard_interactive_mode
            and hasattr(self, "_agent_keys")
            and not self._safe_keyboard_mode
        ):
            self.show_agent_selector()

    def _display_answer_with_flush(self, answer: str):
        """Display answer with flush output effect - streaming character by character."""
        import time
        import sys

        # Use configurable delays
        char_delay = self._flush_char_delay
        word_delay = self._flush_word_delay
        line_delay = 0.2  # Delay at line breaks

        try:
            # Split answer into lines to handle multi-line text properly
            lines = answer.split("\n")

            for line_idx, line in enumerate(lines):
                if not line.strip():
                    # Empty line - just print newline and continue
                    self.console.print()
                    continue

                # Display this line character by character
                for i, char in enumerate(line):
                    # Print character with style, using end='' to stay on same line
                    styled_char = Text(char, style=self.colors["text"])
                    self.console.print(styled_char, end="", highlight=False)

                    # Flush immediately for real-time effect
                    sys.stdout.flush()

                    # Add delays for natural reading rhythm
                    if char in [" ", ",", ";"]:
                        time.sleep(word_delay)
                    elif char in [".", "!", "?", ":"]:
                        time.sleep(word_delay * 2)
                    else:
                        time.sleep(char_delay)

                # Add newline at end of line (except for last line which might not need it)
                if line_idx < len(lines) - 1:
                    self.console.print()  # Newline
                    time.sleep(line_delay)

            # Final newline
            self.console.print()

        except KeyboardInterrupt:
            # If user interrupts, show the complete answer immediately
            self.console.print(f"\n{Text(answer, style=self.colors['text'])}")
        except Exception:
            # On any error, fallback to immediate display
            self.console.print(Text(answer, style=self.colors["text"]))

    def _get_selected_agent_final_answer(self, selected_agent: str) -> str:
        """Get the final provided answer from the selected agent."""
        if not selected_agent:
            return ""

        # First, try to get the answer from orchestrator's stored state
        try:
            if hasattr(self, "orchestrator") and self.orchestrator:
                status = self.orchestrator.get_status()
                if (
                    hasattr(self.orchestrator, "agent_states")
                    and selected_agent in self.orchestrator.agent_states
                ):
                    stored_answer = self.orchestrator.agent_states[
                        selected_agent
                    ].answer
                    if stored_answer:
                        # Clean up the stored answer
                        return (
                            stored_answer.replace("\\", "\n").replace("**", "").strip()
                        )

                # Alternative: try getting from status
                if (
                    "agent_states" in status
                    and selected_agent in status["agent_states"]
                ):
                    agent_state = status["agent_states"][selected_agent]
                    if hasattr(agent_state, "answer") and agent_state.answer:
                        return (
                            agent_state.answer.replace("\\", "\n")
                            .replace("**", "")
                            .strip()
                        )
                    elif isinstance(agent_state, dict) and "answer" in agent_state:
                        return (
                            agent_state["answer"]
                            .replace("\\", "\n")
                            .replace("**", "")
                            .strip()
                        )
        except:
            pass

        # Fallback: extract from agent outputs
        if selected_agent not in self.agent_outputs:
            return ""

        agent_output = self.agent_outputs[selected_agent]
        if not agent_output:
            return ""

        # Look for the most recent meaningful answer content
        answer_lines = []

        # Scan backwards through the output to find the most recent answer
        for line in reversed(agent_output):
            line = line.strip()
            if not line:
                continue

            # Skip status indicators and tool outputs
            if any(
                marker in line
                for marker in ["⚡", "🔄", "✅", "🗳️", "❌", "voted", "🔧", "status"]
            ):
                continue

            # Stop at voting/coordination markers - we want the answer before voting
            if any(
                marker in line.lower()
                for marker in ["final coordinated", "coordination", "voting"]
            ):
                break

            # Collect meaningful content
            answer_lines.insert(0, line)

            # Stop when we have enough content or hit a natural break
            if len(answer_lines) >= 10 or len("\n".join(answer_lines)) > 500:
                break

        # Clean and return the answer
        if answer_lines:
            answer = "\n".join(answer_lines).strip()
            # Remove common formatting artifacts
            answer = answer.replace("**", "").replace("##", "").strip()
            return answer

        return ""

    def _extract_presentation_content(self, selected_agent: str) -> str:
        """Extract presentation content from the selected agent's output."""
        if selected_agent not in self.agent_outputs:
            return ""

        agent_output = self.agent_outputs[selected_agent]
        presentation_lines = []

        # Look for presentation content - typically comes after voting/status completion
        # and may be marked with 🎤 or similar presentation indicators
        collecting_presentation = False

        for line in agent_output:
            # Start collecting when we see presentation indicators
            if "🎤" in line or "presentation" in line.lower():
                collecting_presentation = True
                continue

            # Skip empty lines and status updates
            if not line.strip() or line.startswith("⚡") or line.startswith("🔄"):
                continue

            # Collect meaningful content that appears to be presentation material
            if collecting_presentation and line.strip():
                # Stop if we hit another status indicator or coordination marker
                if any(
                    marker in line
                    for marker in [
                        "✅",
                        "🗳️",
                        "🔄",
                        "❌",
                        "voted",
                        "Final",
                        "coordination",
                    ]
                ):
                    break
                presentation_lines.append(line.strip())

        # If no specific presentation content found, get the most recent meaningful content
        if not presentation_lines and agent_output:
            # Get the last few non-status lines as potential presentation content
            for line in reversed(agent_output[-10:]):  # Look at last 10 lines
                if (
                    line.strip()
                    and not line.startswith("⚡")
                    and not line.startswith("🔄")
                    and not any(
                        marker in line for marker in ["voted", "🗳️", "✅", "status"]
                    )
                ):
                    presentation_lines.insert(0, line.strip())
                    if len(presentation_lines) >= 5:  # Limit to reasonable amount
                        break

        return "\n".join(presentation_lines) if presentation_lines else ""

    def _display_final_presentation_content(
        self, selected_agent: str, presentation_content: str
    ):
        """Display the final presentation content in a formatted panel with orchestrator query enhancements."""
        if not presentation_content.strip():
            return

        # Store the presentation content for later re-display
        self._stored_final_presentation = presentation_content
        self._stored_presentation_agent = selected_agent

        # Create presentation header with orchestrator context
        header_text = Text()
        header_text.append(
            f"🎤 Final Presentation from {selected_agent}",
            style=self.colors["header_style"],
        )

        header_panel = Panel(
            Align.center(header_text),
            border_style=self.colors["success"],
            box=DOUBLE,
            title="[bold]Final Presentation[/bold]",
        )

        self.console.print(header_panel)
        self.console.print("=" * 60)

        # Enhanced content formatting for orchestrator responses
        content_text = Text()

        # Use the enhanced presentation content formatter
        formatted_content = self._format_presentation_content(presentation_content)
        content_text.append(formatted_content)

        # Create content panel with orchestrator-specific styling
        content_panel = Panel(
            content_text,
            title=f"[bold]{selected_agent.upper()} Final Presentation[/bold]",
            border_style=self.colors["primary"],
            box=ROUNDED,
            subtitle=f"[italic]Final presentation content[/italic]",
        )

        self.console.print(content_panel)
        self.console.print("=" * 60)

        # Add presentation completion indicator
        completion_text = Text()
        completion_text.append(
            "✅ Final presentation completed successfully", style=self.colors["success"]
        )
        completion_panel = Panel(
            Align.center(completion_text),
            border_style=self.colors["success"],
            box=ROUNDED,
        )
        self.console.print(completion_panel)

    def _show_orchestrator_final_presentation(
        self, selected_agent: str, vote_results: Dict[str, Any] = None
    ):
        """Show the final presentation from the orchestrator for the selected agent."""
        import time
        import traceback

        try:

            if not hasattr(self, "orchestrator") or not self.orchestrator:
                return

            # Get the final presentation from the orchestrator
            if hasattr(self.orchestrator, "get_final_presentation"):
                import asyncio

                async def _get_and_display_presentation():
                    """Helper to get and display presentation asynchronously."""
                    try:
                        presentation_stream = self.orchestrator.get_final_presentation(
                            selected_agent, vote_results
                        )

                        # Display the presentation
                        await self.display_final_presentation(
                            selected_agent, presentation_stream, vote_results
                        )
                    except Exception as e:
                        raise

                # Run the async function
                import nest_asyncio

                nest_asyncio.apply()

                try:
                    # Create new event loop if needed
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    # Run the coroutine and ensure it completes
                    loop.run_until_complete(_get_and_display_presentation())
                    # Add explicit wait to ensure presentation is fully displayed
                    time.sleep(0.5)
                except Exception as e:
                    # If all else fails, try asyncio.run
                    try:
                        asyncio.run(_get_and_display_presentation())
                        # Add explicit wait to ensure presentation is fully displayed
                        time.sleep(0.5)
                    except Exception as e2:
                        # Last resort: show stored content
                        self._display_final_presentation_content(
                            selected_agent, "Unable to retrieve live presentation."
                        )
            else:
                # Fallback: try to get stored presentation content
                status = self.orchestrator.get_status()
                if selected_agent in status.get("agent_states", {}):
                    stored_answer = status["agent_states"][selected_agent].get(
                        "answer", ""
                    )
                    if stored_answer:
                        self._display_final_presentation_content(
                            selected_agent, stored_answer
                        )
                    else:
                        print("DEBUG: No stored answer found")
                else:
                    print(f"DEBUG: Agent {selected_agent} not found in agent_states")
        except Exception as e:
            # Handle errors gracefully
            error_text = Text(
                f"❌ Error in final presentation: {e}", style=self.colors["error"]
            )
            self.console.print(error_text)

        # except Exception as e:
        #     # Handle errors gracefully - show a simple message
        #     error_text = Text(f"Unable to retrieve final presentation: {str(e)}", style=self.colors['warning'])
        #     self.console.print(error_text)

    def _force_display_final_vote_statuses(self):
        """Force display update to show all agents' final vote statuses."""
        with self._lock:
            # Mark all agents for update to ensure final vote status is shown
            for agent_id in self.agent_ids:
                self._pending_updates.add(agent_id)
            self._pending_updates.add("footer")

            # Force immediate update with final status display
            self._schedule_async_update(force_update=True)

        # Wait longer to ensure all updates are processed and displayed
        import time

        time.sleep(0.3)  # Increased wait to ensure all vote statuses are displayed

    def _flush_all_buffers(self):
        """Flush all text buffers to ensure no content is lost."""
        for agent_id in self.agent_ids:
            if agent_id in self._text_buffers and self._text_buffers[agent_id]:
                buffer_content = self._text_buffers[agent_id].strip()
                if buffer_content:
                    self.agent_outputs[agent_id].append(buffer_content)
                self._text_buffers[agent_id] = ""

    def cleanup(self):
        """Clean up display resources."""
        with self._lock:
            # Flush any remaining buffered content
            self._flush_all_buffers()

            # Stop live display with proper error handling
            if self.live:
                try:
                    self.live.stop()
                except Exception:
                    # Ignore any errors during stop
                    pass
                finally:
                    self.live = None

            # Stop input thread if active
            self._stop_input_thread = True
            if self._input_thread and self._input_thread.is_alive():
                try:
                    self._input_thread.join(timeout=1.0)
                except:
                    pass

            # Restore terminal settings
            try:
                self._restore_terminal_settings()
            except:
                # Ignore errors during terminal restoration
                pass

            # Reset all state flags
            self._agent_selector_active = False
            self._final_answer_shown = False

            # Remove resize signal handler
            try:
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
            except (AttributeError, OSError):
                pass

            # Stop keyboard handler if active
            if self._key_handler:
                try:
                    self._key_handler.stop()
                except:
                    pass

            # Set shutdown flag to prevent new timers
            self._shutdown_flag = True

            # Cancel all debounce timers
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()

            # Cancel all buffer timers
            for timer in self._buffer_timers.values():
                if timer:
                    timer.cancel()
            self._buffer_timers.clear()

            # Cancel batch timer
            if self._batch_timer:
                self._batch_timer.cancel()
                self._batch_timer = None

            # Shutdown executors
            if hasattr(self, "_refresh_executor"):
                self._refresh_executor.shutdown(wait=True)
            if hasattr(self, "_status_update_executor"):
                self._status_update_executor.shutdown(wait=True)

            # Close agent files gracefully
            try:
                for agent_id, file_path in self.agent_files.items():
                    if file_path.exists():
                        with open(file_path, "a", encoding="utf-8") as f:
                            f.write(
                                f"\n=== SESSION ENDED at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                            )
            except:
                pass

    def _schedule_priority_update(self, agent_id: str):
        """Schedule immediate priority update for critical agent status changes."""
        if self._shutdown_flag:
            return

        def priority_update():
            try:
                # Update the specific agent panel immediately
                self._update_agent_panel_cache(agent_id)
                # Trigger immediate display update
                self._update_display_safe()
            except Exception:
                pass

        self._status_update_executor.submit(priority_update)

    def _categorize_update(self, agent_id: str, content_type: str, content: str):
        """Categorize update by priority for layered refresh strategy."""
        if content_type in ["status", "error", "tool"] or any(
            keyword in content.lower()
            for keyword in ["error", "failed", "completed", "voted"]
        ):
            self._critical_updates.add(agent_id)
            # Remove from other categories to avoid duplicate processing
            self._normal_updates.discard(agent_id)
            self._decorative_updates.discard(agent_id)
        elif content_type in ["thinking", "presentation"]:
            if agent_id not in self._critical_updates:
                self._normal_updates.add(agent_id)
                self._decorative_updates.discard(agent_id)
        else:
            # Decorative updates (progress, timestamps, etc.)
            if (
                agent_id not in self._critical_updates
                and agent_id not in self._normal_updates
            ):
                self._decorative_updates.add(agent_id)

    def _schedule_layered_update(self, agent_id: str, is_critical: bool = False):
        """Schedule update using layered refresh strategy with intelligent batching."""
        if is_critical:
            # Critical updates: immediate processing, flush any pending batch
            self._flush_update_batch()
            self._pending_updates.add(agent_id)
            self._schedule_async_update(force_update=True)
        else:
            # Normal updates: intelligent batching based on terminal performance
            perf_tier = self._terminal_performance["performance_tier"]

            if perf_tier == "high":
                # High performance: process immediately
                self._pending_updates.add(agent_id)
                self._schedule_async_update(force_update=False)
            else:
                # Lower performance: use batching
                self._add_to_update_batch(agent_id)

    def _schedule_delayed_update(self):
        """Schedule delayed update for non-critical content."""
        delay = self._debounce_delay * 2  # Double delay for non-critical updates

        def delayed_update():
            if self._pending_updates:
                self._schedule_async_update(force_update=False)

        # Cancel existing delayed timer
        if "delayed" in self._debounce_timers:
            self._debounce_timers["delayed"].cancel()

        self._debounce_timers["delayed"] = threading.Timer(delay, delayed_update)
        self._debounce_timers["delayed"].start()

    def _add_to_update_batch(self, agent_id: str):
        """Add update to batch for efficient processing."""
        self._update_batch.add(agent_id)

        # Cancel existing batch timer
        if self._batch_timer:
            self._batch_timer.cancel()

        # Set new batch timer
        self._batch_timer = threading.Timer(
            self._batch_timeout, self._process_update_batch
        )
        self._batch_timer.start()

    def _process_update_batch(self):
        """Process accumulated batch of updates."""
        if self._update_batch:
            # Move batch to pending updates
            self._pending_updates.update(self._update_batch)
            self._update_batch.clear()

            # Process batch
            self._schedule_async_update(force_update=False)

    def _flush_update_batch(self):
        """Immediately flush any pending batch updates."""
        if self._batch_timer:
            self._batch_timer.cancel()
            self._batch_timer = None

        if self._update_batch:
            self._pending_updates.update(self._update_batch)
            self._update_batch.clear()

    def _schedule_async_update(self, force_update: bool = False):
        """Schedule asynchronous update with debouncing to prevent jitter."""
        current_time = time.time()

        # Frame skipping: if the terminal is struggling, skip updates more aggressively
        if not force_update and self._should_skip_frame():
            return

        # Check if we need a full refresh - less frequent for performance
        if (current_time - self._last_full_refresh) > self._full_refresh_interval:
            with self._lock:
                self._pending_updates.add("header")
                self._pending_updates.add("footer")
                self._pending_updates.update(self.agent_ids)
            self._last_full_refresh = current_time

        # For force updates (status changes, tool content), bypass debouncing completely
        if force_update:
            self._last_update = current_time
            # Submit multiple update tasks for even faster processing
            self._refresh_executor.submit(self._async_update_components)
            return

        # Cancel existing debounce timer if any
        if "main" in self._debounce_timers:
            self._debounce_timers["main"].cancel()

        # Create new debounce timer
        def debounced_update():
            current_time = time.time()
            time_since_last_update = current_time - self._last_update

            if time_since_last_update >= self._update_interval:
                self._last_update = current_time
                self._refresh_executor.submit(self._async_update_components)

        self._debounce_timers["main"] = threading.Timer(
            self._debounce_delay, debounced_update
        )
        self._debounce_timers["main"].start()

    def _should_skip_frame(self):
        """Determine if we should skip this frame update to maintain stability."""
        # Skip frames more aggressively for macOS terminals
        term_type = self._terminal_performance["type"]
        if term_type in ["iterm", "macos_terminal"]:
            # Skip if we have too many dropped frames
            if self._dropped_frames > 1:
                return True
            # Skip if refresh executor is overloaded
            if (
                hasattr(self._refresh_executor, "_work_queue")
                and self._refresh_executor._work_queue.qsize() > 2
            ):
                return True

        return False

    def _async_update_components(self):
        """Asynchronously update only the components that have changed."""
        start_time = time.time()

        try:
            updates_to_process = None

            with self._lock:
                if self._pending_updates:
                    updates_to_process = self._pending_updates.copy()
                    self._pending_updates.clear()

            if not updates_to_process:
                return

            # Update components in parallel
            futures = []

            for update_id in updates_to_process:
                if update_id == "header":
                    future = self._refresh_executor.submit(self._update_header_cache)
                    futures.append(future)
                elif update_id == "footer":
                    future = self._refresh_executor.submit(self._update_footer_cache)
                    futures.append(future)
                elif update_id in self.agent_ids:
                    future = self._refresh_executor.submit(
                        self._update_agent_panel_cache, update_id
                    )
                    futures.append(future)

            # Wait for all updates to complete
            for future in futures:
                future.result()

            # Update display with new layout
            self._update_display_safe()

        except Exception:
            # Silently handle errors to avoid disrupting display
            pass
        finally:
            # Performance monitoring
            refresh_time = time.time() - start_time
            self._refresh_times.append(refresh_time)
            self._monitor_performance()

    def _update_header_cache(self):
        """Update the cached header panel."""
        try:
            self._header_cache = self._create_header()
        except:
            pass

    def _update_footer_cache(self):
        """Update the cached footer panel."""
        try:
            self._footer_cache = self._create_footer()
        except:
            pass

    def _update_agent_panel_cache(self, agent_id: str):
        """Update the cached panel for a specific agent."""
        try:
            self._agent_panels_cache[agent_id] = self._create_agent_panel(agent_id)
        except:
            pass

    def _refresh_display(self):
        """Override parent's refresh method to use async updates."""
        # Only refresh if there are actual pending updates
        # This prevents unnecessary full refreshes
        if self._pending_updates:
            self._schedule_async_update()

    def _is_content_important(self, content: str, content_type: str) -> bool:
        """Determine if content is important enough to trigger a display update."""
        # Always important content types
        if content_type in self._important_content_types:
            return True

        # Check for status change indicators in content
        if any(keyword in content.lower() for keyword in self._status_change_keywords):
            return True

        # Check for error indicators
        if any(
            keyword in content.lower()
            for keyword in ["error", "exception", "failed", "timeout"]
        ):
            return True

        return False

    def set_status_jump_enabled(self, enabled: bool):
        """Enable or disable status jumping functionality.

        Args:
            enabled: Whether to enable status jumping
        """
        with self._lock:
            self._status_jump_enabled = enabled

    def set_web_search_truncation(self, enabled: bool, max_lines: int = 3):
        """Configure web search content truncation on status changes.

        Args:
            enabled: Whether to enable web search truncation
            max_lines: Maximum web search lines to keep when truncating
        """
        with self._lock:
            self._web_search_truncate_on_status_change = enabled
            self._max_web_search_lines = max_lines

    def set_flush_output(
        self, enabled: bool, char_delay: float = 0.03, word_delay: float = 0.08
    ):
        """Configure flush output settings for final answer display.

        Args:
            enabled: Whether to enable flush output effect
            char_delay: Delay between characters in seconds
            word_delay: Extra delay after punctuation in seconds
        """
        with self._lock:
            self._enable_flush_output = enabled
            self._flush_char_delay = char_delay
            self._flush_word_delay = word_delay


# Convenience function to check Rich availability
def is_rich_available() -> bool:
    """Check if Rich library is available."""
    return RICH_AVAILABLE


# Factory function for creating display
def create_rich_display(agent_ids: List[str], **kwargs) -> RichTerminalDisplay:
    """Create a RichTerminalDisplay instance.

    Args:
        agent_ids: List of agent IDs to display
        **kwargs: Configuration options for RichTerminalDisplay

    Returns:
        RichTerminalDisplay instance

    Raises:
        ImportError: If Rich library is not available
    """
    return RichTerminalDisplay(agent_ids, **kwargs)
