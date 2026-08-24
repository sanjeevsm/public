# iLab+ — AI Interview Simulator

A short summary of the primary technologies used: Frontend: Jinja2 + Vanilla JS · Backend: Flask · Desktop GUI: Tkinter

iLab+ is an AI-powered technical interview simulator that generates multiple-choice questions from a job description or a list of skills, runs them as a timed quiz, and delivers a scored result with per-question explanations. It supports six AI providers and runs in two modes: a native desktop GUI or a shared web server that any browser on the same network can access.

## Docker (Recommended)

The quickest way to run iLab+ in web mode — no Python or virtualenv setup required.

**Prerequisites:** [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)

```bash
cd ilab

# Optional: set a custom secret key
cp .env.example .env   # then edit .env

docker compose up -d
```

| URL | Description |
|---|---|
| `http://localhost:8001` | iLab+ web UI |

**LAN access:** replace `localhost` with this machine's IP address — the server binds to `0.0.0.0` so no additional config is needed.

```bash
docker compose down        # stop and remove container
docker compose logs -f     # follow logs
```

> **API key:** configure your AI provider key in the web UI (⚙ Settings) after opening the app — it is stored in the browser, not on the server.
>
> **Single worker:** the container runs with one Gunicorn worker (`-w 1`). The in-memory session store is not safe for multiple worker processes. Do not override this.

---

## Quick Start

See the Installation section below for detailed platform-specific steps (Windows / macOS / Linux).

---

## Table of Contents

1. [Features](#features)
2. [Modes of Operation](#modes-of-operation)
3. [AI Providers](#ai-providers)
4. [Themes](#themes)
5. [Requirements](#requirements)
6. [Installation](#installation)
   - [Windows](#windows)
   - [macOS](#macos)
   - [Linux / Unix](#linux--unix)
7. [Configuration](#configuration)
   - [Environment Variables (Web Mode)](#environment-variables-web-mode)
   - [API Keys](#api-keys)
8. [Starting the Application](#starting-the-application)
   - [Windows — PowerShell Scripts](#windows--powershell-scripts)
   - [macOS / Linux — Shell Scripts](#macos--linux--shell-scripts)
   - [Starting Manually](#starting-manually)
9. [Stopping the Application](#stopping-the-application)
   - [Windows](#windows-1)
   - [macOS / Linux](#macos--linux-1)
   - [Stopping Manually](#stopping-manually)
10. [Accessing the Application](#accessing-the-application)
    - [Desktop Mode](#desktop-mode)
    - [Web Mode — Local Access](#web-mode--local-access)
    - [Web Mode — LAN Access (sharing with others)](#web-mode--lan-access-sharing-with-others)
11. [Using the Application](#using-the-application)
    - [Step 1 — Configure Your API Key](#step-1--configure-your-api-key)
    - [Step 2 — Generate Questions](#step-2--generate-questions)
    - [Step 3 — Take the Quiz](#step-3--take-the-quiz)
    - [Step 4 — Review Your Results](#step-4--review-your-results)
12. [Web Mode — Multi-User Notes](#web-mode--multi-user-notes)
13. [Production Deployment](#production-deployment)
14. [Troubleshooting](#troubleshooting)

---

## Features

### Question Generation
- Generates multiple-choice technical interview questions from either a **job description** or a **skills / tech-stack list**.
- Each question has exactly four answer options, one correct answer, a difficulty rating (Easy / Medium / Hard), a category label, and a detailed explanation of the correct answer.
- Questions are tailored to the selected **experience level**: Junior, Mid-level, Senior, Lead, or Architect — adjusting complexity from fundamentals through to architecture and strategy.
- The number of questions is configurable: 5 to 50 (web) or 5 to 100 (desktop) in steps of 5.
- All generation is performed in the background with live progress feedback so the UI is never blocked.

### Quiz Engine
- Questions are presented one at a time on a card-style interface.
- Clicking an option immediately reveals the answer: the correct option turns green, a wrong selection turns red and the correct answer is highlighted alongside it.
- The explanation for each question is displayed after answering.
- A **scrollable navigation rail** at the bottom shows a colour-coded dot for every question (answered, bookmarked, or pending) enabling non-linear navigation.
- A **bookmark toggle** on each question lets you flag questions for later review. A bookmark filter mode restricts the navigation rail to flagged questions only.
- Back and Next buttons allow free navigation at any point, including revisiting already-answered questions.

### Scoring and Results
- After finishing, a results page shows the overall score, accuracy percentage, number of correct / incorrect / skipped answers, and a grade label.

| Score | Grade |
|---|---|
| 90 %+ | Outstanding |
| 80–89 % | Excellent |
| 70–79 % | Good Job |
| 50–69 % | Keep Practising |
| < 50 % | Needs Improvement |

- A full per-question review section shows every question with all four options colour-coded (green = correct, red = your wrong selection) and the explanation for every item.

### Settings and Personalisation
- **11 themes** available in web mode (6 dark, 5 light); 2 themes (Dark / Light) in desktop mode.
- Default experience level, question count, and active theme are saved per-user in the settings page.
- API keys and model selection are stored in the browser's `localStorage` in web mode — they never leave the user's machine.

### Multi-User Web Mode
- Any number of users can connect to the same server simultaneously.
- Each user maintains their own independent quiz session.
- Each user provides their own API key in their browser settings — no key is ever stored on the server.
- Session data (jobs, quizzes, results) expires automatically after 2 hours of inactivity.

### Live Generation Progress (Web Mode)
- A loading screen shows real-time progress via **Server-Sent Events (SSE)**.
- A step checklist (Connect → Analyse → Generate → Finalise) updates as each stage completes.
- An elapsed timer and rotating contextual tips keep the user informed during generation.
- Automatic polling fallback activates if SSE is unavailable; a `<meta>` refresh acts as a final safety net.

---

## Modes of Operation

| | Desktop Mode | Web Mode |
|---|---|---|
| Interface | Native OS window (CustomTkinter) | Browser (any device on the network) |
| Who can use it | One user on the host machine | Multiple users simultaneously |
| API key storage | `config.json` on disk (host machine only) | Browser `localStorage` (each user's own device) |
| Theme options | Dark / Light | 11 themes |
| Start command | `start.ps1` or `start.sh` (default) | `start.ps1 -Mode web` or `start.sh --web` |
| Server required | No | Yes (Flask + Gunicorn on Unix; Flask built-in on Windows) |

---

## AI Providers

| Provider | Key Required | Default Model | Notes |
|---|---|---|---|
| **Claude** (Anthropic) | Yes | `claude-opus-4-7` | Best reasoning quality |
| **OpenAI** | Yes | `gpt-4o` | Industry standard |
| **Gemini** (Google) | Yes | `gemini-1.5-pro` | Good for large context JDs |
| **Groq** | Yes | `llama-3.3-70b-versatile` | Free tier available, fast inference |
| **Ollama** | No | `llama3.2` | Fully local, no internet required |
| **xAI** (Grok) | Yes | `grok-3-mini` | Grok model family |

A custom **Base URL** field is available for every provider to point to a self-hosted or proxy endpoint.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web server | Python 3.10+, Flask | HTTP routing, Jinja2 templates, SSE progress streaming |
| Production server | Gunicorn (Unix/macOS) | Single-worker WSGI production server |
| Desktop GUI | CustomTkinter | Native OS window for desktop mode |
| AI client -- Claude | anthropic | Anthropic Claude API integration |
| AI client -- OpenAI | openai | OpenAI GPT API integration |
| AI client -- Gemini | google-generativeai | Google Gemini API integration |
| AI client -- Groq | groq | Groq fast-inference API integration |
| AI client -- Ollama / xAI | httpx | Local Ollama and xAI Grok API integration |
| Frontend | Jinja2, vanilla JS/HTML/CSS | Server-side rendered quiz UI; no JS framework |
| Real-time progress | Server-Sent Events (SSE) | Live generation progress streaming to the browser |
| Session management | Flask sessions (UUID cookies) | Per-user in-memory job/quiz/result stores |
| Scripts | Bash (.sh), PowerShell (.ps1) | Cross-platform start / stop |

---

## Themes

### Web Mode (11 themes)

| Theme | Style | Background | Accent |
|---|---|---|---|
| Dark Pro | Dark | `#0d1117` | Indigo |
| Midnight | Dark | `#080b14` | Purple |
| Navy | Dark | `#0f172a` | Cyan |
| Forest | Dark | `#0b1714` | Emerald |
| Warm | Dark | `#120f07` | Amber |
| Light | Light | `#f6f8fa` | Indigo |
| Ocean | Light | `#f0f8ff` | Sky Blue |
| Rose | Light | `#fff5f5` | Rose |
| Sage | Light | `#f0faf4` | Green |
| Sunset | Light | `#fffbf0` | Orange |
| Lavender | Light | `#f8f5ff` | Violet |

### Desktop Mode (2 themes)
- **Dark** — deep navy background, blue accent
- **Light** — light grey background, deep blue accent

---

## Requirements

- **Python 3.10 or newer** (3.13 recommended)
- pip (bundled with Python)
- Internet access to reach your chosen AI provider's API (not required for Ollama)

### Desktop Mode Additional Requirements
- **Windows**: Python installed with Tcl/Tk (default installer includes it)
- **macOS**: Tkinter is included with the system Python (`xcode-select --install` if missing)
- **Linux**: `python3-tk` system package (see [Installation — Linux](#linux--unix))

---

## Installation

### Windows

1. **Install Python 3.10+**

   Download from [python.org](https://www.python.org/downloads/). During installation check **"Add Python to PATH"** and **"tcl/tk and IDLE"**.

2. **Clone or download the repository**

   ```powershell
   git clone <repo-url>
   cd ilab
   ```

   Or download and extract the ZIP, then open a PowerShell window in the `ilab` folder.

3. **Verify Python is on the PATH**

   ```powershell
   python --version
   ```

   Expected output: `Python 3.10.x` or newer.

4. **Allow script execution** (one-time, if not already set)

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

5. **Run the start script** — it creates the virtual environment and installs all dependencies automatically:

   ```powershell
   # Desktop mode (default)
   .\scripts\start.ps1

   # Web mode
   .\scripts\start.ps1 -Mode web
   ```

   On first run this downloads all Python packages, which may take 1–2 minutes.

---

### macOS

1. **Install Python 3.10+**

   ```bash
   # Using Homebrew (recommended)
   brew install python@3.13

   # Or download from python.org
   ```

2. **Clone or download the repository**

   ```bash
   git clone <repo-url>
   cd ilab
   ```

3. **Make the scripts executable** (one-time)

   ```bash
   chmod +x scripts/start.sh scripts/stop.sh
   ```

4. **Run the start script** — it creates the virtual environment and installs dependencies automatically:

   ```bash
   # Desktop mode (default)
   ./scripts/start.sh

   # Web mode
   ./scripts/start.sh --web
   ```

   On first run this downloads all Python packages, which may take 1–2 minutes.

> **Tkinter on macOS**: If you see `No module named tkinter` when starting desktop mode, install a Homebrew Python with Tkinter support:
> ```bash
> brew install python-tk@3.13
> ```

---

### Linux / Unix

1. **Install Python 3.10+ and Tkinter** (Tkinter is required only for desktop mode)

   **Ubuntu / Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv python3-tk
   ```

   **Fedora / RHEL / CentOS:**
   ```bash
   sudo dnf install python3 python3-pip python3-tkinter
   ```

   **Arch Linux:**
   ```bash
   sudo pacman -S python tk
   ```

2. **Clone or download the repository**

   ```bash
   git clone <repo-url>
   cd ilab
   ```

3. **Make the scripts executable** (one-time)

   ```bash
   chmod +x scripts/start.sh scripts/stop.sh
   ```

4. **Run the start script** — it creates the virtual environment and installs dependencies automatically:

   ```bash
   # Desktop mode (default)
   ./scripts/start.sh

   # Web mode
   ./scripts/start.sh --web
   ```

   On first run this downloads all Python packages, which may take 1–2 minutes.

> **Web mode only (no desktop required)**: If you are deploying on a headless server, skip `python3-tk` and always start with `--web`. The `requirements-web.txt` file does not include the GUI libraries.

### Reinstallation (Clean Reset)

The steps above are for a **first-time install**, where `start` creates the `.venv/` and installs dependencies automatically. Because the start script tracks installed dependencies with a marker file, there are two levels of reinstall:

**A. Refresh dependencies only** (e.g. after editing `requirements.txt` / `requirements-web.txt`). The start script reinstalls automatically when the requirements file is newer than the marker, but you can force it by deleting the marker:

```bash
# macOS / Linux
rm -f .venv/.desktop_deps_installed .venv/.web_deps_installed

# Windows (PowerShell)
Remove-Item .venv\.desktop_deps_installed, .venv\.web_deps_installed -ErrorAction SilentlyContinue
```

Then re-run `./scripts/start.sh` (or `.\scripts\start.ps1`) and dependencies reinstall on next launch.

**B. Full clean reset** (corrupted virtualenv, Python version change, or a pristine slate):

1. Stop the app:

   ```bash
   ./scripts/stop.sh          # Windows: .\scripts\stop.ps1
   ```

2. Delete the environment and runtime artifacts:

   ```bash
   # macOS / Linux
   rm -rf .venv .pids data/logs
   find . -type d -name __pycache__ -prune -exec rm -rf {} +
   ```

   ```powershell
   # Windows (PowerShell)
   Remove-Item -Recurse -Force .venv, .pids, data\logs -ErrorAction SilentlyContinue
   Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
   ```

   Delete `config.json` too for a pristine reset — it is recreated from `config.example.json`.

3. Re-run the start script; it rebuilds `.venv/` and reinstalls everything:

   ```bash
   ./scripts/start.sh              # or: .\scripts\start.ps1 -Mode web
   ```

---

## Configuration

### Environment Variables (Web Mode)

Copy `.env.example` to `.env` and edit it before starting the web server:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `ILAB_SECRET` | *(auto-generated)* | Secret key used to sign Flask sessions. Set a fixed value so sessions survive restarts. Generate one with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `HOST` | `0.0.0.0` | IP address to bind to. `0.0.0.0` = all interfaces (accessible from the LAN). Use `127.0.0.1` to restrict to localhost only. |
| `PORT` | `8001` | TCP port the web server listens on. |
| `FLASK_DEBUG` | `0` | Set to `1` to enable Flask debug mode. Never use `1` in production. |

If `.env` is not present, the server starts with safe defaults (random secret, all interfaces, port 8001).

### API Keys

**Web Mode**: API keys are configured per user in the browser. Each user navigates to **Settings**, selects their preferred provider, and enters their API key. The key is saved to the browser's `localStorage` and is never sent to the server except as a form field when generating questions — it is never stored in any server-side file or database.

**Desktop Mode**: API keys are stored in `config.json` in the project directory. This file is only accessible to the user running the application on that machine.

---

## Starting the Application

### Windows — PowerShell Scripts

> Run these from a PowerShell window opened in the project's root directory.

**Desktop mode (default)**
```powershell
.\scripts\start.ps1
```

**Web mode**
```powershell
.\scripts\start.ps1 -Mode web
```

**Web mode on a custom port**
```powershell
.\scripts\start.ps1 -Mode web -Port 9000
```

The script will:
1. Check that Python is installed.
2. Create a `.venv` virtual environment if it does not exist.
3. Install dependencies from `requirements.txt` (desktop) or `requirements-web.txt` (web) if they have changed.
4. Start the application in the background.
5. Print the local and network URLs (web mode).

---

### macOS / Linux — Shell Scripts

**Desktop mode (default)**
```bash
./scripts/start.sh
```

**Web mode**
```bash
./scripts/start.sh --web
```

**Web mode on a custom port**
```bash
./scripts/start.sh --web --port 9000
```

The script follows the same steps as the PowerShell equivalent. In web mode it prefers **Gunicorn** if installed (included in `requirements-web.txt`) and falls back to the Flask built-in server.

---

### Starting Manually

If you prefer not to use the scripts, activate the virtual environment and run the entry point directly.

**Desktop mode**
```bash
# macOS / Linux
source .venv/bin/activate
python main.py
```
```powershell
# Windows
.venv\Scripts\Activate.ps1
python main.py
```

**Web mode — Flask built-in server (development)**
```bash
# macOS / Linux
source .venv/bin/activate
HOST=0.0.0.0 PORT=8001 python flask_app.py
```
```powershell
# Windows
.venv\Scripts\Activate.ps1
$env:HOST="0.0.0.0"; $env:PORT="8001"; python flask_app.py
```

**Web mode — Gunicorn (macOS / Linux production)**
```bash
source .venv/bin/activate
gunicorn --workers 1 --bind 0.0.0.0:8001 --timeout 120 wsgi:application
```

> **Important:** Always use `--workers 1` with Gunicorn. The job, quiz, and result stores are held in memory within the single worker process. Multiple workers would route different requests to different stores and silently lose data.

---

## Stopping the Application

### Windows

**Stop everything (desktop + web)**
```powershell
.\scripts\stop.ps1
```

**Stop web server only**
```powershell
.\scripts\stop.ps1 -Mode web
```

**Stop desktop app only**
```powershell
.\scripts\stop.ps1 -Mode desktop
```

---

### macOS / Linux

**Stop everything (desktop + web)**
```bash
./scripts/stop.sh
```

**Stop web server only**
```bash
./scripts/stop.sh --web
```

**Stop desktop app only**
```bash
./scripts/stop.sh --desktop
```

---

### Stopping Manually

If the scripts are not available or the PID files are missing, find and kill the process by port:

**macOS / Linux**
```bash
kill $(lsof -t -i:8001)
```

**Windows (PowerShell)**
```powershell
 $pid = (Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -First 1
if ($pid) { Stop-Process -Id $pid -Force }
```

**Windows (Command Prompt)**
```cmd
netstat -ano | findstr :8001
taskkill /PID <pid> /F
```

---

## Accessing the Application

### Desktop Mode

The application window opens automatically when you run the start script. No browser is needed.

---

### Web Mode — Local Access

Once the server is running, open a browser on the same machine and go to:

```
http://localhost:8001
```

or

```
http://127.0.0.1:8001
```

If you specified a custom port, replace `8001` with your port number.

---

### Web Mode — LAN Access (sharing with others)

When the server binds to `0.0.0.0` (the default), anyone on the same local network can access it by using your machine's LAN IP address.

The start script prints the network URL automatically when it starts:

```
   Local URL   -> http://127.0.0.1:8001
   Network URL -> http://10.220.29.125:8001  (share this with others on your LAN)
```

Share the **Network URL** with other users. They open it in any browser — no installation required on their machine.

**Finding your LAN IP manually**

*Windows (PowerShell):*
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(127\.|169\.)' } | Select-Object IPAddress
```

*macOS:*
```bash
ipconfig getifaddr en0
```

*Linux:*
```bash
ip route get 1.1.1.1 | awk '/src/{print $7}'
```

**Windows Firewall**

If other machines cannot connect, Windows Firewall may be blocking port 8001. Allow it with:

```powershell
New-NetFirewallRule -DisplayName "iLab+ Web" -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow
```

To remove this rule later:
```powershell
Remove-NetFirewallRule -DisplayName "iLab+ Web"
```

---

## Using the Application

### Step 1 — Configure Your API Key

1. Click **Settings** (gear icon) in the top-right navigation bar.
2. Under **Active AI Provider**, select the provider you want to use (Claude, OpenAI, Gemini, Groq, Ollama, xAI).
3. In the **Provider Configuration** section, click the tab for your selected provider and enter your API key in the **API Key** field.
4. Optionally change the **Model** and **Base URL** for that provider.
5. Click **Save Settings**. Your API key is saved in your browser only — it is never sent to the server in settings.

> **Ollama users**: No API key is required. Set the Base URL to `http://localhost:11434/v1` (or the host running Ollama) and select a model.

---

### Step 2 — Generate Questions

1. On the home screen, choose the input method using the tab switcher:
   - **Job Description** — paste a full job posting or role description.
   - **Skills / Tech Stack** — list technologies, frameworks, or topics (one per line or comma-separated).
2. Set the **Experience Level** slider to match the candidate level (Junior → Architect).
3. Set the **Number of Questions** slider.
4. Click **Start Interview**.
5. A loading screen appears showing real-time progress as the AI generates questions.

---

### Step 3 — Take the Quiz

- Read the question and click one of the four options.
- The correct answer and a wrong selection are highlighted immediately after you click.
- The explanation for the correct answer appears below the options.
- Use the **Back** and **Next** buttons or click any dot in the navigation rail to jump to any question.
- Click the **bookmark icon** (star) to flag a question. Toggle the bookmark filter to review only bookmarked questions.
- When you are ready to see your score, click **Finish**.

---

### Step 4 — Review Your Results

- Your score, accuracy, and grade are displayed on the results page.
- Scroll down to review every question: all four options are shown with colour coding and the explanation for each answer is visible regardless of whether you answered correctly.
- Click **New Interview** to start again or **Home** to return to the start screen.

---

## Web Mode — Multi-User Notes

- Multiple users can run independent quizzes simultaneously on the same server.
- Each user's session (job, quiz, results) is identified by a UUID stored in their browser session cookie.
- Sessions are held in memory and expire after **2 hours of inactivity**. Restarting the server clears all in-progress sessions.
- If you need sessions to survive server restarts, set a fixed `ILAB_SECRET` in `.env`. Without this, a random secret is generated each restart and existing browser cookies become invalid.
- API keys are not shared between users. Each user enters their own key in their own browser.

---

## Production Deployment

For a production deployment accessible beyond a local network (internet-facing), the following additional steps are recommended:

**Use Gunicorn (Linux / macOS only)**

Gunicorn is included in `requirements-web.txt` and is used automatically by `start.sh --web` on Unix. Always run with a single worker:

```bash
gunicorn --workers 1 --bind 0.0.0.0:8001 --timeout 120 wsgi:application
```

**Reverse proxy with Nginx or Caddy**

Place a reverse proxy in front of Flask/Gunicorn to handle TLS, compression, and static files:

```nginx
server {
    listen 443 ssl;
    server_name ilab.yourdomain.com;

    location / {
      proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;          # required for SSE streaming
        proxy_read_timeout 180s;      # match Gunicorn timeout
    }
}
```

**Set a fixed secret key**

```bash
# In .env
ILAB_SECRET=<output of: python -c "import secrets; print(secrets.token_hex(32))">
```

**Bind to localhost only** (let the proxy handle external traffic)

```bash
# In .env
HOST=127.0.0.1
```

**Windows production note**: Gunicorn does not support Windows. For Windows production deployments use **WSL2 + Gunicorn**, containerise with **Docker on Windows**, or deploy to a Linux server.

---

## Troubleshooting

### "python3 not found" (macOS / Linux) or "Python not found" (Windows)

Ensure Python is installed and on your PATH.

- **Windows**: Re-run the Python installer and check "Add Python to PATH".
- **macOS**: `brew install python@3.13` or add `/opt/homebrew/bin` to your PATH.
- **Linux**: `sudo apt-get install python3` (Debian/Ubuntu) or `sudo dnf install python3` (Fedora).

---

### "No module named tkinter" (Linux desktop mode)

```bash
# Ubuntu / Debian
sudo apt-get install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

### Web server exits immediately

Run the server manually to see the full error output:

```bash
# macOS / Linux
.venv/bin/python flask_app.py

# Windows
.venv\Scripts\python.exe flask_app.py
```

Common causes:
-- Port 8001 is already in use — change `PORT` in `.env` or stop the existing process.
- A required package is missing — delete `.venv` and run the start script again.

---

### Can't connect from another machine on the LAN

1. Confirm the server is bound to `0.0.0.0` — the start script output should say `Running on http://0.0.0.0:8001`.
2. Check that no firewall is blocking port 8001 (see [Windows Firewall](#web-mode--lan-access-sharing-with-others)).
3. Ensure you are using the **LAN IP address** of the host machine, not `localhost` or `127.0.0.1`.

---

### API key not working

- Verify the key is saved in Settings by reopening the Settings page — the field should be pre-filled.
- Check that the correct **provider tab** is selected (e.g. your Claude key will not work if OpenAI is the active provider).
- For Groq and xAI, confirm the **Base URL** field is set correctly.
- For Ollama, ensure the Ollama server is running on the machine specified in the Base URL.

---

### "iLab+ is already running" warning

A stale PID file was left over from a previous run. Delete it and retry:

```bash
rm .pids/web.pid     # web mode
rm .pids/app.pid     # desktop mode
```

```powershell
Remove-Item .pids\web.pid    # web mode
Remove-Item .pids\app.pid    # desktop mode
```

---

### Dependencies not reinstalling after requirements file change

Delete the marker file to force a reinstall:

```bash
rm .venv/.web_deps_installed      # web mode
rm .venv/.desktop_deps_installed  # desktop mode
```

```powershell
Remove-Item .venv\.web_deps_installed
Remove-Item .venv\.desktop_deps_installed
```

Then run the start script again.
