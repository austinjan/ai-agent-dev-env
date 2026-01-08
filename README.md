# ai-agent-dev-env

This document defines a **strict, reproducible development environment** for AI agent development.  
The goal is to ensure **consistent runtime behavior**, predictable debugging, and reliable remote support across teams and platforms.

> **Principle:**  
> All agent execution and runtime tools run on **Linux (WSL / native Linux / macOS)**.  
> **Windows is editor/UI only.**

### Windows
- Windows **must** use **WSL 2**
- WSL is mandatory to align behavior with Linux/macOS
- Projects must live inside the Linux filesystem (`/home/...`)

### Linux / macOS
- Native Linux and macOS are first-class environments
- No special compatibility layer required



### Windows (UI / Editor only)

| Tool | Windows | WSL | Comment |
| --- | --- | --- | --- |
| Zed Editor | ✔️ | ❌ | Remote editing into WSL |
| antigravity | ✔️ | ❌ | Demo / teaching only (optional) |
| gh (GitHub CLI) | ⚠️ | ❌ | Optional, read-only use |

⚠️ Allowed but **not authoritative**

---

### Linux / macOS / WSL (Runtime & Execution)

| Tool | Windows | WSL / Linux / macOS | Comment |
| --- | --- | --- | --- |
| Node.js | ❌ | ✔️ | **Only runtime environment** |
| Python 3.10+ | ❌ | ✔️ | **Only runtime environment** |
| uv | ❌ | ✔️ | Python package manager |
| Claude Code | ❌ | ✔️ | Coding agent |
| Codex | ❌ | ✔️ | Coding agent |
| Gemini-CLI | ❌ | ✔️ | Coding agent |
| gh (GitHub CLI) | ⚠️ | ✔️ | Primary Git operations |


## Truble Shooting
- WSL 要安裝 wslu 來開啟 windows 的 browser 不然要開瀏覽器的驗證會卡住
```bash
$ sudo apt install wslu
export BROWSER=wslview # 建議寫到 .bashrc
```
- Fix keyring
```bash
sudo apt install libsecret-1-0
```


Run script `scripts/env_doctor.py` to check current environment
