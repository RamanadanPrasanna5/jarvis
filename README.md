# JARVIS Desktop V1

Start with **START_HERE.md** for Windows setup and usage.

## Structure

- `main.py`: native pywebview window and dependency-free browser fallback.
- `jarvis/server.py`: loopback HTTP API, session and origin checks, input validation.
- `jarvis/storage.py`: SQLite persistence under the user's local data directory.
- `jarvis/assistant.py`: explicit commands, reminder parsing, local Ollama chat adapter.
- `jarvis/voice.py` and `scripts/voice.ps1`: Windows offline speech bridge.
- `ui/`: self-contained HTML, CSS and JavaScript. No CDN resources or UI build step.
- `tests/test_core.py`: standard-library unit and HTTP integration checks.

## Run or develop

Python 3.10+ is required. Python 3.12 is recommended for native Windows dependencies. The browser mode needs only Python's standard library:

```sh
python main.py --browser
```

For the native shell, install `requirements.txt` first. Linux native window dependencies are not included; browser mode is the portable development option. Windows speech/app launching require Windows.

```sh
python -m unittest discover -s tests -v
python -m compileall -q jarvis main.py
```

`JARVIS_DATA_DIR` selects an alternate data folder for tests. `--headless --port 8765` starts a test server without a window. The default launch chooses a free port. Test data is not shipped.

## Design decisions

The local language model produces chat text only. It cannot call actions or execute its own output. Actual app actions come from the explicit command router. This keeps permissions and results predictable. Voice transcriptions are user-reviewable before submission. Responses and user data are inserted into the interface using DOM text nodes, not HTML.

User facts and recent history are added to the model context. Explicit commands are supported in English; AI reply language can be English, Tamil, or both. No model weights, secrets, cloud accounts or LiveKit credentials are bundled.

## API references used

- Ollama chat: https://docs.ollama.com/api/chat
- pywebview installation: https://pywebview.flowrl.com/guide/installation.html
- pywebview usage: https://pywebview.flowrl.com/guide/usage
- Microsoft System.Speech recognition: https://learn.microsoft.com/en-us/dotnet/api/system.speech.recognition.speechrecognitionengine.recognize

The AI request contract is verified against the documented `/api/chat` endpoint with `stream: false`. Live model inference requires an installed local Ollama model and was not exercised in the Linux build environment.
