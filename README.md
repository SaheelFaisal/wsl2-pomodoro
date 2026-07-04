# WSL2 Pomodoro Timer

A premium, interactive Terminal User Interface (TUI) Pomodoro timer optimized for WSL2 (Ubuntu) using Python and the `textual` library.

## Setup & Running

Install dependencies and run the timer:
```bash
pip install -r requirements.txt
python3 pomodoro.py
```

## Features

- **Dynamic Visuals**: Beautiful colors matching your current state (Green for Work focus, Blue/Amber for breaks).
- **WSL2 Toast Notifications**: Instantly sends native Windows desktop toast alerts when a timer ends (using non-blocking PowerShell).
- **Responsive Controls**:
  - `[Space]` Pause / Resume
  - `[R]` Reset current session duration
  - `[S]` Skip the active session
  - `[Q]` Exit
- **Interval Customization**: Pass optional parameters to configure session times:
  ```bash
  python3 pomodoro.py --work 50 --short-break 10 --long-break 20
  ```
