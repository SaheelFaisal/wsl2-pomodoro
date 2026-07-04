#!/usr/bin/env python3
"""
Pomodoro Timer TUI for WSL2 (Ubuntu)
Author: Antigravity Code Assistant
Description: A modern Terminal User Interface (TUI) Pomodoro Timer built with 
             Textual. Optimized for WSL2 with non-blocking native Windows notifications.
"""

import argparse
import subprocess
import sys
import threading
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, ProgressBar


class PomodoroApp(App):
    """
    Textual TUI Application for the Pomodoro Timer.
    """

    # Custom styling for rich aesthetics, using tailored HSL color codes and responsive layouts.
    CSS = """
    Screen {
        background: #121214;
        align: center middle;
    }

    #timer-container {
        width: 56;
        height: 20;
        border: double #3f3f46;
        background: #18181b;
        padding: 2 4;
        align: center middle;
    }

    /* Phase-dependent borders for visual feedback */
    #timer-container.work-phase {
        border: double #10b981; /* Emerald Green */
    }

    #timer-container.short-break-phase {
        border: double #3b82f6; /* Sky Blue */
    }

    #timer-container.long-break-phase {
        border: double #f59e0b; /* Amber Orange */
    }

    #phase-title {
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
        height: 2;
    }

    #phase-title.work-phase {
        color: #10b981;
    }

    #phase-title.short-break-phase {
        color: #3b82f6;
    }

    #phase-title.long-break-phase {
        color: #f59e0b;
    }

    #time-display {
        content-align: center middle;
        text-style: bold;
        height: 5;
        background: #27272a;
        border: round #52525b;
        margin-bottom: 1;
        color: #ffffff;
    }

    #progress-bar {
        width: 100%;
        height: 1;
        margin-bottom: 2;
    }

    #progress-bar > .bar--bar {
        background: #3f3f46;
    }

    #timer-container.work-phase #progress-bar > .bar--complete {
        background: #10b981;
    }

    #timer-container.short-break-phase #progress-bar > .bar--complete {
        background: #3b82f6;
    }

    #timer-container.long-break-phase #progress-bar > .bar--complete {
        background: #f59e0b;
    }

    #status-text {
        content-align: center middle;
        height: 1;
        color: #a1a1aa;
        margin-bottom: 1;
        text-style: italic;
    }

    #session-dots {
        content-align: center middle;
        height: 1;
        color: #e4e4e7;
        text-style: bold;
    }
    """

    # Non-blocking keybinds mapping keyboard controls to TUI actions
    BINDINGS = [
        ("space", "toggle_timer", "Pause/Resume"),
        ("r", "reset_timer", "Reset"),
        ("s", "skip_session", "Skip"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, work_mins=25, short_break_mins=5, long_break_mins=15):
        super().__init__()
        # Store durations in seconds
        self.work_duration = work_mins * 60
        self.short_break_duration = short_break_mins * 60
        self.long_break_duration = long_break_mins * 60

        # State initialization
        self.current_phase = "work"  # "work", "short_break", "long_break"
        self.time_left = self.work_duration
        self.total_duration = self.work_duration
        self.is_timer_running = False
        self.completed_work_sessions = 0

    def compose(self) -> ComposeResult:
        """Create the TUI layout."""
        yield Header(show_clock=True)
        with Container(id="timer-container"):
            yield Static("WORK SESSION", id="phase-title")
            yield Static("00:00", id="time-display")
            yield ProgressBar(id="progress-bar", show_eta=False, show_percentage=False)
            yield Static("Paused. Press \\[Space] to Start", id="status-text")
            yield Static("Sessions: ○ ○ ○ ○", id="session-dots")
        yield Footer()

    def on_mount(self) -> None:
        """Start the tick interval and perform initial UI render."""
        self.update_ui_state()
        self.set_interval(1.0, self.tick)

    def tick(self) -> None:
        """Periodic 1-second countdown tick."""
        if not self.is_timer_running:
            return

        if self.time_left > 0:
            self.time_left -= 1
            self.update_ui_time()
        else:
            self.transition_phase()

    def transition_phase(self) -> None:
        """Handle timer completion and transition to the next phase."""
        # Trigger native Windows notification before shifting durations
        self.send_windows_notification()

        if self.current_phase == "work":
            self.completed_work_sessions += 1
            if self.completed_work_sessions % 4 == 0:
                self.current_phase = "long_break"
                self.time_left = self.long_break_duration
            else:
                self.current_phase = "short_break"
                self.time_left = self.short_break_duration
        else:
            self.current_phase = "work"
            self.time_left = self.work_duration

        self.total_duration = self.time_left
        self.is_timer_running = False  # Pause timer to let user review transitions
        self.update_ui_state()

    def action_toggle_timer(self) -> None:
        """Play/Pause the timer."""
        self.is_timer_running = not self.is_timer_running
        self.update_ui_state()

    def action_reset_timer(self) -> None:
        """Reset the current phase to its full duration."""
        self.is_timer_running = False
        self.time_left = self.total_duration
        self.update_ui_state()

    def action_skip_session(self) -> None:
        """Skip the current session phase immediately."""
        self.is_timer_running = False
        
        # Determine next phase on skip
        if self.current_phase == "work":
            # Increment session count to keep the cycle aligned
            self.completed_work_sessions += 1
            if self.completed_work_sessions % 4 == 0:
                self.current_phase = "long_break"
                self.time_left = self.long_break_duration
            else:
                self.current_phase = "short_break"
                self.time_left = self.short_break_duration
        else:
            self.current_phase = "work"
            self.time_left = self.work_duration

        self.total_duration = self.time_left
        self.update_ui_state()

    def update_ui_time(self) -> None:
        """Refresh the time display string and update the progress bar value."""
        mins = self.time_left // 60
        secs = self.time_left % 60
        time_str = f"{mins:02d}:{secs:02d}"

        self.query_one("#time-display", Static).update(time_str)

        # Calculate progress completion value
        progress_val = self.total_duration - self.time_left
        self.query_one("#progress-bar", ProgressBar).update(progress=progress_val)

    def update_ui_state(self) -> None:
        """Update phase labels, classes (colors), status descriptions, and trackers."""
        container = self.query_one("#timer-container", Container)
        phase_title = self.query_one("#phase-title", Static)
        status_text = self.query_one("#status-text", Static)
        session_dots = self.query_one("#session-dots", Static)

        # Remove old phase-specific styling classes
        container.remove_class("work-phase", "short-break-phase", "long-break-phase")
        phase_title.remove_class("work-phase", "short-break-phase", "long-break-phase")

        # Configure new visual styling based on active phase
        if self.current_phase == "work":
            phase_class = "work-phase"
            title_text = f"WORK SESSION #{self.completed_work_sessions + 1}"
        elif self.current_phase == "short_break":
            phase_class = "short-break-phase"
            title_text = "SHORT BREAK"
        else:
            phase_class = "long-break-phase"
            title_text = "LONG BREAK"

        container.add_class(phase_class)
        phase_title.add_class(phase_class)
        phase_title.update(title_text)

        # Update running state message
        if self.is_timer_running:
            status_text.update("Running... Press \\[Space] to Pause")
        else:
            status_text.update("Paused. Press \\[Space] to Resume")

        # Render session dot indicators (showing completed versus remaining in round of 4)
        completed_mod = self.completed_work_sessions % 4
        if self.completed_work_sessions > 0 and completed_mod == 0:
            dots_str = "Completed: ● ● ● ● (Round Finished)"
        else:
            dots = ["●"] * completed_mod + ["○"] * (4 - completed_mod)
            dots_str = f"Sessions: {' '.join(dots)}"
        session_dots.update(dots_str)

        # Refresh static values
        pb = self.query_one("#progress-bar", ProgressBar)
        pb.update(total=self.total_duration)
        self.update_ui_time()

    def send_windows_notification(self) -> None:
        """Triggers a native Windows host notification via a background thread."""
        title = "Pomodoro Timer"
        if self.current_phase == "work":
            message = "Work session complete! Time for a short break."
            if (self.completed_work_sessions + 1) % 4 == 0:
                message = "Work session complete! Time for a long break."
        else:
            message = "Break is over! Ready to focus?"

        # Invoke notification asynchronously in a background thread
        # This keeps the TUI interface running perfectly smooth without freezing
        threading.Thread(
            target=self._run_notification_bridge,
            args=(title, message),
            daemon=True
        ).start()

    def _run_notification_bridge(self, title: str, message: str) -> None:
        """Invokes powershell.exe with a Windows Runtime Toast XML command."""
        # Double-escape single quotes for safe embedding in the PowerShell script block
        escaped_title = title.replace("'", "''")
        escaped_message = message.replace("'", "''")

        # Standard Windows PowerShell application identifier used to trigger toasts
        aumid = "{1AC14E77-C67E-4335-A8F8-212FF3EFCF85}\\WindowsPowerShell\\v1.0\\powershell.exe"

        ps_script = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
            "$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$toastXml = [xml]$template.GetXml(); "
            f"$toastXml.GetElementsByTagName('text')[0].AppendChild($toastXml.CreateTextNode('{escaped_title}')) | Out-Null; "
            f"$toastXml.GetElementsByTagName('text')[1].AppendChild($toastXml.CreateTextNode('{escaped_message}')) | Out-Null; "
            "$xml = New-Object Windows.Data.Xml.Dom.XmlDocument; "
            "$xml.LoadXml($toastXml.OuterXml); "
            "$toast = New-Object Windows.UI.Notifications.ToastNotification $xml; "
            f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{aumid}').Show($toast);"
        )

        try:
            # Explicit delivery pattern using subprocess.run with powershell.exe
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            # Fail silently if not on WSL2 or if powershell.exe is unavailable
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Pomodoro Timer optimized for WSL2 Terminal Environments."
    )
    parser.add_argument(
        "-w", "--work",
        type=int,
        default=25,
        help="Work session duration in minutes (default: 25)"
    )
    parser.add_argument(
        "-b", "--short-break",
        type=int,
        default=5,
        help="Short break duration in minutes (default: 5)"
    )
    parser.add_argument(
        "-l", "--long-break",
        type=int,
        default=15,
        help="Long break duration in minutes (default: 15)"
    )
    args = parser.parse_args()

    app = PomodoroApp(
        work_mins=args.work,
        short_break_mins=args.short_break,
        long_break_mins=args.long_break
    )
    app.run()


if __name__ == "__main__":
    main()
