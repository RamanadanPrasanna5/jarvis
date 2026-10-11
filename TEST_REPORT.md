# JARVIS Desktop V1 — verification

Verified in the Linux build environment on 11 October 2026.

## Passed

10 automated standard-library tests cover:

- Relative reminder units, next-day rollover, 12 AM handling and invalid time rejection.
- Chat, tasks and Tamil memory persistence across Store instances.
- Recovery of overdue reminders and explicit acknowledgement.
- Rejection of arbitrary command strings without starting a process.
- An honest message when the local AI service is unavailable.
- The Ollama chat request/response contract using a mocked service, including memory and recent messages.
- Session-token requirements on the HTTP API.
- Cross-origin and invalid Host rejection, plus unknown file paths.
- Invalid task and model settings input.
- Task creation, completion, deletion and chat clearing while preserving tasks.

A live HTTP smoke check also passed for the HTML/CSS/JavaScript routes, unique element IDs, script selectors, a chat command and saved task state. Python compilation and JavaScript syntax checking passed. The database connection lifecycle explicitly closes each connection after its transaction.

## Not verified in this environment

- Real Windows microphone recognition, speech synthesis and native WebView2 window.
- Launching installed Windows applications and Windows batch setup scripts.
- Real Ollama model inference, model speed or Tamil answer quality. Model weights are not bundled.
- Browser rendering and end-to-end UI clicking. A Chromium download was attempted but failed, so no visual QA pass is claimed.

The release is runnable source with Windows setup scripts. It is not a compiled installer. Begin with START_HERE.md. Basic commands require no AI service; AI conversation requires Ollama and a downloaded local model.
