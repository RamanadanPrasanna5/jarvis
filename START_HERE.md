# JARVIS — your personal desktop assistant

A Windows desktop assistant with a dark dashboard, local chat history, tasks, reminders, saved memory, push-to-talk, spoken replies, and selected PC commands. General AI conversation uses a separately installed local Ollama model.

## Start on your Windows PC

1. Extract this ZIP completely to a new folder, such as `Documents\JARVIS`. Do not run inside the ZIP viewer.
2. Install **Python 3.12 (64-bit)** from https://www.python.org/downloads/ if you do not have it. Select **Add python.exe to PATH** during installation.
3. Double-click **setup_windows.bat**. Internet is needed to install the optional desktop window package.
4. Double-click **START_JARVIS.bat**. The first screen works immediately for tasks, reminders, memory and commands.
5. For general AI chat, complete the Ollama steps below. No API key is required.

If the native window cannot start, use **START_BROWSER.bat**. It shows the same app through a local browser page. Keep its terminal open. Native mode requires Microsoft Edge WebView2 Runtime: https://developer.microsoft.com/microsoft-edge/webview2/.

## Turn on AI chat

1. Install Ollama for Windows: https://ollama.com/download.
2. Open Terminal or PowerShell and run:

   ```powershell
   ollama pull qwen2.5:3b
   ```

3. Keep Ollama running. Open JARVIS → **Settings** → **Check connection**.
4. Leave the model name as `qwen2.5:3b`, or select an installed local model. Click **Save settings**.
5. Ask a question, for example: “Explain Angular services in Tamil.”

The model is a separate download, not included in the ZIP. Download time, memory use and response speed depend on your PC. If you use a different model, enter its exact local name. Cloud tags are not supported. Ollama can take a while to load the model on the first question. JARVIS waits up to three minutes; smaller models can be more practical on slower PCs. Offline built-in commands continue working if Ollama is unavailable.

## Try these commands

| Type this | What happens |
|---|---|
| `help` | Shows supported commands |
| `add task Finish Angular homework` | Saves a task |
| `remind me in 10 minutes to drink water` | Saves a relative reminder |
| `remind me at 7 pm to go to the gym` | Uses the next occurrence of 7 PM |
| `remind me tomorrow at 9 am to review notes` | Saves tomorrow's reminder |
| `show my tasks` | Shows unfinished tasks and due dates |
| `remember I prefer Tamil explanations` | Saves memory used by local AI chat |
| `show my memories` | Lists saved memories |
| `open calculator` | Opens Windows Calculator |
| `open notepad` | Opens Notepad |
| `open VS Code` / `open Chrome` | Opens the app if found in its usual folder |
| `open downloads` / `open documents` | Opens the default user folder |
| `open YouTube` / `open Gmail` / `open GitHub` | Opens the website in your browser |
| `search for ASP.NET Core tutorials` | Opens a Google search in your browser |
| `what time is it?` | Reads your PC's local date and time |

You can also use the task, reminder, memory and settings forms. Click a task checkbox to complete it; click again to reopen it. Delete is immediate. Chat clearing asks first and preserves tasks and memory.

## Voice

- Click the microphone button and speak a short English sentence. It listens for up to about 12 seconds.
- The transcript appears in the input box. Review it, then press Enter to send. It does not automatically run a recognized command.
- Enable **Read responses aloud** in Settings for Windows text-to-speech. Long replies are limited to the first 2,500 characters for speech; the full reply stays in chat.
- Windows **Settings → Privacy & security → Microphone → Let desktop apps access your microphone** must allow access.
- Install an English speech recognition pack through Windows language/speech settings. Choose a working default microphone and speaker.
- Tamil text chat is supported. Tamil speech depends on Windows having a compatible installed voice; English is the current microphone recognition language.
- Wake-word detection and continuous listening are not included in V1.

## Reminders

Reminders appear as an in-app dialog. Enable spoken replies for a spoken alert. **JARVIS must be running, the interface must remain open, and your PC must be awake.** Browser tabs may delay timers when hidden. This is not a Windows background notification service. It cannot wake your PC or alert you while shut down. Overdue, unacknowledged reminders appear when the app is reopened. Dismissing an alert acknowledges it but does not complete its task. An acknowledged reminder does not repeat.

## Your information

Data lives at `%LOCALAPPDATA%\JarvisDesktop\jarvis.sqlite3`. The exact path is shown in Settings. Close JARVIS before copying this file as a backup or restoring it. Deleting it while JARVIS is closed resets the workspace. Keep only one JARVIS instance open.

Chat, tasks, memory and settings are local SQLite data and are **not encrypted**. Use Windows account security; do not store passwords or secrets. For AI chat, the latest 16 chat messages and up to 30 saved memories are sent to Ollama at `127.0.0.1:11434`. No cloud AI endpoint or API key is configured. The installer and model download require internet. Explicit browser commands contact the websites you request. Windows speech uses System.Speech; JARVIS does not record audio files.

The HTTP server only binds to the local loopback address, validates its Host and Origin, and requires a random session token for all data APIs. This protects against ordinary cross-site requests; it is not a defense against malware or another process running under your Windows account. Model responses cannot run shell commands. Only explicit supported commands launch apps.

## What V1 does not include

No automatic Windows startup, system tray/background service, Gmail reading or sending, calendar sync, live web-result retrieval into chat, screen capture, arbitrary shell execution, or wake-word activation. Opening Gmail launches its website; it does not connect your mailbox. The original LiveKit project and credentials are not included in this separate desktop version.

## Troubleshooting

| Problem | Fix |
|---|---|
| Python not found | Install Python 3.12 with PATH enabled, then reopen the folder and run setup |
| Native window fails | Install WebView2 or use START_BROWSER.bat |
| Ollama is not connected | Launch Ollama; use Check connection; run the model download command |
| Model not found | Model name must exactly match a downloaded model shown by `ollama list` |
| AI response is slow | First load can be slow. Try a smaller locally installed model |
| Microphone doesn't work | Enable desktop microphone permission, install English speech recognition, choose a default input |
| No reminder when app is closed | Keep JARVIS open and the PC awake; missed reminders show at next launch |
| VS Code / Chrome not found | The launcher checks standard installation folders; unusual installations are not supported yet |
| Downloads / Documents path is wrong | Redirected or OneDrive-managed folders may differ from the default paths |

## Bro — quick Tamil guide

1. ZIP file-a **Extract All** பண்ணு.
2. Python 3.12 install பண்ணி, **setup_windows.bat** open பண்ணு.
3. Setup முடிந்ததும் **START_JARVIS.bat** double-click பண்ணு.
4. AI-யுடன் பேச Ollama install பண்ணி `ollama pull qwen2.5:3b` run பண்ணு.
5. JARVIS Settings-ல் **Check connection** பண்ணு. Response language-ஐ **Tamil** ஆக மாற்றலாம்.
6. Reminder வர app open-ஆவும் PC awake-ஆவும் இருக்கணும்.

This is source code with setup/launch scripts, not a compiled Windows EXE. Windows microphone, speakers, native shell and installed-app paths need verification on your own PC. See TEST_REPORT.md for what was tested here.
