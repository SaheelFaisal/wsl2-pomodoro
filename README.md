# WSL2 Pomodoro Timer

A premium, interactive Terminal User Interface (TUI) Pomodoro timer optimized to run inside a **WSL2 (Ubuntu)** terminal, built with Python and the `textual` framework. 

It features dynamic theme colors matching the current timer phase, reactive progress indicators, responsive keyboard shortcuts, and a background bridge that triggers native **Windows 10/11 Desktop Toast notifications** when a timer expires.

---

## 🚀 Installation & Running

Follow these two commands to install the required dependencies and start the application:

```bash
pip install -r requirements.txt
python3 pomodoro.py
```

> [!NOTE]
> On modern Debian/Ubuntu-based WSL2 systems, if python-venv is not installed, you can install textual directly to your user space using:
> `python3 -m pip install --user textual`

---

## 🎨 Visual & Theme States

The TUI features a clean card design centered in the terminal window. The double-border and text accents shift dynamically based on the active timer phase:
* 🟢 **Work Phase**: Vibrant Emerald Green border and text to focus your mind.
* 🔵 **Short Break**: Sky Blue border and text for a quick breather.
* 🟡 **Long Break**: Amber Orange border and text for a deeper rest.

---

## 🔄 Pomodoro Cycle Mechanics

The application implements standard Pomodoro scheduling rules:
* **Focus Loop**: A long break automatically triggers after **4 completed focus (work) sessions**.
* **Transition Flow**:
  * Work Session 1 ➜ Short Break
  * Work Session 2 ➜ Short Break
  * Work Session 3 ➜ Short Break
  * Work Session 4 ➜ **Long Break**
* **Cycle Tracking**: Solid dots (`●`) represent completed work sessions, while empty dots (`○`) show remaining sessions in the current 4-session loop (e.g. `Sessions: ● ● ○ ○`).
* **Timer Completion**: When a timer hits `00:00`, a native Windows toast notification is dispatched via a background thread on the Windows host desktop, and the timer automatically pauses so you can control when to start your next session.

---

## ⚙️ Customization & CLI Flags

The timer intervals can be customized at launch using either short or long command-line flags:

| Short Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `-w` | `--work` | Work session duration in minutes | `25` |
| `-b` | `--short-break` | Short break duration in minutes | `5` |
| `-l` | `--long-break` | Long break duration in minutes | `15` |
| `-h` | `--help` | Display the auto-generated help documentation and exit | - |

### Examples:
```bash
# Run a 50-minute work session, 10-minute short break, and 20-minute long break:
python3 pomodoro.py -w 50 -b 10 -l 20

# Check option options using the standard help flag:
python3 pomodoro.py --help
```

---

## ⌨️ Keyboard Controls

The TUI listens to non-blocking, responsive key presses to manage the active session:

* **`[Space]`** — **Pause / Resume**: Toggle the active countdown timer.
* **`[R]`** — **Reset**: Revert the active timer phase back to its full starting duration.
* **`[S]`** — **Skip**: Skip the current phase immediately (skipping a Work session increments the session counter to keep the 4-session cycle aligned, preventing double long-break bugs).
* **`[Q]`** — **Quit**: Safely exit the application.

---

## 🌉 WSL2-to-Windows Notification Bridge

Standard Linux desktop notifications (D-Bus/notify-send) fail inside WSL2 because they are not connected to the Windows host GUI. 

This app solves the problem by invoking a non-blocking background thread that communicates with the Windows host via `powershell.exe`. It calls native Windows Runtime APIs using inline Toast XML (`ToastText02`) and the standard Windows PowerShell AppUserModelID (`{1AC14E77-C67E-4335-A8F8-212FF3EFCF85}`). 

```python
# The notification executes cleanly on Windows without external modules:
subprocess.run(["powershell.exe", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```
Because this subprocess runs in a background daemon thread, your terminal clock continues ticking smoothly at 1-second intervals without stuttering or stalling while PowerShell launches.
